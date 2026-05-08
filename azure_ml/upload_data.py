"""Upload data to Azure ML."""

from azureml.core import Workspace, Dataset, Datastore
from pathlib import Path
from config.azure_config import azure_config
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


def upload_hospital_data(ws: Workspace, hospital_name: str):
    """
    Upload hospital data to Azure ML.
    
    Args:
        ws: Azure ML workspace
        hospital_name: Hospital name (italy, pakistan, usa)
    """
    # Get default datastore
    datastore = ws.get_default_datastore()
    
    # Local data path
    local_path = settings.data_dir / f"hospital_{hospital_name}"
    
    if not local_path.exists():
        logger.warning(f"Data not found: {local_path}")
        return
    
    # Upload to datastore
    target_path = f"hospitals/{hospital_name}"
    
    logger.info(f"Uploading {hospital_name} data to Azure ML...")
    datastore.upload(
        src_dir=str(local_path),
        target_path=target_path,
        overwrite=True,
        show_progress=True
    )
    
    # Create dataset
    dataset_name = f"hospital_{hospital_name}_data"
    dataset = Dataset.File.from_files(path=(datastore, target_path))
    
    dataset.register(
        workspace=ws,
        name=dataset_name,
        description=f"CBC and blood smear data from {hospital_name}",
        create_new_version=True
    )
    
    logger.info(f"Registered dataset: {dataset_name}")


def upload_all_data(ws: Workspace):
    """Upload all hospital data."""
    for hospital in settings.hospitals:
        upload_hospital_data(ws, hospital)
    
    logger.info("All data uploaded successfully")


def main():
    """Main upload function."""
    from .setup_compute import get_or_create_workspace
    
    ws = get_or_create_workspace()
    upload_all_data(ws)


if __name__ == "__main__":
    main()
