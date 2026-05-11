"""
Layer 2: Solana State Compression for Tamper-Proof Attestation

Anchors audit artifact hashes on Solana for permanent, verifiable proof
that a training round occurred and data integrity.

Uses Solana's memo program to store attestation data at minimal cost (~$0.000005 per tx).

Network is configurable via SOLANA_NETWORK env var:
  - devnet (default): free, for development and testing
  - mainnet-beta: production, requires SOL for tx fees (~$0.000005 per tx)
"""

import os
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("fednet.solana_attestation")

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


# ── Network helpers ───────────────────────────────────────────────────────────

RPC_URLS = {
    "devnet": "https://api.devnet.solana.com",
    "mainnet-beta": "https://api.mainnet-beta.solana.com",
    "testnet": "https://api.testnet.solana.com",
}


def _get_rpc_url(network: str, rpc_url: Optional[str] = None) -> str:
    """Resolve Solana RPC URL from network name or explicit URL."""
    if rpc_url:
        return rpc_url
    return RPC_URLS.get(network, RPC_URLS["devnet"])


def _get_explorer_url(tx_id: str, network: str) -> str:
    """Build Solana explorer URL with correct cluster param."""
    base = f"https://explorer.solana.com/tx/{tx_id}"
    if network == "mainnet-beta":
        return base  # mainnet doesn't use ?cluster=
    return f"{base}?cluster={network}"


# ── Production client ─────────────────────────────────────────────────────────

class SolanaAttestationClient:
    """
    Client for anchoring audit artifacts on Solana via state compression.

    For MVP: Uses Solana's memo program to store attestation data.
    For production: Would use custom Anchor program with Merkle proof compression.
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        payer_secret_key: Optional[str] = None,
        network: str = "devnet",
    ):
        """
        Initialize Solana attestation client.

        Args:
            rpc_url: Solana RPC endpoint URL (auto-derived from network if not set)
            payer_secret_key: Hex-encoded secret key for paying transactions
            network: Solana network (devnet, mainnet-beta, testnet)
        """
        if not SOLANA_AVAILABLE:
            raise ImportError("Solana SDK not installed. Install with: pip install solders solana spl-token")

        self.network = network
        self.rpc_url = _get_rpc_url(network, rpc_url)
        self.client = Client(self.rpc_url)

        # Initialize payer keypair
        if payer_secret_key:
            self.payer = Keypair.from_secret_key(bytes.fromhex(payer_secret_key[:64]))
        else:
            # For testing: generate ephemeral keypair
            self.payer = Keypair()

        logger.info(
            "Solana attestation client initialized: network=%s rpc=%s payer=%s",
            network, self.rpc_url, str(self.payer.public_key)[:16] + "...",
        )

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
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                "chain": f"solana-{self.network}",
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
            explorer_url = _get_explorer_url(tx_id, self.network)

            logger.info(
                "Artifact attested on Solana: round=%d tx=%s network=%s",
                round_id, tx_id[:16] + "...", self.network,
            )

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
            logger.error("Error anchoring artifact on Solana: %s", e, exc_info=True)
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
                "explorer_url": _get_explorer_url(tx_id, self.network),
            }

        except Exception as e:
            logger.error("Error verifying attestation: %s", e, exc_info=True)
            return None

    def get_explorer_url(self, tx_id: str) -> str:
        """Get Solana explorer URL for a transaction."""
        return _get_explorer_url(tx_id, self.network)

    def get_payer_address(self) -> str:
        """Get the payer's public key."""
        return str(self.payer.public_key)


# ── Mock client (testing) ─────────────────────────────────────────────────────

class MockSolanaAttestationClient:
    """
    Mock Solana client for testing without network access.
    Simulates artifact attestation for development/CI.
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        payer_secret_key: Optional[str] = None,
        network: str = "devnet",
    ):
        """Initialize mock client."""
        self.network = network
        self.rpc_url = _get_rpc_url(network, rpc_url)
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
            "explorer_url": _get_explorer_url(tx_id, self.network),
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
        return _get_explorer_url(tx_id, self.network)

    def get_payer_address(self) -> str:
        """Get payer address."""
        return self.payer_address


# ── Factory ───────────────────────────────────────────────────────────────────

def create_solana_client(
    use_mock: bool = False,
    rpc_url: Optional[str] = None,
    payer_secret_key: Optional[str] = None,
    network: Optional[str] = None,
) -> "SolanaAttestationClient":
    """
    Factory function to create a Solana attestation client.

    Args:
        use_mock: If True, uses mock client for testing
        rpc_url: Solana RPC endpoint (auto-derived from network if not set)
        payer_secret_key: Payer's secret key
        network: Solana network (devnet, mainnet-beta). Defaults to SOLANA_NETWORK env var.

    Returns:
        SolanaAttestationClient or MockSolanaAttestationClient instance
    """
    if network is None:
        network = os.getenv("SOLANA_NETWORK", "devnet")

    if use_mock:
        return MockSolanaAttestationClient(rpc_url, payer_secret_key, network)

    return SolanaAttestationClient(rpc_url, payer_secret_key, network)
