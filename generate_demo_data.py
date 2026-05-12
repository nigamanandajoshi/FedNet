#!/usr/bin/env python3
"""
Generate sample FedNet demo data for dashboard display.
Runs on startup to populate artifacts and attestations.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from fednet.audit_artifacts import create_artifact_generator
from fednet.solana_attestation import create_solana_client

def generate_demo_artifacts():
    """Generate sample artifacts for dashboard demo."""

    artifacts_dir = Path("artifacts")
    attestations_dir = Path("attestations")

    artifacts_dir.mkdir(exist_ok=True)
    attestations_dir.mkdir(exist_ok=True)

    # Skip if artifacts already exist
    if list(artifacts_dir.glob("*.json")):
        print("✓ Demo artifacts already exist, skipping generation")
        return

    print("Generating demo FedNet artifacts...")

    # Initialize generators
    artifact_gen = create_artifact_generator("fednet-demo")
    solana_client = create_solana_client(use_mock=True)

    # Generate 2 demo rounds
    demo_participants = [
        "0xhospital_mercy",
        "0xclinic_urgent_care",
        "0xresearch_institute"
    ]

    for round_num in range(1, 3):
        print(f"  Generating round {round_num}...")

        # Create mock gradients
        import numpy as np
        gradients = {
            f"layer_{i}": np.random.randn(10, 10).astype(np.float32)
            for i in range(3)
        }

        # Generate artifact
        artifact = artifact_gen.generate_artifact(
            round_id=round_num,
            participants=demo_participants,
            gradients=gradients,
            model_version="v1.0.0",
            epsilon=0.1,
            delta=1e-5,
        )

        # Save artifact
        artifact_path = artifacts_dir / f"round_{round_num:03d}.json"
        artifact_gen.save_artifact(artifact, str(artifact_path))
        print(f"    ✓ Artifact saved: {artifact_path.name}")

        # Generate attestation
        attestation = solana_client.attest_artifact(
            artifact_hash=artifact.gradient_hash,
            round_id=round_num,
            participants=len(demo_participants),
            model_version=artifact.model_version,
        )

        # Save attestation
        attestation_path = attestations_dir / f"round_{round_num:03d}.json"
        with open(attestation_path, "w") as f:
            json.dump(attestation, f, indent=2, default=str)
        print(f"    ✓ Attestation saved: {attestation_path.name}")

    print("✓ Demo data generation complete!")

if __name__ == "__main__":
    generate_demo_artifacts()
