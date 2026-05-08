"""Tests for FedNet audit artifact generation."""

import pytest
import json
import tempfile
from pathlib import Path
from fednet.audit_artifacts import (
    AuditArtifact,
    AuditArtifactGenerator,
    create_artifact_generator,
)


class TestAuditArtifact:
    """Test AuditArtifact dataclass."""

    def test_artifact_creation(self):
        """Test creating an artifact."""
        artifact = AuditArtifact(
            round_id=1,
            timestamp="2026-05-08T12:00:00Z",
            participants=["hash1", "hash2"],
            gradient_hash="0x7f3a9b",
            model_version="v1.0.0",
            differential_privacy_applied=True,
            epsilon=0.1,
            delta=1e-5,
        )

        assert artifact.round_id == 1
        assert artifact.model_version == "v1.0.0"
        assert artifact.differential_privacy_applied is True

    def test_artifact_to_json(self):
        """Test artifact serialization to JSON."""
        artifact = AuditArtifact(
            round_id=1,
            timestamp="2026-05-08T12:00:00Z",
            participants=["hash1"],
            gradient_hash="0xabc123",
            model_version="v1.0.0",
            differential_privacy_applied=False,
        )

        json_str = artifact.to_json()
        parsed = json.loads(json_str)

        assert parsed["round_id"] == 1
        assert parsed["model_version"] == "v1.0.0"


class TestAuditArtifactGenerator:
    """Test AuditArtifactGenerator functionality."""

    @pytest.fixture
    def generator(self):
        """Create a test generator."""
        return AuditArtifactGenerator("test-secret-key-12345")

    def test_hash_participant_wallet(self, generator):
        """Test wallet address hashing."""
        wallet = "0x1234567890abcdef"
        hashed = generator.hash_participant_wallet(wallet)

        assert isinstance(hashed, str)
        assert len(hashed) == 16
        assert hashed == generator.hash_participant_wallet(wallet)  # Deterministic

    def test_hash_gradients(self, generator):
        """Test gradient hashing."""
        gradients = {
            "layer1": [0.1, 0.2, 0.3],
            "layer2": [0.4, 0.5, 0.6],
        }

        hash1 = generator.hash_gradients(gradients)
        hash2 = generator.hash_gradients(gradients)

        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 64  # SHA256 hex

    def test_generate_artifact(self, generator):
        """Test artifact generation and signing."""
        participants = ["wallet1", "wallet2", "wallet3"]
        gradients = {
            "layer1.weight": [0.1, 0.2],
            "layer1.bias": [0.3],
        }

        artifact = generator.generate_artifact(
            round_id=1,
            participants=participants,
            gradients=gradients,
            model_version="v1.0.0",
            epsilon=0.1,
            delta=1e-5,
        )

        assert artifact.round_id == 1
        assert len(artifact.participants) == 3
        assert artifact.differential_privacy_applied is True
        assert artifact.aggregator_signature != ""
        assert artifact.raw_data_moved is False

    def test_artifact_signature_verification(self, generator):
        """Test artifact signature verification."""
        artifact = generator.generate_artifact(
            round_id=1,
            participants=["wallet1"],
            gradients={"layer1": [0.1]},
            model_version="v1.0.0",
        )

        assert generator.verify_artifact(artifact) is True

    def test_tampered_artifact_fails_verification(self, generator):
        """Test that tampered artifacts fail verification."""
        artifact = generator.generate_artifact(
            round_id=1,
            participants=["wallet1"],
            gradients={"layer1": [0.1]},
            model_version="v1.0.0",
        )

        # Tamper with the artifact
        artifact.round_id = 2

        assert generator.verify_artifact(artifact) is False

    def test_artifact_persistence(self, generator):
        """Test saving and loading artifacts."""
        artifact = generator.generate_artifact(
            round_id=1,
            participants=["wallet1", "wallet2"],
            gradients={"layer1": [0.1, 0.2]},
            model_version="v1.0.0",
            epsilon=0.1,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "artifact.json"

            # Save
            generator.save_artifact(artifact, str(filepath))
            assert filepath.exists()

            # Load
            loaded = generator.load_artifact(str(filepath))

            assert loaded.round_id == artifact.round_id
            assert loaded.model_version == artifact.model_version
            assert loaded.aggregator_signature == artifact.aggregator_signature
            assert generator.verify_artifact(loaded) is True

    def test_different_generators_cant_verify_artifacts(self):
        """Test that artifacts signed by one generator can't be verified by another."""
        gen1 = AuditArtifactGenerator("secret-key-1")
        gen2 = AuditArtifactGenerator("secret-key-2")

        artifact = gen1.generate_artifact(
            round_id=1,
            participants=["wallet1"],
            gradients={"layer1": [0.1]},
            model_version="v1.0.0",
        )

        assert gen1.verify_artifact(artifact) is True
        assert gen2.verify_artifact(artifact) is False

    def test_factory_function(self):
        """Test artifact generator factory function."""
        gen1 = create_artifact_generator()
        gen2 = create_artifact_generator("custom-secret")

        assert isinstance(gen1, AuditArtifactGenerator)
        assert isinstance(gen2, AuditArtifactGenerator)

    def test_differential_privacy_optional(self, generator):
        """Test that DP parameters are optional."""
        artifact = generator.generate_artifact(
            round_id=1,
            participants=["wallet1"],
            gradients={"layer1": [0.1]},
            model_version="v1.0.0",
            epsilon=None,
            delta=None,
        )

        assert artifact.differential_privacy_applied is False
        assert artifact.epsilon is None
        assert artifact.delta is None
