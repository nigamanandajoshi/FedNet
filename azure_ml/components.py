"""Azure ML pipeline components."""

from azureml.core import Environment
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.steps import PythonScriptStep
from config.logging_config import get_logger

logger = get_logger(__name__)


def create_environment(name: str = "fednet-env") -> Environment:
    """
    Create Azure ML environment.
    
    Args:
        name: Environment name
        
    Returns:
        Environment instance
    """
    env = Environment(name=name)
    
    # Use curated environment as base
    env = Environment.from_conda_specification(
        name=name,
        file_path="environment.yml"
    )
    
    env.docker.enabled = True
    env.docker.base_image = "mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.1-cudnn8-ubuntu20.04"
    
    logger.info(f"Created environment: {name}")
    
    return env


def create_training_step(
    name: str,
    script_name: str,
    compute_target,
    environment: Environment,
    arguments: list = None
) -> PythonScriptStep:
    """
    Create a training pipeline step.
    
    Args:
        name: Step name
        script_name: Python script to run
        compute_target: Compute target
        environment: Environment
        arguments: Script arguments
        
    Returns:
        Pipeline step
    """
    run_config = RunConfiguration()
    run_config.environment = environment
    
    step = PythonScriptStep(
        name=name,
        script_name=script_name,
        arguments=arguments or [],
        compute_target=compute_target,
        runconfig=run_config,
        allow_reuse=True
    )
    
    logger.info(f"Created pipeline step: {name}")
    
    return step
