"""Tests for FedNet Solana attestation module."""

import pytest
import json
from fednet.solana_attestation import create_solana_client, MockSolanaAttestationClient


class TestMockSolanaAttestationClient:
    """Test mock Solana attestation client."""

    @pytest.fixture
    def client(self):
        """Create a mock Solana client."""
        return create_solana_client(use_mock=True)

    def test_attest_artifact(self, client):
        """Test artifact attestation."""
        result = client.attest_artifact(
            artifact_hash="0x7f3a9b2c1d4e5f6a",
            round_id=1,
            participants=3,
            model_version="v1.0.0",
        )

        assert result is not None
        assert result["tx_id"].startswith("mock_tx_")
        assert result["round_id"] == 1
        assert result["artifact_hash"] == "0x7f3a9b2c1d4e5f6a"
        assert result["status"] == "confirmed"

    def test_explorer_url(self, client):
        """Test explorer URL generation."""
        result = client.attest_artifact(
            artifact_hash="abc123",
            round_id=1,
            participants=2,
            model_version="v1.0.0",
        )

        url = result["explorer_url"]
        assert "explorer.solana.com" in url
        assert "devnet" in url
        assert result["tx_id"] in url

    def test_verify_attestation(self, client):
        """Test attestation verification."""
        # Create attestation
        result = client.attest_artifact(
            artifact_hash="abc123",
            round_id=1,
            participants=2,
            model_version="v1.0.0",
        )

        tx_id = result["tx_id"]

        # Verify it
        verification = client.verify_attestation(tx_id)

        assert verification is not None
        assert verification["tx_id"] == tx_id
        assert verification["status"] == "verified"

    def test_verify_nonexistent_tx(self, client):
        """Test verifying non-existent transaction."""
        result = client.verify_attestation("nonexistent_tx")
        assert result is None

    def test_payer_address(self, client):
        """Test getting payer address."""
        address = client.get_payer_address()
        assert address is not None
        assert len(address) > 0

    def test_memo_format(self, client):
        """Test that memo contains properly formatted JSON."""
        result = client.attest_artifact(
            artifact_hash="0x123abc",
            round_id=5,
            participants=4,
            model_version="v2.1.0",
        )

        memo_text = result["memo"]
        memo_data = json.loads(memo_text)

        assert memo_data["type"] == "fednet_artifact_attestation"
        assert memo_data["artifact_hash"] == "0x123abc"
        assert memo_data["round_id"] == 5
        assert memo_data["num_participants"] == 4
        assert memo_data["model_version"] == "v2.1.0"

    def test_multiple_attestations(self, client):
        """Test multiple attestations."""
        tx_ids = []

        for round_id in range(1, 4):
            result = client.attest_artifact(
                artifact_hash=f"hash_{round_id}",
                round_id=round_id,
                participants=2,
                model_version="v1.0.0",
            )
            tx_ids.append(result["tx_id"])

        # Verify all
        for tx_id in tx_ids:
            verification = client.verify_attestation(tx_id)
            assert verification is not None
            assert verification["status"] == "verified"

    def test_factory_creates_mock(self):
        """Test factory creates mock client when requested."""
        client = create_solana_client(use_mock=True)
        assert isinstance(client, MockSolanaAttestationClient)

    def test_factory_creates_real_client(self):
        """Test factory creates real client when requested."""
        from fednet.solana_attestation import SolanaAttestationClient

        try:
            client = create_solana_client(use_mock=False)
            assert isinstance(client, SolanaAttestationClient)
        except ImportError:
            # OK if Solana SDK not installed in test environment
            pytest.skip("Solana SDK not available")
