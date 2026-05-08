# Azure Machine Learning Integration Guide

This directory contains scripts and configurations to run FedNet on Azure Machine Learning (Azure ML).

## Prerequisites

1.  **Azure Account**: You need an active Azure subscription.
2.  **Azure CLI**: Install the Azure CLI and log in (`az login`).
3.  **Python SDK**: The project requirements include `azureml-core` and `azureml-sdk`.

## Configuration

Configuration is managed via environment variables and the `config/azure_config.py` file.

Create a `.env` file in the project root with the following variables:

```env
# Required
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_RESOURCE_GROUP="fednet-rg"
AZURE_WORKSPACE_NAME="fednet-ws"
AZURE_LOCATION="eastus"

# Optional (Defaults available)
AZURE_COMPUTE_NAME="fednet-compute"
AZURE_VM_SIZE="Standard_NC6"  # GPU enable VM for faster training
AZURE_MIN_NODES="0"
AZURE_MAX_NODES="4"
```

## Project Structure

*   `setup_compute.py`: Sets up the Azure ML Workspace and Compute Cluster.
*   `pipeline.py`: Defines and runs the Federated Learning pipeline.
*   `upload_data.py`: Helper to upload local datasets to Azure Blob Storage.
*   `components.py`: Defines reusable Azure ML pipeline components (e.g., training steps).
*   `deploy.py`: Handles model deployment to Azure Container Instances (ACI) or Kubernetes Services (AKS).

## How to Run

### 1. Setup Environment
First, ensure that your Azure Workspace and Compute resources are ready.

```bash
python -m azure_ml.setup_compute
```

This script will:
*   Check if the Resource Group exists (or create it).
*   Check if the Workspace exists (or create it).
*   Provision the Compute Cluster (if not already existing).

### 2. Upload Data
If you have local data that needs to be accessible by the cloud training jobs:

```bash
python -m azure_ml.upload_data
```

### 3. Run Federated Learning Pipeline
Execute the main pipeline script to start the training experiment.

```bash
python -m azure_ml.pipeline
```

This will:
*   Connect to your workspace.
*   Build the pipeline steps (preprocessing, local training, aggregation).
*   Submit the experiment to Azure ML.
*   Stream logs to your console.

## Extending the Pipeline

To add custom steps (e.g., a new validation step), modify `azure_ml/pipeline.py`. Use `PythonScriptStep` to wrap your local scripts.

```python
# Example in pipeline.py
step = PythonScriptStep(
    name="train_step",
    script_name="train.py",
    arguments=["--epochs", 10],
    compute_target=compute_target,
    source_directory="."
)
```

## Monitoring

You can monitor your experiments in the [Azure Machine Learning Studio](https://ml.azure.com/).
