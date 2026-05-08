#!/bin/bash

# Azure deployment script for FedNet

set -e

echo "FedNet Azure Deployment"
echo "============================"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Please install it first."
    exit 1
fi

# Login to Azure
echo "Logging in to Azure..."
az login

# Set subscription
if [ -n "$AZURE_SUBSCRIPTION_ID" ]; then
    az account set --subscription "$AZURE_SUBSCRIPTION_ID"
fi

# Create resource group
echo "Creating resource group..."
az group create \
    --name "${AZURE_RESOURCE_GROUP:-fednet-rg}" \
    --location "${AZURE_LOCATION:-eastus}"

# Setup Azure ML workspace
echo "Setting up Azure ML workspace..."
python azure_ml/setup_compute.py

# Upload data
echo "Uploading data to Azure..."
python azure_ml/upload_data.py

# Deploy pipeline
echo "Deploying FL pipeline..."
python azure_ml/pipeline.py

echo "Deployment complete!"
echo "Check Azure Portal for details: https://portal.azure.com"
