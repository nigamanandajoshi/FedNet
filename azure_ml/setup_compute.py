"""Azure ML compute setup."""

from azureml.core import Workspace, ComputeTarget
from azureml.core.compute import AmlCompute, ComputeTarget
from azureml.core.compute_target import ComputeTargetException
from config.azure_config import azure_config
from config.logging_config import get_logger

logger = get_logger(__name__)


def get_or_create_workspace() -> Workspace:
    """Get or create Azure ML workspace."""
    try:
        ws = Workspace.get(
            name=azure_config.workspace_name,
            subscription_id=azure_config.subscription_id,
            resource_group=azure_config.resource_group
        )
        logger.info(f"Found existing workspace: {ws.name}")
    except Exception as e:
        logger.info(f"Creating new workspace: {azure_config.workspace_name}")
        ws = Workspace.create(
            name=azure_config.workspace_name,
            subscription_id=azure_config.subscription_id,
            resource_group=azure_config.resource_group,
            location=azure_config.location,
            create_resource_group=True
        )
    
    return ws


def setup_compute_cluster(ws: Workspace) -> ComputeTarget:
    """
    Create or get existing compute cluster.
    
    Args:
        ws: Azure ML workspace
        
    Returns:
        Compute target
    """
    try:
        compute_target = ComputeTarget(workspace=ws, name=azure_config.compute_name)
        logger.info(f"Found existing compute: {azure_config.compute_name}")
    except ComputeTargetException:
        logger.info(f"Creating new compute: {azure_config.compute_name}")
        
        compute_config = AmlCompute.provisioning_configuration(
            vm_size=azure_config.vm_size,
            min_nodes=azure_config.min_nodes,
            max_nodes=azure_config.max_nodes,
            idle_seconds_before_scaledown=300
        )
        
        compute_target = ComputeTarget.create(
            ws,
            azure_config.compute_name,
            compute_config
        )
        
        compute_target.wait_for_completion(show_output=True)
    
    return compute_target


def main():
    """Main setup function."""
    logger.info("Setting up Azure ML environment")
    
    # Get workspace
    ws = get_or_create_workspace()
    
    # Setup compute
    compute_target = setup_compute_cluster(ws)
    
    logger.info("Azure ML setup complete!")
    logger.info(f"Workspace: {ws.name}")
    logger.info(f"Compute: {compute_target.name}")


if __name__ == "__main__":
    main()
