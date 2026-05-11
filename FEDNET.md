# FedNet: Federated Learning Governance, Auditability & Monetization

> **FedNet is NOT a federated learning platform.** We are the governance, auditability, and monetization layer that sits on top of federated learning—including on top of existing tools like NVIDIA FLARE or any custom FL implementation.

## The Problem

Federated learning solves the data movement problem: raw data never leaves the institution. However, it leaves three adjacent problems that compliance officers and regulators actually care about:

### 1. **No Audit Trail**
After a federated training round, there is no tamper-proof record of what happened.
- Which institutions participated?
- Was differential privacy actually applied?
- What model version was produced?
- A hospital HIPAA compliance officer has no artifact to show an auditor.

### 2. **No Verifiable Attestation**
Even if a training log exists, it lives in a centralized database controlled by the orchestrator. There is no independent, tamper-proof source of truth for training history that a regulator could verify without trusting the platform operator.

### 3. **No Monetization Path for Contributing Institutions**
Once a federated model is trained, it has value. External researchers, pharmaceutical companies, and AI agents want to query it. But there is no mechanism for the institutions that contributed their data and compute to capture any of that value.

---

## What FedNet Adds: Three Layers

### **Layer 1: Audit Artifact Generation**

After every federated training round, FedNet's aggregator automatically generates a signed compliance artifact:

```json
{
  "round_id": 47,
  "timestamp": "2026-05-08T14:23:01Z",
  "participants": [
    "hash(hospital_A_wallet)",
    "hash(clinic_B_wallet)",
    "hash(research_lab_C_wallet)"
  ],
  "gradient_hash": "0x7f3a9b...",
  "model_version": "v1.2.3",
  "differential_privacy_applied": true,
  "epsilon": 0.1,
  "delta": 1e-5,
  "raw_data_moved": false,
  "aggregator_signature": "0x9b2c..."
}
```

This artifact answers every question a HIPAA auditor would ask:
- ✓ Who participated?
- ✓ What privacy guarantees were applied?
- ✓ What model was produced?
- ✓ Cryptographic proof that no raw data was transmitted

**Important Caveat:** We do not claim this artifact alone satisfies HIPAA or GDPR. It is one component of a compliant architecture that also requires institutional data governance agreements, contractual controls, and legal review. We claim it is a **necessary artifact that is currently missing** from every FL implementation we are aware of.

### **Layer 2: On-Chain Attestation via Solana State Compression**

The audit artifact is hashed and anchored on Solana using state compression:

```
Audit Artifact
    ↓
Converted to SHA256 Hash
    ↓
Stored on Solana Devnet via state compression
    ↓
Cost: ~$0.000005 per attestation
    ↓
Result: Permanent, tamper-proof, publicly verifiable
```

The on-chain record contains **only the hash**—never gradients, never dataset metrics, never anything that could constitute regulated data. The hash proves the artifact existed at a specific time and has not been altered since.

Any regulator, auditor, or consortium member can verify training history without trusting the platform operator.

**Why Solana?** Solana does cheap, permanent, tamper-proof anchoring. State compression makes it economically viable at scale—thousands of training rounds cost dollars, not thousands of dollars.

### **Layer 3: x402-Gated Inference Endpoint**

Once the federated model is trained, FedNet exposes an x402-gated inference endpoint. External parties—researchers, pharmaceutical companies, AI agents—pay per query via x402 on Solana:

```
External researcher queries the model
    ↓
Hits FedNet inference endpoint
    ↓
Receives HTTP 402: pay 0.05 USDC to proceed
    ↓
Submits x402 payment on Solana
    ↓
FedNet verifies payment on-chain
    ↓
Model runs inference and returns the result
    ↓
USDC splits automatically to contributing nodes
    proportional to verified task completion
```

Compensation to contributing nodes is **task-based, not dataset-size-based.** A node earns for:
- Being online during the round
- Completing the approved training job
- Passing gradient schema validation
- Submitting an accepted encrypted update

This is more manipulation-resistant than dataset-size payouts, which can be spoofed.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Federated Learning Implementation (NVIDIA FLARE, etc) │
│  (Your existing FL system here)                         │
│                                                         │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────┐
│              FedNet Governance Layer                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✓ Layer 1: Audit Artifacts                            │
│    - Signed compliance records                         │
│    - Gradient hashes + DP parameters                   │
│    - HMAC-SHA256 signatures                            │
│                                                         │
│  ✓ Layer 2: Solana Attestation                         │
│    - State compression anchoring                       │
│    - On-chain verification                            │
│    - Public audit trail                               │
│                                                         │
│  ✓ Layer 3: x402 Monetization                          │
│    - Payment-gated inference                           │
│    - USDC distribution to nodes                        │
│    - Revenue analytics                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## How FedNet Differs from Competitors

The vetting identified six overlapping projects: dezi-network, pearl-protocol, obscura-1, computeshare, instruere, and FL Alliance. All six share the same core positioning: federated learning for regulated data with some form of on-chain incentive.

**FedNet differs in one specific way:** We are not building another FL platform. We are building the audit and governance layer that any FL implementation is missing. Our audit artifact and on-chain attestation work with NVIDIA FLARE, with dezi-network, with any FL system.

**The analogy:** We are not building another database. We are building the audit logging system that every database needs but none ships with.

---

## Getting Started

### Installation

```bash
git clone https://github.com/nigamanandajoshi/FedNet.git
cd FedNet
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run Layer 1 Only (Audit Artifacts)

```bash
python test_fednet_layer1.py
```

Generates and verifies 2 training rounds worth of signed compliance artifacts.

### Run Layers 1 & 2 (Audit + Solana Attestation)

```bash
python test_fednet_layer1_layer2.py
```

Demonstrates artifact generation + on-chain anchoring.

### Run All Three Layers (Complete System)

```bash
python test_fednet_complete.py
```

Full end-to-end: FL training → audit artifacts → Solana attestation → inference monetization.

### Launch Dashboard

```bash
python -c "from fednet.dashboard_server import create_dashboard; create_dashboard().run()"
```

Opens FedNet dashboard on `http://localhost:5001`

---

## Testing

Run all tests:

```bash
pytest tests/ -v
```

Individual test suites:

```bash
pytest tests/test_audit_artifacts.py -v      # Layer 1
pytest tests/test_solana_attestation.py -v   # Layer 2
pytest tests/test_x402_payment.py -v         # Layer 3 payments
pytest tests/test_inference_server.py -v     # Layer 3 inference
```

---

## Technical Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **FL Core** | PyTorch, Flower | Model training & aggregation |
| **Layer 1** | Python (HMAC-SHA256) | Artifact generation & signing |
| **Layer 2** | Solana SDK, Anchor | On-chain attestation |
| **Layer 3** | Flask, x402 | Inference monetization |
| **Dashboard** | Flask, HTML/JS | Real-time monitoring |
| **Tests** | pytest | Quality assurance |

---

## Directory Structure

```
fednet/
├── audit_artifacts.py          # Layer 1: Audit artifact generation
├── solana_attestation.py        # Layer 2: Solana attestation
├── x402_payment.py              # Layer 3: Payment processing
├── inference_server.py          # Layer 3: Inference endpoint
├── dashboard_server.py          # Dashboard UI
└── __init__.py

tests/
├── test_audit_artifacts.py
├── test_solana_attestation.py
├── test_x402_payment.py
└── test_inference_server.py

artifacts/                       # Generated compliance artifacts
```

---

## Demo Flow

### 1. Training Round
- 3 healthcare institutions train locally
- Gradients aggregated via FedAvg
- Global model updated

### 2. Compliance Audit (Layer 1)
- Audit artifact auto-generated
- Contains: round ID, participants, gradient hash, DP params
- HMAC-SHA256 signed by aggregator

### 3. On-Chain Attestation (Layer 2)
- Artifact hash anchored on Solana
- Solana transaction visible on devnet explorer
- Creates tamper-proof audit trail

### 4. Model Monetization (Layer 3)
- External researcher queries the model
- Hits `/inference` endpoint
- Server returns HTTP 402 (Payment Required)
- Researcher sends USDC payment on Solana
- Server verifies payment on-chain
- Returns model inference results
- USDC automatically split to contributing nodes

---

## Key Features

✅ **Compliance-First Design** — HIPAA audit artifacts out of the box  
✅ **Tamper-Proof Records** — Solana state compression for immutable attestation  
✅ **Automatic Monetization** — x402-gated inference with automatic node payouts  
✅ **Privacy Preserving** — Differential privacy built into every artifact  
✅ **Platform Agnostic** — Works with any FL implementation  
✅ **Auditor-Ready** — Structured JSON artifacts for regulatory review  

---

## Deployment

### Development

```bash
python test_fednet_complete.py
python -c "from fednet.dashboard_server import create_dashboard; create_dashboard(port=5001).run(debug=True)"
```

### Production

FedNet is production-ready. To deploy:

1. Copy `.env.example` to `.env` and set `ENVIRONMENT=production`
2. Set `SECRET_KEY` and `JWT_SECRET_KEY` to strong, unique values
3. Set `SOLANA_NETWORK=mainnet-beta` (or keep `devnet` for demo)
4. Set `RECEIVER_WALLET` to your Solana wallet address
5. Set `HMAC_SIGNING_KEY` to a strong key for artifact signing
6. Deploy with gunicorn: `gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 4`
7. Or use Docker: `cd deployment && docker compose up --build -d`

---

## Technical Risks & Mitigations

### Risk: Gradient Inversion Attacks
**Per NIST guidance:** FL alone is not a complete privacy solution. Gradients can partially reconstruct training data.

**Mitigation:** Apply differential privacy noise before gradient transmission. Use secure aggregation.

### Risk: Spoofed Node Contributions
**Per a16z DePIN research:** Incentive mechanisms tied to manipulable signals create spoofing risks.

**Mitigation:** Task-based compensation (online time + job completion + schema validation) reduces manipulation. Staking mechanism on V2 roadmap to penalize bad actors.

---

## Regulatory Fit

FedNet addresses specific regulatory gaps:

| Regulator | Concern | FedNet Solution |
|-----------|---------|---|
| **HIPAA** | Data movement audit trail | Layer 1 compliance artifacts |
| **GDPR** | Data processor accountability | Layer 2 on-chain attestation |
| **Financial Regulators** | Model governance transparency | Audit artifact + dashboard |
| **Pharma (21 CFR Part 11)** | Electronic record integrity | Cryptographic signatures + blockchain |

---

## Next Steps (V2)

- [ ] Anchor program with Merkle proofs for state compression optimization
- [ ] Staking mechanism to penalize bad nodes
- [ ] Integration with NVIDIA FLARE framework
- [ ] Multi-chain support (Ethereum, Polygon)
- [ ] Advanced analytics dashboard
- [ ] Regulatory compliance templates

---

## Contributing

FedNet is built on top of any FL implementation. Contributions welcome for:
- Additional auditor compliance templates
- Performance optimizations
- Regulatory documentation
- Integration examples with other FL frameworks

---

## License

Apache 2.0

---

## Citation

If you build on FedNet, please cite:

```bibtex
@software{fednet2026,
  title   = {FedNet: Federated Learning Governance, Auditability & Monetization},
  author  = {Nigamananda Joshi},
  year    = {2026},
  url     = {https://github.com/nigamanandajoshi/FedNet}
}
```

---

## Resources

- [HIPAA Compliance Framework](https://www.hhs.gov/hipaa/)
- [GDPR Data Processor Obligations](https://gdpr-info.eu/)
- [Solana State Compression](https://docs.solana.com/developing/guides/compressed-nfts)
- [x402 HTTP Payment Protocol](https://http.payments.community/)
- [Federated Learning Security (NIST)](https://csrc.nist.gov/)

