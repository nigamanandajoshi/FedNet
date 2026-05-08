"""Tests for x402-gated inference server."""

import pytest
import json
import torch
import torch.nn as nn
from decimal import Decimal
from fednet.inference_server import X402InferenceServer


class SimpleTestModel(nn.Module):
    """Simple model for testing."""

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 5)
        self.fc2 = nn.Linear(5, 2)

    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))


class TestX402InferenceServer:
    """Test x402-gated inference server."""

    @pytest.fixture
    def model(self):
        """Create test model."""
        return SimpleTestModel()

    @pytest.fixture
    def server(self, model):
        """Create test server."""
        return X402InferenceServer(
            model=model,
            model_id="test_model_v1",
            price_per_inference=Decimal("0.05"),
            debug=False,
        )

    @pytest.fixture
    def client(self, server):
        """Create Flask test client."""
        return server.app.test_client()

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["model_id"] == "test_model_v1"

    def test_model_info(self, client):
        """Test model info endpoint."""
        response = client.get("/model/info")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["model_id"] == "test_model_v1"
        assert data["price_per_inference_usdc"] == "0.05"
        assert data["payment_required"] is True

    def test_inference_without_payment(self, client):
        """Test inference request without payment returns 402."""
        response = client.post(
            "/inference",
            json={"input": [0.1] * 10},
        )

        assert response.status_code == 402
        data = json.loads(response.data)
        assert "payment required" in data["error"].lower()

    def test_inference_with_valid_payment(self, client, server):
        """Test inference with valid payment."""
        response = client.post(
            "/inference",
            json={
                "input": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                "payment_tx_id": "mock_tx_123",
                "payer_wallet": "0xuser123",
                "payment_amount": "0.05",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert "result" in data
        assert data["payment_verified"] is True
        assert data["model_id"] == "test_model_v1"

    def test_inference_with_insufficient_payment(self, client):
        """Test inference with insufficient payment."""
        response = client.post(
            "/inference",
            json={
                "input": [0.1] * 10,
                "payment_tx_id": "mock_tx_456",
                "payer_wallet": "0xuser456",
                "payment_amount": "0.01",  # Less than required
            },
        )

        assert response.status_code == 402

    def test_inference_updates_stats(self, client, server):
        """Test that inference updates server statistics."""
        assert server.inference_count == 0

        client.post(
            "/inference",
            json={
                "input": [0.1] * 10,
                "payment_tx_id": "tx_1",
                "payer_wallet": "0xuser1",
                "payment_amount": "0.05",
            },
        )

        assert server.inference_count == 1
        assert server.total_revenue == Decimal("0.05")

    def test_multiple_inferences(self, client, server):
        """Test multiple inference requests."""
        for i in range(3):
            client.post(
                "/inference",
                json={
                    "input": [0.1] * 10,
                    "payment_tx_id": f"tx_{i}",
                    "payer_wallet": f"0xuser{i}",
                    "payment_amount": "0.05",
                },
            )

        assert server.inference_count == 3
        assert server.total_revenue == Decimal("0.15")

    def test_payment_history_endpoint(self, client):
        """Test payment history endpoint."""
        # Make some inferences with payment
        for i in range(2):
            client.post(
                "/inference",
                json={
                    "input": [0.1] * 10,
                    "payment_tx_id": f"tx_{i}",
                    "payer_wallet": f"0xuser{i}",
                    "payment_amount": "0.05",
                },
            )

        response = client.get("/payments/history")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["total_payments"] == 2
        assert data["total_revenue"] == "0.10"

    def test_stats_endpoint(self, client):
        """Test statistics endpoint."""
        # Make an inference
        client.post(
            "/inference",
            json={
                "input": [0.1] * 10,
                "payment_tx_id": "tx_1",
                "payer_wallet": "0xuser1",
                "payment_amount": "0.05",
            },
        )

        response = client.get("/stats")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["total_inferences"] == 1
        assert data["total_revenue_usdc"] == "0.05"
        assert data["total_payments"] == 1

    def test_inference_with_list_input(self, client):
        """Test inference with list input."""
        response = client.post(
            "/inference",
            json={
                "input": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                "payment_tx_id": "tx_123",
                "payer_wallet": "0xuser",
                "payment_amount": "0.05",
            },
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data["result"], list)

    def test_inference_missing_input(self, client):
        """Test inference request missing input field."""
        response = client.post(
            "/inference",
            json={
                "payment_tx_id": "tx_123",
                "payer_wallet": "0xuser",
                "payment_amount": "0.05",
            },
        )

        assert response.status_code == 400

    def test_custom_price_per_inference(self, model):
        """Test server with custom pricing."""
        server = X402InferenceServer(
            model=model,
            model_id="expensive_model",
            price_per_inference=Decimal("1.00"),
        )

        assert server.payment_processor.price_per_inference == Decimal("1.00")

    def test_inference_id_sequential(self, client, server):
        """Test that inference IDs are sequential."""
        inference_ids = []

        for i in range(3):
            response = client.post(
                "/inference",
                json={
                    "input": [0.1] * 10,
                    "payment_tx_id": f"tx_{i}",
                    "payer_wallet": f"0xuser{i}",
                    "payment_amount": "0.05",
                },
            )

            data = json.loads(response.data)
            inference_ids.append(data["inference_id"])

        assert inference_ids == ["000001", "000002", "000003"]
