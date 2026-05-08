"""Script to run Azure ML federated learning."""

import argparse
from config.logging_config import setup_logging
from azure_ml.setup_compute import get_or_create_workspace
from azure_ml.pipeline import create_fl_pipeline, run_pipeline

logger = setup_logging(log_level="INFO")


def main():
    """Run Azure ML FL pipeline."""
    parser = argparse.ArgumentParser(description="Run Azure FL pipeline")
    parser.add_argument("--experiment", type=str, default="thalassemia_fl", help="Experiment name")
    args = parser.parse_args()
    
    logger.info("Starting Azure ML federated learning")
    
    # Get workspace
    ws = get_or_create_workspace()
    
    # Create pipeline
    pipeline = create_fl_pipeline(ws)
    
    if pipeline:
        # Run pipeline
        run = run_pipeline(ws, pipeline, args.experiment)
        run.wait_for_completion(show_output=True)
        
        logger.info("Azure FL pipeline completed")
    else:
        logger.warning("Pipeline not created - implement pipeline logic first")


if __name__ == "__main__":
    main()
