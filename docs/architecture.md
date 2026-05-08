# FedNet Architecture

## System Overview

FedNet is the **governance, auditability, and monetization layer** for federated learning. It plugs into any FL implementation (NVIDIA FLARE, Flower, custom) and adds three capabilities that compliance officers and regulators require:

1. **Audit Artifacts** — Signed compliance records after every training round
2. **On-Chain Attestation** — Tamper-proof hash anchoring on Solana
3. **Inference Monetization** — x402-gated model queries with revenue distribution

The underlying FL system handles model training and aggregation. FedNet handles everything else.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│           Any Federated Learning Implementation             │
│           (NVIDIA FLARE, Flower, Custom, etc.)              │
└─────────────────────────┬───────────────────────────────────┘
                          │ Training round completes
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FedNet Governance Layer                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Layer 1: Audit Artifacts                                   │
│  ├── Signed JSON compliance records                         │
│  ├── Participant hashes + gradient hashes + DP params       │
│  └── HMAC-SHA256 signatures for tamper detection            │
│                                                             │
│  Layer 2: Solana Attestation                                │
│  ├── SHA256 hash of artifact → state compression            │
│  ├── ~$0.000005 per attestation on devnet                   │
│  └── Publicly verifiable, immutable audit trail             │
│                                                             │
│  Layer 3: x402 Monetization                                 │
│  ├── HTTP 402 payment-gated inference endpoint              │
│  ├── USDC payments verified on-chain                        │
│  └── Revenue split to contributing nodes (task-based)       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  ┌──────────┐    ┌─────────────┐    ┌──────────┐
  │ Artifacts │    │   Solana    │    │ Inference │
  │  (JSON)   │    │  (On-Chain) │    │  (Flask)  │
  └──────────┘    └─────────────┘    └──────────┘
```

## FL Training Flow

```
Node A (Hospital)      Node B (Clinic)       Node C (Research Lab)
   Local training ──┐    Local training ──┤    Local training ──┐
   (raw data stays) │    (raw data stays) │    (raw data stays) │
                    ▼                     ▼                     ▼
              ┌─────────────────────────────────────────────┐
              │            Aggregator (FedAvg)              │
              │   Weighted average of gradients only        │
              │   Fault-tolerant: continues if node fails   │
              └──────────────────┬──────────────────────────┘
                                 │
                                 ▼
              ┌─────────────────────────────────────────────┐
              │        FedNet Post-Round Processing         │
              │  1. Generate audit artifact (Layer 1)       │
              │  2. Anchor hash on Solana (Layer 2)         │
              │  3. Update inference model (Layer 3)        │
              └─────────────────────────────────────────────┘
```

## Components

### 1. Core Governance Package (`fednet/`)
- **audit_artifacts.py** — Layer 1: Generates and verifies compliance artifacts
- **solana_attestation.py** — Layer 2: Solana state compression anchoring
- **x402_payment.py** — Layer 3: x402 payment verification
- **inference_server.py** — Layer 3: Payment-gated Flask inference server
- **dashboard_server.py** — Real-time monitoring dashboard

### 2. FL Infrastructure
- **models/** — PyTorch model architectures (CBC, Image, Hybrid)
- **training/** — Local training logic and metrics
- **federated/** — FL orchestration and FedAvg aggregation
- **data_loaders/** — PyTorch datasets for each modality
- **data_generation/** — Synthetic data generators

### 3. Blockchain Layer
- **blockchain/** — Local hash-chained ledger
- **blockchain_eth/** — Ethereum smart contracts (Hardhat)

### 4. API & Dashboard
- **api/** — Flask REST API for model serving and status
- **dashboard/** — Vite + React monitoring frontend

### 5. Cloud & Deployment
- **azure_ml/** — Azure ML pipeline integration
- **deployment/** — Docker and cloud deployment configs

## Data Flow

1. **Initialization**: Global model initialized and distributed to nodes
2. **Local Training**: Each node trains on private data (data never leaves)
3. **Update Collection**: Only gradient tensors transmitted
4. **Aggregation**: Combined via FedAvg (weighted by dataset size)
5. **Audit (Layer 1)**: Compliance artifact auto-generated and signed
6. **Attestation (Layer 2)**: Artifact hash anchored on Solana
7. **Monetization (Layer 3)**: Updated model available for paid inference
8. **Iteration**: Repeat for multiple rounds

## Security & Privacy

- **Data Privacy**: Raw data never leaves the originating node
- **Gradient Protection**: Differential privacy noise applied before transmission
- **Tamper Detection**: HMAC-SHA256 signatures on all artifacts
- **On-Chain Verification**: Independent audit trail on Solana (no trust required)
- **Access Control**: Smart contract governance for node registration

## Scalability

- **Horizontal**: Add more FL client nodes
- **Vertical**: Azure ML for GPU compute scaling
- **Asynchronous**: Non-blocking aggregation supported
- **Cost-Efficient**: Solana state compression keeps attestation costs negligible
