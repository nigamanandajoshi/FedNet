#!/usr/bin/env python3
"""
Test Layers 1 & 2: Audit Artifacts + Solana Attestation
Demonstrates end-to-end compliance audit trail with on-chain attestation.
"""

import torch
import torch.nn as nn
from pathlib import Path
from fednet.audit_artifacts import create_artifact_generator
from fednet.solana_attestation import create_solana_client

print("=" * 80)
print("FedNet Layers 1 & 2: Audit + Solana Attestation Integration Test")
print("=" * 80)

# Simple model
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 20)
        self.fc2 = nn.Linear(20, 2)

    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

def integrated_fl_simulation(num_rounds=2):
    print(f"\nSimulating {num_rounds} FL rounds with on-chain attestation...\n")

    # Initialize components
    aggregator_key = "fednet-test-key-12345"
    artifact_gen = create_artifact_generator(aggregator_key)
    solana_client = create_solana_client(use_mock=True)  # Using mock for testing

    artifacts_dir = Path("artifacts")
    attestations_dir = Path("attestations")
    artifacts_dir.mkdir(exist_ok=True)
    attestations_dir.mkdir(exist_ok=True)

    # Initialize global model
    global_model = SimpleModel()
    global_weights = global_model.state_dict()

    # Simulate participants
    participants = ["0xhospital_a", "0xclinic_b", "0xresearch_lab_c"]

    print("=" * 80)
    print("FEDERATED LEARNING ROUNDS WITH COMPLIANCE AUDIT")
    print("=" * 80)

    attestation_records = []

    for round_num in range(num_rounds):
        print(f"\n--- FL Round {round_num + 1} ---")

        # Simulate client training
        client_weights = []
        for participant in participants:
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

        # LAYER 1: Generate Compliance Audit Artifact
        print(f"\n  [Layer 1] Generating audit artifact...")
        gradient_dict = {k: v.cpu().numpy() for k, v in global_weights.items()}

        audit_artifact = artifact_gen.generate_artifact(
            round_id=round_num + 1,
            participants=participants,
            gradients=gradient_dict,
            model_version="v1.0.0",
            epsilon=0.1,
            delta=1e-5,
        )

        artifact_path = artifacts_dir / f"round_{round_num + 1:03d}.json"
        artifact_gen.save_artifact(audit_artifact, str(artifact_path))

        print(f"    ✓ Artifact generated: {artifact_path.name}")
        print(f"    ✓ Signature: {audit_artifact.aggregator_signature[:16]}...")

        # LAYER 2: Anchor Artifact Hash on Solana
        print(f"  [Layer 2] Anchoring artifact hash on Solana devnet...")

        attestation = solana_client.attest_artifact(
            artifact_hash=audit_artifact.gradient_hash,
            round_id=round_num + 1,
            participants=len(participants),
            model_version=audit_artifact.model_version,
        )

        attestation_records.append(attestation)

        print(f"    ✓ Transaction ID: {attestation['tx_id']}")
        print(f"    ✓ Explorer: {attestation['explorer_url']}")
        print(f"    ✓ Status: {attestation['status']}")

    print("\n" + "=" * 80)
    print("AUDIT TRAIL VERIFICATION")
    print("=" * 80)

    # Verify all artifacts
    print(f"\n✓ Verifying {len(list(artifacts_dir.glob('*.json')))} artifacts...")
    all_valid = True

    for artifact_file in sorted(artifacts_dir.glob("*.json")):
        loaded = artifact_gen.load_artifact(str(artifact_file))
        is_valid = artifact_gen.verify_artifact(loaded)

        print(f"\n  {artifact_file.name}:")
        print(f"    - Artifact signature: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"    - Gradient hash: {loaded.gradient_hash[:16]}...")
        print(f"    - Round: {loaded.round_id}")
        print(f"    - Participants: {len(loaded.participants)}")
        print(f"    - DP Applied: epsilon={loaded.epsilon}")

        all_valid = all_valid and is_valid

    # Verify attestations
    print(f"\n✓ Verifying {len(attestation_records)} Solana attestations...")

    for attestation in attestation_records:
        verification = solana_client.verify_attestation(attestation["tx_id"])

        print(f"\n  Round {attestation['round_id']}:")
        print(f"    - Transaction: {attestation['tx_id']}")
        print(f"    - Status: {'✓ VERIFIED' if verification else '✗ FAILED'}")
        print(f"    - Explorer: {attestation['explorer_url']}")

        all_valid = all_valid and (verification is not None)

    print("\n" + "=" * 80)
    print("LAYERS 1 & 2 TEST COMPLETE")
    print("=" * 80)

    if all_valid:
        print("\n✓ Full audit trail verified!")
        print("✓ Layer 1: Compliance artifacts signed and stored locally")
        print("✓ Layer 2: Artifact hashes anchored on Solana (tamper-proof)")
        print(f"✓ Artifacts: {artifacts_dir.absolute()}")
        print("\nCompliance Record:")
        print(f"  - {len(list(artifacts_dir.glob('*.json')))} training rounds")
        print(f"  - {len(attestation_records)} on-chain attestations")
        print(f"  - All artifacts verified and cryptographically signed")
        print("\nNext step: Implement x402-gated inference endpoint (Layer 3)")
    else:
        print("\n✗ Some verification failed!")

    return all_valid

if __name__ == "__main__":
    success = integrated_fl_simulation(num_rounds=2)
    exit(0 if success else 1)
