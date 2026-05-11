"""Integration tests for FedNet end-to-end flows."""

import pytest
import json
import torch
import torch.nn as nn
from decimal import Decimal
from pathlib import Path
import tempfile

from fednet.audit_artifacts import create_artifact_generator
from fednet.solana_attestation import create_solana_client
from fednet.inference_server import X402InferenceServer


class SimpleModel(nn.Module):
    """Simple model for integration testing."""

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8, 16)
        self.fc2 = nn.Linear(16, 3)

    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))


class TestEndToEndPipeline:
    """Test the complete FedNet pipeline: audit → attestation → verification."""

    def test_artifact_generation_and_attestation(self):
        """Test Layer 1 → Layer 2 flow: generate artifact, attest on chain, verify."""
        # Layer 1: Generate audit artifact
        artifact_gen = create_artifact_generator("test-integration-key")

        participants = ["wallet_a", "wallet_b", "wallet_c"]
        gradients = {"layer1.weight": [0.1, 0.2, 0.3], "layer1.bias": [0.01]}

        artifact = artifact_gen.generate_artifact(
            round_id=1,
            participants=participants,
            gradients=gradients,
            model_version="v1.0.0",
            epsilon=0.1,
            delta=1e-5,
        )

        # Verify artifact is valid
        assert artifact_gen.verify_artifact(artifact) is True
        assert artifact.differential_privacy_applied is True
        assert artifact.raw_data_moved is False
        assert len(artifact.participants) == 3
        assert artifact.aggregator_signature != ""

        # Layer 2: Attest on Solana (mock)
        solana_client = create_solana_client(use_mock=True)

        attestation = solana_client.attest_artifact(
            artifact_hash=artifact.gradient_hash,
            round_id=artifact.round_id,
            participants=len(artifact.participants),
            model_version=artifact.model_version,
        )

        assert attestation is not None
        assert attestation["status"] == "confirmed"
        assert attestation["artifact_hash"] == artifact.gradient_hash

        # Verify attestation
        verification = solana_client.verify_attestation(attestation["tx_id"])
        assert verification is not None
        assert verification["status"] == "verified"

    def test_artifact_persistence_round_trip(self):
        """Test artifact save → load → verify round trip."""
        artifact_gen = create_artifact_generator("persistence-test-key")

        artifact = artifact_gen.generate_artifact(
            round_id=42,
            participants=["node1", "node2"],
            gradients={"fc.weight": [1.0, 2.0, 3.0]},
            model_version="v2.0.0",
            epsilon=0.5,
            delta=1e-6,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = str(Path(tmpdir) / "test_artifact.json")

            # Save
            artifact_gen.save_artifact(artifact, filepath)

            # Load
            loaded = artifact_gen.load_artifact(filepath)

            # Verify integrity
            assert loaded.round_id == 42
            assert loaded.model_version == "v2.0.0"
            assert loaded.epsilon == 0.5
            assert artifact_gen.verify_artifact(loaded) is True

    def test_multi_round_attestation(self):
        """Test multiple FL rounds with attestation."""
        artifact_gen = create_artifact_generator("multi-round-key")
        solana_client = create_solana_client(use_mock=True)

        tx_ids = []
        for round_id in range(1, 4):
            artifact = artifact_gen.generate_artifact(
                round_id=round_id,
                participants=[f"node_{i}" for i in range(3)],
                gradients={f"layer{round_id}": [float(round_id)]},
                model_version="v1.0.0",
                epsilon=0.1,
            )

            attestation = solana_client.attest_artifact(
                artifact_hash=artifact.gradient_hash,
                round_id=round_id,
                participants=3,
                model_version="v1.0.0",
            )

            tx_ids.append(attestation["tx_id"])

        # Verify all attestations
        for tx_id in tx_ids:
            assert solana_client.verify_attestation(tx_id)["status"] == "verified"


class TestInferenceIntegration:
    """Test inference server with payment flow."""

    @pytest.fixture
    def server(self):
        """Create test server."""
        model = SimpleModel()
        return X402InferenceServer(
            model=model,
            model_id="integration_test_v1",
            price_per_inference=Decimal("0.05"),
            use_mock=True,
        )

    @pytest.fixture
    def client(self, server):
        """Create Flask test client."""
        return server.app.test_client()

    def test_full_payment_and_inference_flow(self, client, server):
        """Test: check info → attempt without payment → pay → infer."""
        # Step 1: Check model info
        resp = client.get("/model/info")
        assert resp.status_code == 200
        info = json.loads(resp.data)
        assert info["payment_required"] is True
        assert info["price_per_inference_usdc"] == "0.05"

        # Step 2: Attempt inference without payment
        resp = client.post("/inference", json={"input": [1.0] * 8})
        assert resp.status_code == 402

        # Step 3: Inference with valid payment
        resp = client.post("/inference", json={
            "input": [11.5, 4.5, 80, 28, 33, 15, 7.0, 250],
            "payment_tx_id": "integration_tx_001",
            "payer_wallet": "0xresearcher",
            "payment_amount": "0.05",
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["payment_verified"] is True
        assert "result" in data
        assert isinstance(data["result"], list)
        assert len(data["result"]) == 3  # 3 classes

        # Step 4: Verify stats updated
        resp = client.get("/stats")
        stats = json.loads(resp.data)
        assert stats["total_inferences"] == 1
        assert stats["total_revenue_usdc"] == "0.05"

    def test_multiple_sequential_inferences(self, client, server):
        """Test multiple inferences accumulate correctly."""
        for i in range(5):
            resp = client.post("/inference", json={
                "input": [float(i + 1)] * 8,
                "payment_tx_id": f"batch_tx_{i}",
                "payer_wallet": f"0xuser_{i}",
                "payment_amount": "0.05",
            })
            assert resp.status_code == 200

        assert server.inference_count == 5
        assert server.total_revenue == Decimal("0.25")

        # Verify payment history
        resp = client.get("/payments/history")
        history = json.loads(resp.data)
        assert history["total_payments"] == 5

    def test_health_check(self, client):
        """Test health endpoint."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "healthy"
