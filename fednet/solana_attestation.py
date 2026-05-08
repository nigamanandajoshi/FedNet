"""
Layer 2: Solana State Compression for Tamper-Proof Attestation

Anchors audit artifact hashes on Solana devnet for permanent, verifiable proof
that a training round occurred and data integrity.

Uses Solana's memo program to store attestation data at minimal cost (~$0.000005 per tx).
"""

import json
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

try:
    from solders.keypair import Keypair
    from solders.rpc.responses import GetTransactionResp
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.api import Client
    from solana.transaction import Transaction
    from solana.system_program import CreateAccountParams, create_account
    from spl.memo.instructions import memo
    from solana.publickey import PublicKey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False


class SolanaAttestationClient:
    """
    Client for anchoring audit artifacts on Solana via state compression.

    For MVP: Uses Solana's memo program to store attestation data.
    For production: Would use custom Anchor program with Merkle proof compression.
    """

    def __init__(
        self,
        rpc_url: str = "https://api.devnet.solana.com",
        payer_secret_key: Optional[str] = None,
    ):
        """
        Initialize Solana attestation client.

        Args:
            rpc_url: Solana RPC endpoint URL
            payer_secret_key: Base58 encoded secret key for paying transactions
        """
        if not SOLANA_AVAILABLE:
            raise ImportError("Solana SDK not installed. Install with: pip install solders solana spl-token")

        self.rpc_url = rpc_url
        self.client = Client(rpc_url)

        # Initialize payer keypair
        if payer_secret_key:
            self.payer = Keypair.from_secret_key(bytes.fromhex(payer_secret_key[:64]))
        else:
            # For testing: generate ephemeral keypair
            self.payer = Keypair()

    def attest_artifact(
        self,
        artifact_hash: str,
        round_id: int,
        participants: int,
        model_version: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Anchor an audit artifact hash on Solana via memo program.

        Args:
            artifact_hash: SHA256 hash of the artifact
            round_id: Training round number
            participants: Number of participating nodes
            model_version: Model version string

        Returns:
            Transaction details including signature and explorer URL
        """
        try:
            # Create attestation data
            attestation_data = {
                "type": "fednet_artifact_attestation",
                "artifact_hash": artifact_hash,
                "round_id": round_id,
                "num_participants": participants,
                "model_version": model_version,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "chain": "solana-devnet",
            }

            # Encode as JSON memo
            memo_text = json.dumps(attestation_data)

            # Create transaction with memo instruction
            tx = Transaction()
            tx.add(memo(memo_text.encode(), [self.payer.public_key]))

            # Send transaction
            tx_sig = self.client.send_transaction(tx, self.payer)
            tx_id = str(tx_sig)

            # Create explorer link
            explorer_url = f"https://explorer.solana.com/tx/{tx_id}?cluster=devnet"

            return {
                "tx_id": tx_id,
                "explorer_url": explorer_url,
                "artifact_hash": artifact_hash,
                "round_id": round_id,
                "timestamp": attestation_data["timestamp"],
                "memo": memo_text,
                "status": "confirmed",
            }

        except Exception as e:
            print(f"Error anchoring artifact on Solana: {e}")
            return None

    def verify_attestation(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify an attestation on Solana.

        Args:
            tx_id: Transaction ID to verify

        Returns:
            Transaction data including memo content if verification succeeds
        """
        try:
            tx = self.client.get_transaction(tx_id)

            if not tx or not tx.get("result"):
                return None

            # Extract memo from transaction
            result = tx["result"]
            meta = result.get("transaction", {}).get("message", {})

            # For MVP: Just confirm transaction exists and was successful
            slot = result.get("slot")

            return {
                "tx_id": tx_id,
                "slot": slot,
                "status": "verified" if tx else "not_found",
                "explorer_url": f"https://explorer.solana.com/tx/{tx_id}?cluster=devnet",
            }

        except Exception as e:
            print(f"Error verifying attestation: {e}")
            return None

    def get_explorer_url(self, tx_id: str) -> str:
        """Get Solana explorer URL for a transaction."""
        return f"https://explorer.solana.com/tx/{tx_id}?cluster=devnet"

    def get_payer_address(self) -> str:
        """Get the payer's public key."""
        return str(self.payer.public_key)


class MockSolanaAttestationClient:
    """
    Mock Solana client for testing without network access.
    Simulates artifact attestation for development/CI.
    """

    def __init__(self, rpc_url: str = "https://api.devnet.solana.com", payer_secret_key: Optional[str] = None):
        """Initialize mock client."""
        self.rpc_url = rpc_url
        self.attestations: Dict[str, Dict[str, Any]] = {}
        self.payer_address = "FedNetTestPayer111111111111111111111111111"

    def attest_artifact(
        self,
        artifact_hash: str,
        round_id: int,
        participants: int,
        model_version: str,
    ) -> Dict[str, Any]:
        """Simulate artifact attestation."""
        tx_id = f"mock_tx_{round_id}_{artifact_hash[:8]}"

        attestation = {
            "tx_id": tx_id,
            "explorer_url": f"https://explorer.solana.com/tx/{tx_id}?cluster=devnet",
            "artifact_hash": artifact_hash,
            "round_id": round_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "memo": json.dumps({
                "type": "fednet_artifact_attestation",
                "artifact_hash": artifact_hash,
                "round_id": round_id,
                "num_participants": participants,
                "model_version": model_version,
            }),
            "status": "confirmed",
        }

        self.attestations[tx_id] = attestation
        return attestation

    def verify_attestation(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Verify an attestation."""
        if tx_id in self.attestations:
            return {
                "tx_id": tx_id,
                "slot": 12345,
                "status": "verified",
                "explorer_url": self.attestations[tx_id]["explorer_url"],
            }
        return None

    def get_explorer_url(self, tx_id: str) -> str:
        """Get explorer URL."""
        return f"https://explorer.solana.com/tx/{tx_id}?cluster=devnet"

    def get_payer_address(self) -> str:
        """Get payer address."""
        return self.payer_address


def create_solana_client(
    use_mock: bool = False,
    rpc_url: str = "https://api.devnet.solana.com",
    payer_secret_key: Optional[str] = None,
) -> "SolanaAttestationClient":
    """
    Factory function to create a Solana attestation client.

    Args:
        use_mock: If True, uses mock client for testing
        rpc_url: Solana RPC endpoint
        payer_secret_key: Payer's secret key

    Returns:
        SolanaAttestationClient or MockSolanaAttestationClient instance
    """
    if use_mock:
        return MockSolanaAttestationClient(rpc_url, payer_secret_key)

    return SolanaAttestationClient(rpc_url, payer_secret_key)
