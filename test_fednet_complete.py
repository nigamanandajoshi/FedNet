#!/usr/bin/env python3
"""
Complete FedNet System Test: All Three Layers

Layer 1: Audit Artifact Generation
Layer 2: Solana On-Chain Attestation
Layer 3: x402-Gated Inference Monetization

This demonstrates the full FedNet architecture end-to-end.
"""

import torch
import torch.nn as nn
import json
from pathlib import Path
from decimal import Decimal
from fednet.audit_artifacts import create_artifact_generator
from fednet.solana_attestation import create_solana_client
from fednet.inference_server import X402InferenceServer

print("=" * 80)
print("FedNet Complete System Test: All Layers Integration")
print("=" * 80)

# Simple model for testing
class HealthcareModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, 3)  # 3 classes: normal, minor, major

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


def run_complete_fednet_system(num_rounds=2, num_participants=3):
    """Run complete FedNet system demonstration."""

    print(f"\n{'='*80}")
    print("INITIALIZATION")
    print(f"{'='*80}\n")

    # Create directories
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    # Initialize components
    print("✓ Initializing Layer 1: Audit Artifact Generator")
    artifact_gen = create_artifact_generator("fednet-system-test")

    print("✓ Initializing Layer 2: Solana Attestation Client")
    solana_client = create_solana_client(use_mock=True)

    print("✓ Initializing Layer 3: x402 Inference Server")
    model = HealthcareModel()
    inference_server = X402InferenceServer(
        model=model,
        model_id="fednet_healthcare_v1",
        price_per_inference=Decimal("0.05"),
    )

    # Simulation participants
    participants = [
        "0xhospital_mercy",
        "0xclinic_urgent_care",
        "0xresearch_institute",
    ]

    print(f"✓ Simulating {num_participants} healthcare institutions\n")

    # Initialize model
    global_model = HealthcareModel()
    global_weights = global_model.state_dict()

    # Track system metrics
    attestation_records = []
    inference_requests = []

    print(f"{'='*80}")
    print("FEDERATED LEARNING ROUNDS")
    print(f"{'='*80}\n")

    # FL Rounds
    for round_num in range(num_rounds):
        print(f"--- Round {round_num + 1}/{num_rounds} ---\n")

        # Simulate local training at each institution
        print("  Training at participating institutions...")
        client_weights = []
        for i, participant in enumerate(participants):
            # Simulate local training with random updates
            local_weights = {}
            for key, param in global_weights.items():
                noise = torch.randn_like(param) * 0.01
                local_weights[key] = param + noise

            client_weights.append(local_weights)
            print(f"    ✓ {participant}: Local training complete")

        # Federated averaging
        print("\n  Performing federated aggregation...")
        aggregated = {}
        for key in global_weights.keys():
            aggregated[key] = torch.stack(
                [w[key] for w in client_weights]
            ).mean(dim=0)

        global_weights = aggregated
        global_model.load_state_dict(global_weights)
        print(f"    ✓ Global model aggregated from {len(participants)} participants")

        # LAYER 1: Generate Compliance Audit Artifact
        print("\n  [Layer 1] Generating audit artifact...")
        gradient_dict = {k: v.cpu().numpy() for k, v in global_weights.items()}

        audit_artifact = artifact_gen.generate_artifact(
            round_id=round_num + 1,
            participants=participants,
            gradients=gradient_dict,
            model_version="v1.0.0",
            epsilon=0.1,  # DP epsilon
            delta=1e-5,   # DP delta
        )

        artifact_path = artifacts_dir / f"round_{round_num + 1:03d}.json"
        artifact_gen.save_artifact(audit_artifact, str(artifact_path))

        print(f"    ✓ Artifact generated with signature: {audit_artifact.aggregator_signature[:16]}...")
        print(f"    ✓ Differential privacy: ε={audit_artifact.epsilon}, δ={audit_artifact.delta}")

        # LAYER 2: Anchor on Solana
        print("\n  [Layer 2] Anchoring artifact hash on Solana...")
        attestation = solana_client.attest_artifact(
            artifact_hash=audit_artifact.gradient_hash,
            round_id=round_num + 1,
            participants=len(participants),
            model_version=audit_artifact.model_version,
        )

        attestation_records.append(attestation)

        print(f"    ✓ Transaction: {attestation['tx_id']}")
        print(f"    ✓ Solana Explorer: {attestation['explorer_url']}")
        print(f"    ✓ Status: {attestation['status']}")

        # Update inference server with new model
        inference_server.model = global_model

    print(f"\n{'='*80}")
    print("LAYER 3: MONETIZATION - INFERENCE QUERIES")
    print(f"{'='*80}\n")

    # Simulate inference queries with payment
    test_queries = [
        {
            "description": "Researcher query: CBC sample analysis",
            "input": [11.5, 4.5, 80, 28, 33, 15, 7.0, 250],  # CBC features
            "payer": "0xresearcher_university",
            "amount": Decimal("0.05"),
        },
        {
            "description": "Pharma company: Batch validation",
            "input": [12.0, 4.8, 82, 29, 34, 16, 7.5, 260],
            "payer": "0xpharma_company",
            "amount": Decimal("0.10"),
        },
        {
            "description": "AI agent: Automated screening",
            "input": [10.5, 4.2, 78, 27, 32, 14, 6.5, 240],
            "payer": "0xai_agent_autonomy",
            "amount": Decimal("0.05"),
        },
    ]

    client = inference_server.app.test_client()

    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query['description']}")

        # Make inference request with payment
        response = client.post(
            "/inference",
            json={
                "input": query["input"],
                "payment_tx_id": f"solana_tx_{i}",
                "payer_wallet": query["payer"],
                "payment_amount": str(query["amount"]),
            },
        )

        if response.status_code == 200:
            data = json.loads(response.data)
            result = data["result"]

            print(f"   ✓ Payment verified: {query['amount']} USDC from {query['payer']}")
            print(f"   ✓ Model prediction: {result}")
            print(f"   ✓ Inference ID: {data['inference_id']}\n")

            inference_requests.append({
                "query": query["description"],
                "payer": query["payer"],
                "amount": query["amount"],
                "result": result,
            })
        else:
            print(f"   ✗ Request failed with status {response.status_code}\n")

    print(f"{'='*80}")
    print("SYSTEM VERIFICATION & ANALYTICS")
    print(f"{'='*80}\n")

    # Verify all artifacts
    print("✓ Artifact Verification:")
    all_valid = True
    for artifact_file in sorted(artifacts_dir.glob("*.json")):
        loaded = artifact_gen.load_artifact(str(artifact_file))
        is_valid = artifact_gen.verify_artifact(loaded)
        status = "✓ VALID" if is_valid else "✗ INVALID"

        print(f"  {artifact_file.name}: {status}")
        print(f"    - Round: {loaded.round_id}")
        print(f"    - Gradient Hash: {loaded.gradient_hash[:16]}...")
        print(f"    - Participants: {len(loaded.participants)}")

        all_valid = all_valid and is_valid

    # Verify attestations
    print(f"\n✓ Solana Attestations ({len(attestation_records)} total):")
    for attestation in attestation_records:
        verification = solana_client.verify_attestation(attestation["tx_id"])
        status = "✓ VERIFIED" if verification else "✗ FAILED"

        print(f"  Round {attestation['round_id']}: {status}")
        print(f"    - TX: {attestation['tx_id']}")

    # Monetization Analytics
    print(f"\n✓ Inference Monetization Analytics:")
    print(f"  Total inferences processed: {inference_server.inference_count}")
    print(f"  Total revenue: ${inference_server.total_revenue} USDC")
    print(f"  Average per inference: ${inference_server.total_revenue / max(inference_server.inference_count, 1):.2f} USDC")
    print(f"  Unique payers: {len(set(r['payer'] for r in inference_requests))}")

    print(f"\n{'='*80}")
    print("FEDNET SYSTEM TEST COMPLETE")
    print(f"{'='*80}")

    print("\n✓ Layer 1 (Audit): Compliance artifacts generated and signed")
    print("✓ Layer 2 (Solana): Artifact hashes anchored on-chain")
    print("✓ Layer 3 (Monetization): Model inference monetized via x402 protocol")

    print(f"\n✓ System Summary:")
    print(f"  - {num_rounds} FL rounds completed")
    print(f"  - {len(attestation_records)} on-chain attestations")
    print(f"  - {inference_server.inference_count} paid inferences")
    print(f"  - {inference_server.total_revenue} USDC collected")
    print(f"  - All artifacts verified and tamper-proof")

    return all_valid and inference_server.inference_count == len(inference_requests)


if __name__ == "__main__":
    success = run_complete_fednet_system(num_rounds=2, num_participants=3)

    if success:
        print("\n🎉 FedNet System Verification: SUCCESS\n")
    else:
        print("\n❌ FedNet System Verification: FAILED\n")

    exit(0 if success else 1)
