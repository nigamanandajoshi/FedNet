# FedNet Quick Start Guide

Get FedNet running in 5 minutes.

## Prerequisites

- Python 3.9+
- Git

## Setup

```bash
# Clone the repository
git clone https://github.com/nigamanandajoshi/FedNet.git
cd FedNet

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the System

### Option 1: Test All Three Layers (Recommended)

```bash
python test_fednet_complete.py
```

This runs:
- ✓ 2 FL training rounds
- ✓ Layer 1: Generates 2 signed compliance artifacts
- ✓ Layer 2: Anchors artifacts on Solana (mock)
- ✓ Layer 3: Processes 3 inference queries with payments

**Expected Output:**
```
🎉 FedNet System Verification: SUCCESS
```

### Option 2: Layer 1 Only (Audit Artifacts)

```bash
python test_fednet_layer1.py
```

Demonstrates compliance artifact generation and verification.

### Option 3: Layers 1 & 2 (Audit + Solana)

```bash
python test_fednet_layer1_layer2.py
```

Shows artifacts being anchored on Solana.

## Run Tests

```bash
# All tests
pytest tests/ -v

# Layer 1 tests
pytest tests/test_audit_artifacts.py -v

# Layer 2 tests
pytest tests/test_solana_attestation.py -v

# Layer 3 tests
pytest tests/test_x402_payment.py -v
pytest tests/test_inference_server.py -v
```

## Launch Dashboard

```bash
python -c "from fednet.dashboard_server import create_dashboard; create_dashboard(port=5001).run()"
```

Then open: `http://localhost:5001`

## What Each Layer Does

### Layer 1: Audit Artifacts
- Generates signed JSON compliance records
- Contains: participants, gradient hash, DP parameters
- HMAC-SHA256 signatures for tamper-proof verification

**Files Generated:**
```
artifacts/
├── round_001.json
├── round_002.json
└── ...
```

### Layer 2: Solana Attestation
- Hashes artifacts and anchors on Solana devnet
- Creates tamper-proof audit trail
- Cost: ~$0.000005 per attestation

**Sample Output:**
```
Explorer: https://explorer.solana.com/tx/mock_tx_1_77c7f730?cluster=devnet
```

### Layer 3: x402 Monetization
- Gates model inference behind payments
- HTTP 402 response: "Payment Required"
- Verifies USDC payments on Solana
- Distributes revenue to contributing nodes

**Sample Payment:**
```
POST /inference
{
  "input": [0.1, 0.2, ...],
  "payment_tx_id": "solana_tx_signature",
  "payer_wallet": "0xresearcher",
  "payment_amount": "0.05"
}
```

## Key Commands Reference

| Task | Command |
|------|---------|
| Run complete system | `python test_fednet_complete.py` |
| Run Layer 1 only | `python test_fednet_layer1.py` |
| Run Layers 1+2 | `python test_fednet_layer1_layer2.py` |
| Run all tests | `pytest tests/ -v` |
| Launch dashboard | `python -c "from fednet.dashboard_server import create_dashboard; create_dashboard().run()"` |
| View documentation | `cat FEDNET.md` |

## Understanding the Output

When you run `test_fednet_complete.py`, you'll see:

### 1. Training Phase
```
--- FL Round 1/2 ---
  Training at participating institutions...
    ✓ 0xhospital_mercy: Local training complete
```

### 2. Audit Phase
```
  [Layer 1] Generating audit artifact...
    ✓ Artifact generated with signature: 7f6877e9...
    ✓ Differential privacy: ε=0.1, δ=1e-05
```

### 3. Attestation Phase
```
  [Layer 2] Anchoring artifact hash on Solana...
    ✓ Transaction: mock_tx_1_77c7f730
    ✓ Solana Explorer: https://explorer.solana.com/tx/mock_tx_1_77c7f730?cluster=devnet
```

### 4. Monetization Phase
```
  ✓ Payment verified: 0.05 USDC from 0xresearcher_university
  ✓ Model prediction: [-1.12, -2.97, 1.23]
  ✓ Inference ID: 000001
```

## File Structure

```
FedNet/
├── fednet/
│   ├── audit_artifacts.py         # Layer 1
│   ├── solana_attestation.py       # Layer 2
│   ├── x402_payment.py             # Layer 3
│   ├── inference_server.py         # Layer 3
│   ├── dashboard_server.py         # Dashboard
│   └── __init__.py
├── tests/
│   ├── test_audit_artifacts.py
│   ├── test_solana_attestation.py
│   ├── test_x402_payment.py
│   └── test_inference_server.py
├── artifacts/                      # Generated compliance artifacts
├── test_fednet_layer1.py
├── test_fednet_layer1_layer2.py
├── test_fednet_complete.py
├── FEDNET.md                       # Full documentation
├── QUICKSTART.md                   # This file
└── requirements.txt
```

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'fednet'`

Make sure you're in the project root and have activated the virtual environment:

```bash
cd FedNet
source venv/bin/activate
python test_fednet_complete.py
```

### Error: `ImportError: No module named 'torch'`

Reinstall dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Tests not found

```bash
cd FedNet
source venv/bin/activate
pytest tests/ -v
```

## Next Steps

1. **Understand the Architecture**: Read `FEDNET.md`
2. **Run Complete Demo**: `python test_fednet_complete.py`
3. **Explore the Code**:
   - `fednet/audit_artifacts.py` — How compliance artifacts are created
   - `fednet/solana_attestation.py` — How artifacts get on-chain
   - `fednet/x402_payment.py` — How inference is monetized
4. **Integrate with Your FL System**:
   - Replace `test_fednet_*.py` imports with your FL implementation
   - Use `AuditArtifactGenerator` after each training round
   - Use `SolanaAttestationClient` to anchor artifacts
   - Use `X402InferenceServer` to gate inference

## Performance

- **Artifact Generation**: ~100ms per round
- **Solana Attestation**: ~2-3s per transaction (devnet)
- **Inference Query**: <100ms (depends on model size)
- **Payment Processing**: Instant verification on-chain

## For Production

FedNet is production-ready. To deploy:

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env:
#   ENVIRONMENT=production
#   SOLANA_NETWORK=mainnet-beta   (or keep devnet for demo)
#   RECEIVER_WALLET=<your-solana-wallet>
#   SECRET_KEY=<strong-random-key>
#   HMAC_SIGNING_KEY=<strong-random-key>

# 2. Deploy with gunicorn
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4

# 3. Or deploy with Docker
cd deployment && docker compose up --build -d
```

Features enabled in production:
- Real Solana RPC payment verification (tx confirmation + USDC balance checks)
- Rate limiting (200 req/min)
- Non-root Docker containers with health checks
- Replay protection (duplicate tx_id rejection)
- Production secret validation (fails loudly if dev secrets are used)

## Questions?

See `FEDNET.md` for:
- Detailed architecture
- Technical risks and mitigations
- Regulatory compliance information
- Deployment guide

---

**Ready to go?** Run: `python test_fednet_complete.py`
