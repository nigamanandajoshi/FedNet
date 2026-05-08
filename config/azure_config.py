"""Azure Machine Learning configuration."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AzureConfig:
    """Azure ML workspace configuration."""
    
    subscription_id: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    resource_group: str = os.getenv("AZURE_RESOURCE_GROUP", "fednet-rg")
    workspace_name: str = os.getenv("AZURE_WORKSPACE_NAME", "fednet-ws")
    location: str = os.getenv("AZURE_LOCATION", "eastus")
    
    # Compute configuration
    compute_name: str = os.getenv("AZURE_COMPUTE_NAME", "fednet-compute")
    vm_size: str = os.getenv("AZURE_VM_SIZE", "Standard_NC6")
    min_nodes: int = int(os.getenv("AZURE_MIN_NODES", "0"))
    max_nodes: int = int(os.getenv("AZURE_MAX_NODES", "4"))
    
    # Storage configuration
    storage_account_name: str = os.getenv("AZURE_STORAGE_ACCOUNT", "fednetflstorage")
    container_name: str = os.getenv("AZURE_CONTAINER_NAME", "datasets")
    
    # Datastore configuration
    datastore_name: str = os.getenv("AZURE_DATASTORE_NAME", "fednet_datastore")
    
    # Experiment configuration
    experiment_name: str = os.getenv("AZURE_EXPERIMENT_NAME", "thalassemia_fl")
    
    # Authentication
    tenant_id: Optional[str] = os.getenv("AZURE_TENANT_ID")
    client_id: Optional[str] = os.getenv("AZURE_CLIENT_ID")
    client_secret: Optional[str] = os.getenv("AZURE_CLIENT_SECRET")
    
    def validate(self) -> bool:
        """Validate required configuration."""
        required_fields = [
            self.subscription_id,
            self.resource_group,
            self.workspace_name,
        ]
        return all(required_fields)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "subscription_id": self.subscription_id,
            "resource_group": self.resource_group,
            "workspace_name": self.workspace_name,
            "location": self.location,
        }


# Global instance
azure_config = AzureConfig()
