#!/usr/bin/env python3
"""
Test Layer 1: Audit Artifact Generation
Demonstrates FedNet's compliance audit capabilities without blockchain setup.
"""

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from pathlib import Path
import numpy as np
from fednet.audit_artifacts import create_artifact_generator

print("=" * 80)
print("FedNet Layer 1: Audit Artifact Generation Test")
print("=" * 80)

# Simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 20)
        self.fc2 = nn.Linear(20, 2)

    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

# Simulate federated training
def simulate_fl_round(num_participants=3, num_rounds=2):
    print(f"\nSimulating {num_rounds} FL rounds with {num_participants} participants...\n")

    # Initialize aggregator and artifact generator
    aggregator_key = "fednet-test-key-12345"
    artifact_gen = create_artifact_generator(aggregator_key)
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    # Initialize global model
    global_model = SimpleModel()
    global_weights = global_model.state_dict()

    # Simulate participants
    participants = [f"0xparticipant{i:03d}" for i in range(num_participants)]

    # FL training loop
    for round_num in range(num_rounds):
        print(f"--- FL Round {round_num + 1} ---")

        # Simulate client training (in reality, each client would train locally)
        client_weights = []
        for participant in participants:
            # Copy global weights and simulate local training by adding noise
            local_weights = {}
            for key, param in global_weights.items():
                noise = torch.randn_like(param) * 0.01
                local_weights[key] = param + noise

            client_weights.append(local_weights)
            print(f"  ✓ {participant}: Local training complete")

        # Federated averaging
        aggregated = {}
        for key in global_weights.keys():
            aggregated[key] = torch.stack([w[key] for w in client_weights]).mean(dim=0)

        global_weights = aggregated
        global_model.load_state_dict(global_weights)

        # Layer 1: Generate Compliance Audit Artifact
        print(f"\n  Generating audit artifact...")

        # Convert weights to numpy for hashing
        gradient_dict = {k: v.cpu().numpy() for k, v in global_weights.items()}

        audit_artifact = artifact_gen.generate_artifact(
            round_id=round_num + 1,
            participants=participants,
            gradients=gradient_dict,
            model_version="v1.0.0",
            epsilon=0.1,  # DP epsilon
            delta=1e-5,   # DP delta
        )

        # Save artifact
        artifact_path = artifacts_dir / f"round_{round_num + 1:03d}.json"
        artifact_gen.save_artifact(audit_artifact, str(artifact_path))

        print(f"  ✓ Audit artifact signed and saved")
        print(f"    - Round ID: {audit_artifact.round_id}")
        print(f"    - Participants: {len(audit_artifact.participants)}")
        print(f"    - Gradient Hash: {audit_artifact.gradient_hash[:16]}...")
        print(f"    - Model Version: {audit_artifact.model_version}")
        print(f"    - DP Applied: epsilon={audit_artifact.epsilon}, delta={audit_artifact.delta}")
        print(f"    - Signature: {audit_artifact.aggregator_signature[:16]}...")
        print(f"    - File: {artifact_path.name}\n")

    # Verify all artifacts
    print("=" * 80)
    print("ARTIFACT VERIFICATION")
    print("=" * 80)

    all_verified = True
    for artifact_file in sorted(artifacts_dir.glob("*.json")):
        loaded = artifact_gen.load_artifact(str(artifact_file))
        is_valid = artifact_gen.verify_artifact(loaded)
        status = "✓ VALID" if is_valid else "✗ INVALID"

        print(f"\n{artifact_file.name}: {status}")
        print(f"  Round: {loaded.round_id}")
        print(f"  Participants: {len(loaded.participants)}")
        print(f"  Gradient Hash: {loaded.gradient_hash[:16]}...")
        print(f"  Raw Data Moved: {loaded.raw_data_moved}")
        print(f"  DP Epsilon: {loaded.epsilon}")
        print(f"  Timestamp: {loaded.timestamp}")

        all_verified = all_verified and is_valid

    print("\n" + "=" * 80)
    print("LAYER 1 TEST COMPLETE")
    print("=" * 80)

    if all_verified:
        print("✓ All artifacts verified successfully!")
        print("✓ Compliance audit trail is complete and tamper-proof")
        print(f"✓ Artifacts location: {artifacts_dir.absolute()}\n")
        print("Next step: Deploy artifacts to Solana for Layer 2 attestation")
    else:
        print("✗ Some artifacts failed verification!")

    return all_verified

if __name__ == "__main__":
    success = simulate_fl_round(num_participants=3, num_rounds=2)
    exit(0 if success else 1)
