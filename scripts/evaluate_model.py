"""Script to evaluate trained model."""

import torch
import argparse
from pathlib import Path
from config.settings import settings
from config.logging_config import setup_logging
from models.thalassemia_models import get_model
from models.model_utils import load_model
from data_loaders.cbc_dataset import create_cbc_dataloader
from training.local_trainer import LocalTrainer
from training.metrics import get_classification_report, calculate_confusion_matrix

logger = setup_logging(log_level="INFO")


def main():
    """Evaluate model on test set."""
    parser = argparse.ArgumentParser(description="Evaluate model")
    parser.add_argument("--model-path", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--model-type", type=str, default="cbc", help="Model type")
    args = parser.parse_args()
    
    logger.info("Evaluating model")
    
    # Load test data
    test_path = settings.data_dir / "test" / "cbc_data.csv"
    test_loader = create_cbc_dataloader(
        test_path,
        batch_size=settings.batch_size,
        shuffle=False,
        num_workers=settings.num_workers
    )
    
    # Load model
    model = get_model(args.model_type, num_classes=settings.num_classes)
    checkpoint = load_model(model, Path(args.model_path))
    
    # Evaluate
    trainer = LocalTrainer(model)
    metrics = trainer.validate(test_loader)
    
    logger.info("\nEvaluation Results:")
    logger.info(f"Loss: {metrics['loss']:.4f}")
    logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall: {metrics['recall']:.4f}")
    logger.info(f"F1 Score: {metrics['f1']:.4f}")


if __name__ == "__main__":
    main()
