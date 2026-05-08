<p align="center">
  <h1 align="center">FedNet</h1>
  <p align="center">
    <strong>Governance · Auditability · Monetization for Federated Learning</strong>
  </p>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white" alt="PyTorch"></a>
  <a href="#"><img src="https://img.shields.io/badge/Solana-devnet-9945FF?style=flat-square&logo=solana&logoColor=white" alt="Solana"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue?style=flat-square" alt="License"></a>
</p>

---

> **FedNet is NOT a federated learning platform.** It is the governance, auditability, and monetization layer that sits *on top* of federated learning — including NVIDIA FLARE, Flower, or any custom FL implementation.

## The Problem

Federated learning keeps raw data local. That is solved. But three adjacent problems remain that compliance officers and regulators actually care about:

| # | Gap | What's Missing |
|---|-----|----------------|
| 1 | **No Audit Trail** | No tamper-proof record of who participated, what privacy was applied, or what model was produced |
| 2 | **No Verifiable Attestation** | Training logs live in a centralized DB controlled by the orchestrator — no independent verification |
| 3 | **No Monetization** | Contributing institutions can't capture value from the model they helped train |

## What FedNet Adds

FedNet provides **three layers** that plug into any existing FL system:

### Layer 1 — Audit Artifacts
After every training round, FedNet auto-generates a signed JSON compliance artifact containing participant hashes, gradient hashes, differential privacy parameters, and HMAC-SHA256 signatures. This answers every question a HIPAA auditor would ask.

### Layer 2 — Solana Attestation
The artifact hash is anchored on Solana via state compression (~$0.000005 per attestation). The on-chain record contains **only the hash** — never gradients, never data. Any regulator can verify training history without trusting the platform operator.

### Layer 3 — x402-Gated Inference
Trained models are exposed via x402-gated endpoints. External parties pay per-query in USDC on Solana. Revenue splits automatically to contributing nodes proportional to verified task completion.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Federated Learning Implementation (NVIDIA FLARE, etc)  │
│  (Your existing FL system — FedNet plugs in here)       │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              FedNet Governance Layer                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✓ Layer 1: Audit Artifacts                             │
│    Signed compliance records · Gradient hashes · DP     │
│                                                         │
│  ✓ Layer 2: Solana Attestation                          │
│    State compression anchoring · Public audit trail     │
│                                                         │
│  ✓ Layer 3: x402 Monetization                           │
│    Payment-gated inference · USDC node distribution     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nigamanandajoshi/FedNet.git
cd FedNet

# Set up environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the complete 3-layer demo
python test_fednet_complete.py
```

**Expected output:**
```
🎉 FedNet System Verification: SUCCESS
```

For a hands-on walkthrough, see the [Quick Start Guide](QUICKSTART.md). For the full technical deep-dive, see [FEDNET.md](FEDNET.md).

## Run Individual Layers

```bash
# Layer 1 only — Audit Artifacts
python test_fednet_layer1.py

# Layers 1 & 2 — Audit + Solana Attestation
python test_fednet_layer1_layer2.py

# All 3 Layers — Complete system
python test_fednet_complete.py

# Launch monitoring dashboard
python -c "from fednet.dashboard_server import create_dashboard; create_dashboard(port=5001).run()"
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Individual test suites
pytest tests/test_audit_artifacts.py -v      # Layer 1
pytest tests/test_solana_attestation.py -v   # Layer 2
pytest tests/test_x402_payment.py -v         # Layer 3 payments
pytest tests/test_inference_server.py -v     # Layer 3 inference
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **FL Core** | PyTorch, Flower | Model training & federated aggregation |
| **Layer 1** | Python (HMAC-SHA256) | Audit artifact generation & signing |
| **Layer 2** | Solana SDK | On-chain attestation via state compression |
| **Layer 3** | Flask, x402 | Payment-gated inference & revenue distribution |
| **Dashboard** | Flask, HTML/JS | Real-time monitoring UI |
| **Blockchain** | Ethereum (Hardhat) | Local ledger & smart contracts |
| **Tests** | pytest | Automated quality assurance |

## Project Structure

```
FedNet/
├── fednet/                         # Core governance package
│   ├── audit_artifacts.py          #   Layer 1: Compliance artifact generation
│   ├── solana_attestation.py       #   Layer 2: Solana attestation client
│   ├── x402_payment.py             #   Layer 3: Payment processing
│   ├── inference_server.py         #   Layer 3: Inference endpoint
│   └── dashboard_server.py         #   Monitoring dashboard
│
├── tests/                          # Automated test suites
│   ├── test_audit_artifacts.py
│   ├── test_solana_attestation.py
│   ├── test_x402_payment.py
│   └── test_inference_server.py
│
├── models/                         # ML model architectures
├── training/                       # Local training logic
├── federated/                      # FL orchestration & aggregation
├── blockchain/                     # Local blockchain ledger
├── blockchain_eth/                 # Ethereum smart contracts (Hardhat)
├── data_loaders/                   # PyTorch dataset loaders
├── data_generation/                # Synthetic data generators
├── api/                            # Flask REST API
├── dashboard/                      # Vite + React monitoring UI
├── scripts/                        # CLI utilities & deployment scripts
├── docs/                           # Extended documentation
├── notebooks/                      # Jupyter exploration notebooks
├── config/                         # Configuration & settings
├── deployment/                     # Docker & cloud deployment
├── azure_ml/                       # Azure ML integration
├── artifacts/                      # Generated compliance artifacts
│
├── FEDNET.md                       # Full technical documentation
├── QUICKSTART.md                   # 5-minute setup guide
├── CONTRIBUTING.md                 # Contribution guidelines
├── requirements.txt                # Python dependencies
├── setup.py                        # Package configuration
├── environment.yml                 # Conda environment
└── LICENSE                         # Apache 2.0
```

## How FedNet Differs

We are **not** building another FL platform. We are building the **audit and governance layer** that every FL implementation needs but none ships with.

Six overlapping projects exist (dezi-network, pearl-protocol, obscura-1, computeshare, instruere, FL Alliance). All position as "federated learning for regulated data with on-chain incentives." FedNet differs in one specific way: our audit artifacts and attestation work **with** any of them — NVIDIA FLARE, Flower, or any custom FL system.

> **The analogy:** We are not building another database. We are building the audit logging system that every database needs.

## Regulatory Fit

| Regulator | Concern | FedNet Solution |
|-----------|---------|-----------------|
| **HIPAA** | Data movement audit trail | Layer 1 compliance artifacts |
| **GDPR** | Data processor accountability | Layer 2 on-chain attestation |
| **Financial** | Model governance transparency | Audit artifacts + dashboard |
| **Pharma (21 CFR Part 11)** | Electronic record integrity | Cryptographic signatures + blockchain |

## Roadmap

- [ ] Anchor program with Merkle proofs for state compression optimization
- [ ] Staking mechanism to penalize bad nodes
- [ ] Integration with NVIDIA FLARE framework
- [ ] Multi-chain support (Ethereum, Polygon)
- [ ] Advanced analytics dashboard
- [ ] Regulatory compliance templates

## Contributing

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Key areas:
- Additional auditor compliance templates
- Integration examples with other FL frameworks
- Performance optimizations
- Regulatory documentation

## License

[Apache 2.0](LICENSE)

## Citation

```bibtex
@software{fednet2026,
  title   = {FedNet: Federated Learning Governance, Auditability & Monetization},
  author  = {Nigamananda Joshi},
  year    = {2026},
  url     = {https://github.com/nigamanandajoshi/FedNet}
}
```

## Author

**Nigamananda Joshi** — [nigamanandajoshi@gmail.com](mailto:nigamanandajoshi@gmail.com) · [LinkedIn](https://linkedin.com/in/nigamananda)

## Resources

- [HIPAA Compliance Framework](https://www.hhs.gov/hipaa/)
- [GDPR Data Processor Obligations](https://gdpr-info.eu/)
- [Solana State Compression](https://docs.solana.com/developing/guides/compressed-nfts)
- [x402 HTTP Payment Protocol](https://http.payments.community/)
- [Federated Learning Security (NIST)](https://csrc.nist.gov/)
