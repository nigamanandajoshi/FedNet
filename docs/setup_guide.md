# Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 16+ (for dashboard, optional)
- Git
- (Optional) Azure subscription for cloud deployment
- (Optional) CUDA-capable GPU for faster training

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/nigamanandajoshi/FedNet.git
cd FedNet
```

### 2. Python Environment

**Option A: pip + venv (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option B: Conda**
```bash
conda env create -f environment.yml
conda activate fednet
```

### 3. Install Package (Development Mode)

```bash
pip install -e .
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Generate Demo Data (Optional)

```bash
python scripts/generate_demo_data.py --n-samples 1000
```

## Configuration

### Environment Variables

See `.env.example` for all configurable variables. Key settings:

```env
# Federated Learning
FL_ROUNDS=10
LOCAL_EPOCHS=5
AGGREGATION_METHOD=fedavg
MIN_CLIENTS=2

# Layer 1: Audit Artifacts
ARTIFACT_OUTPUT_DIR=artifacts

# Layer 2: Solana Attestation
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_NETWORK=devnet

# Layer 3: x402 Monetization
INFERENCE_PORT=5001
QUERY_PRICE_USDC=0.05
```

## Running the System

### Quick Demo (Recommended)

```bash
# Run the complete 3-layer demo
python test_fednet_complete.py

# Or test individual layers
python test_fednet_layer1.py          # Layer 1 only
python test_fednet_layer1_layer2.py   # Layers 1 & 2
```

### Start API Server

```bash
python -m api.app
```

### Launch Dashboard

```bash
python -c "from fednet.dashboard_server import create_dashboard; create_dashboard(port=5001).run()"
```

Visit `http://localhost:5001` to view the dashboard.

### Run Tests

```bash
pytest tests/ -v
```

## Local Federated Learning

```bash
python scripts/run_local_fl.py --rounds 10 --local-epochs 5
```

## Azure ML Setup (Optional)

### 1. Install Azure CLI

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
```

### 2. Setup Workspace

```bash
python azure_ml/setup_compute.py
```

### 3. Upload Data

```bash
python azure_ml/upload_data.py
```

### 4. Run Azure FL

```bash
python scripts/run_azure_fl.py
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'fednet'`
Make sure you installed the package with `pip install -e .` from the project root.

### `ImportError: No module named 'torch'`
Reinstall dependencies: `pip install -r requirements.txt`

### CUDA Out of Memory
Reduce `BATCH_SIZE` in your `.env` file.

### Data Not Found
Run `python scripts/generate_demo_data.py` first.

## Next Steps

- Read the [Architecture](architecture.md) documentation
- Check out the [API Documentation](api_documentation.md)
- Review example notebooks in `notebooks/`
- Read the full technical reference: [FEDNET.md](../FEDNET.md)
