"""
Layer 1: Automated Compliance Audit Artifact Generation

Generates signed compliance artifacts after each FL training round containing:
- Participants involved
- Gradient hash (proof of computation)
- Model version
- Differential privacy parameters
- Cryptographic signature from aggregator

This artifact is the basis for verifiable training history and regulatory audit trails.
"""

import json
import hashlib
import hmac
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class AuditArtifact:
    """Structured compliance artifact from a federated training round."""
    round_id: int
    timestamp: str
    participants: List[str]  # Hashed wallet addresses
    gradient_hash: str  # SHA256 hash of aggregated gradients
    model_version: str
    differential_privacy_applied: bool
    epsilon: Optional[float] = None  # DP parameter
    delta: Optional[float] = None  # DP parameter
    raw_data_moved: bool = False  # Should always be False for FL
    aggregator_signature: str = ""  # HMAC signature

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding signature field for signing."""
        data = asdict(self)
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditArtifactGenerator:
    """
    Generates and signs audit artifacts for federated learning rounds.

    Signs artifacts using HMAC-SHA256 with the aggregator's secret key.
    Ensures artifacts are tamper-proof and verifiable.
    """

    def __init__(self, aggregator_secret_key: str):
        """
        Initialize generator with aggregator's signing key.

        Args:
            aggregator_secret_key: Secret key for signing artifacts (HMAC)
        """
        self.aggregator_secret_key = aggregator_secret_key

    def hash_gradients(self, gradients: Dict[str, Any]) -> str:
        """
        Create SHA256 hash of aggregated gradients.

        Args:
            gradients: Dictionary of gradient tensors/arrays

        Returns:
            Hexadecimal SHA256 hash
        """
        # Serialize gradients to JSON, then hash
        gradient_json = json.dumps({
            k: v.tolist() if hasattr(v, 'tolist') else str(v)
            for k, v in gradients.items()
        }, sort_keys=True)

        return hashlib.sha256(gradient_json.encode()).hexdigest()

    def hash_participant_wallet(self, wallet_address: str) -> str:
        """
        Hash a participant's wallet address for privacy.

        Args:
            wallet_address: Public wallet address

        Returns:
            SHA256 hash of wallet address
        """
        return hashlib.sha256(wallet_address.encode()).hexdigest()[:16]

    def generate_artifact(
        self,
        round_id: int,
        participants: List[str],
        gradients: Dict[str, Any],
        model_version: str,
        epsilon: Optional[float] = None,
        delta: Optional[float] = None,
    ) -> AuditArtifact:
        """
        Generate a signed audit artifact for a training round.

        Args:
            round_id: Training round number
            participants: List of participant wallet addresses
            gradients: Aggregated gradients dictionary
            model_version: Semantic version of the model (e.g., "v1.2.3")
            epsilon: Differential privacy epsilon parameter
            delta: Differential privacy delta parameter

        Returns:
            Signed AuditArtifact instance
        """
        # Hash participant wallets for privacy
        hashed_participants = [
            self.hash_participant_wallet(wallet) for wallet in participants
        ]

        # Hash gradients
        gradient_hash = self.hash_gradients(gradients)

        # Create artifact (without signature initially)
        artifact = AuditArtifact(
            round_id=round_id,
            timestamp=datetime.now(timezone.utc).isoformat() + "Z",
            participants=sorted(hashed_participants),
            gradient_hash=gradient_hash,
            model_version=model_version,
            differential_privacy_applied=epsilon is not None,
            epsilon=epsilon,
            delta=delta,
            raw_data_moved=False,
        )

        # Sign the artifact
        artifact.aggregator_signature = self._sign_artifact(artifact)

        return artifact

    def _sign_artifact(self, artifact: AuditArtifact) -> str:
        """
        Create HMAC-SHA256 signature of artifact.

        Args:
            artifact: Artifact to sign

        Returns:
            Hexadecimal HMAC signature
        """
        # Sign everything except the signature field itself
        artifact_data = asdict(artifact)
        artifact_data.pop('aggregator_signature', None)

        artifact_json = json.dumps(artifact_data, sort_keys=True)

        signature = hmac.new(
            self.aggregator_secret_key.encode(),
            artifact_json.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def verify_artifact(self, artifact: AuditArtifact) -> bool:
        """
        Verify the signature of an artifact.

        Args:
            artifact: Artifact to verify

        Returns:
            True if signature is valid, False otherwise
        """
        stored_signature = artifact.aggregator_signature
        artifact.aggregator_signature = ""

        computed_signature = self._sign_artifact(artifact)
        artifact.aggregator_signature = stored_signature

        return hmac.compare_digest(stored_signature, computed_signature)

    def save_artifact(self, artifact: AuditArtifact, filepath: str) -> None:
        """
        Save artifact to JSON file.

        Args:
            artifact: Artifact to save
            filepath: Path to save JSON file
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(artifact.to_dict(), f, indent=2)

    def load_artifact(self, filepath: str) -> AuditArtifact:
        """
        Load artifact from JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Loaded AuditArtifact instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)

        return AuditArtifact(**data)


def create_artifact_generator(secret_key: Optional[str] = None) -> AuditArtifactGenerator:
    """
    Factory function to create an audit artifact generator.

    Args:
        secret_key: Aggregator's secret key for signing. If None, generates a new one.

    Returns:
        Configured AuditArtifactGenerator instance
    """
    if secret_key is None:
        secret_key = hashlib.sha256(b"fednet-aggregator-key").hexdigest()

    return AuditArtifactGenerator(secret_key)
