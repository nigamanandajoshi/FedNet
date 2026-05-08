"""Generate all synthetic data for hospitals and test sets."""

import argparse
from pathlib import Path
from thalassemia_data_generator import generate_hospital_data
from config.settings import settings
from config.logging_config import setup_logging

logger = setup_logging(log_level="INFO")


def main():
    """Generate all datasets."""
    parser = argparse.ArgumentParser(description="Generate synthetic thalassemia data")
    parser.add_argument("--n-samples", type=int, default=1000, help="Samples per hospital")
    parser.add_argument("--test-samples", type=int, default=300, help="Test samples")
    args = parser.parse_args()
    
    data_dir = settings.data_dir
    
    # Generate hospital data
    hospitals = ["italy", "pakistan", "usa"]
    for hospital in hospitals:
        logger.info(f"Generating data for hospital: {hospital}")
        hospital_dir = data_dir / f"hospital_{hospital}"
        generate_hospital_data(hospital, args.n_samples, hospital_dir)
    
    # Generate test data
    logger.info("Generating test data")
    test_dir = data_dir / "test"
    generate_hospital_data("test", args.test_samples, test_dir, seed=9999)
    
    logger.info("Data generation complete!")


if __name__ == "__main__":
    main()
