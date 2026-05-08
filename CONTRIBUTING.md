# Contributing to FedNet

FedNet is the governance, auditability, and monetization layer for
federated learning. Contributions that improve correctness, extend
functionality, or add integration examples are welcome.

---

## Setup

```bash
git clone https://github.com/nigamanandajoshi/FedNet.git
cd FedNet
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Locally

```bash
# Run the complete 3-layer demo
python test_fednet_complete.py

# Run individual layer tests
python test_fednet_layer1.py          # Layer 1 only
python test_fednet_layer1_layer2.py   # Layers 1 & 2

# Run automated tests
pytest tests/ -v

# Launch dashboard
python -c "from fednet.dashboard_server import create_dashboard; create_dashboard(port=5001).run()"
```

---

## Project Structure

```
FedNet/
├── fednet/                         # Core governance package
│   ├── audit_artifacts.py          #   Layer 1: Compliance artifacts
│   ├── solana_attestation.py       #   Layer 2: Solana attestation
│   ├── x402_payment.py             #   Layer 3: Payment processing
│   ├── inference_server.py         #   Layer 3: Inference endpoint
│   └── dashboard_server.py         #   Monitoring dashboard
│
├── tests/                          # Automated test suites
├── models/                         # ML model architectures
├── training/                       # Local training logic
├── federated/                      # FL orchestration & aggregation
├── blockchain/                     # Local blockchain ledger
├── api/                            # Flask REST API
├── docs/                           # Extended documentation
└── requirements.txt
```

---

## Areas Open for Contribution

| Area | Difficulty | Description |
|------|-----------|-------------|
| Compliance templates | Easy | Add audit artifact templates for different regulations (GDPR, HIPAA) |
| FL framework integration | Medium | Integration examples with NVIDIA FLARE, PySyft, TFF |
| Differential privacy | Medium | Extend DP noise mechanisms and reporting |
| Solana mainnet support | Medium | Production-ready Solana attestation client |
| x402 payment validation | Medium | Full on-chain payment verification |
| Multi-chain support | Hard | Attestation on Ethereum, Polygon, or other chains |
| Secure aggregation | Hard | Encrypted gradient aggregation |
| Benchmarking suite | Medium | Accuracy + latency benchmarks across configurations |
| Docker deployment | Easy | Containerize the full system for reproducible testing |

---

## Contribution Workflow

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test: run `pytest tests/ -v` and verify all tests pass
5. Open a Pull Request with a clear description of what changed and why

## Code Style

- Follow PEP 8
- Type hints on all function signatures
- Docstrings on all classes and public functions
- No hardcoded paths — use environment variables or config files
- Tests for any new functionality

---

## Questions

Open an issue with the `question` label or reach out at
[nigamanandajoshi@gmail.com](mailto:nigamanandajoshi@gmail.com)
