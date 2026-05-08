"""Script to generate demo data for all hospitals."""

import argparse
from config.logging_config import setup_logging
from data_generation.generate_all_data import main as generate_main

logger = setup_logging(log_level="INFO")


if __name__ == "__main__":
    logger.info("Generating demo data")
    generate_main()
