"""Script to run local federated learning simulation."""

import torch
from pathlib import Path
import argparse
from config.settings import settings
from config.logging_config import setup_logging
from models.thalassemia_models import get_model
from data_loaders.cbc_dataset import create_cbc_dataloader
from training.local_trainer import LocalTrainer
from federated.orchestrator import FederatedOrchestrator
from blockchain.ledger import BlockchainLedger

logger = setup_logging(log_level=settings.log_level, log_dir=settings.logs_dir)


def train_hospital_client(
    hospital_name: str,
    global_weights: dict,
    local_epochs: int = 5
) -> tuple:
    """
    Train a hospital client locally.
    
    Args:
        hospital_name: Hospital name
        global_weights: Global model weights
        local_epochs: Number of local epochs
        
    Returns:
        Tuple of (weights, data_size, metrics)
    """
    logger.info(f"Training client: {hospital_name}")
    
    # Load data
    data_path = settings.data_dir / f"hospital_{hospital_name}" / "cbc_data.csv"
    
    if not data_path.exists():
        logger.warning(f"Data not found for {hospital_name}")
        return None, 0, {}
    
    train_loader = create_cbc_dataloader(
        data_path,
        batch_size=settings.batch_size,
        num_workers=settings.num_workers
    )
    
    # Create model and load global weights
    model = get_model("cbc", num_classes=settings.num_classes)
    model.load_state_dict(global_weights)
    
    # Train locally
    trainer = LocalTrainer(model, learning_rate=settings.learning_rate)
    trainer.train(train_loader, epochs=local_epochs, save_best=False)
    
    # Get results
    weights = trainer.get_model_weights()
    data_size = len(train_loader.dataset)
    metrics = trainer.history
    
    final_metrics = {
        'loss': metrics['train_loss'][-1] if metrics['train_loss'] else 0,
        'accuracy': metrics['train_acc'][-1] if metrics['train_acc'] else 0
    }
    
    return weights, data_size, final_metrics


def main():
    """Run federated learning simulation."""
    parser = argparse.ArgumentParser(description="Run local FL simulation")
    parser.add_argument("--rounds", type=int, default=None, help="FL rounds")
    parser.add_argument("--local-epochs", type=int, default=None, help="Local epochs")
    args = parser.parse_args()
    
    fl_rounds = args.rounds or settings.fl_rounds
    local_epochs = args.local_epochs or settings.local_epochs
    
    logger.info("=" * 60)
    logger.info("FedNet: Local Federated Learning Simulation")
    logger.info("=" * 60)
    
    # Initialize global model
    global_model = get_model("cbc", num_classes=settings.num_classes)
    
    # Initialize orchestrator
    orchestrator = FederatedOrchestrator(
        global_model,
        aggregation_method=settings.aggregation_method,
        min_clients=settings.min_clients
    )
    
    # Initialize blockchain
    blockchain = BlockchainLedger()
    
    # Federated learning rounds
    for round_num in range(fl_rounds):
        logger.info(f"\n{'='*60}")
        logger.info(f"Federated Learning Round {round_num + 1}/{fl_rounds}")
        logger.info(f"{'='*60}\n")
        
        # Get global weights
        global_weights = orchestrator.get_global_weights()
        
        # Train each hospital client
        client_weights = []
        client_sizes = []
        client_metrics = []
        
        for hospital in settings.hospitals:
            weights, size, metrics = train_hospital_client(
                hospital,
                global_weights,
                local_epochs
            )
            
            if weights is not None:
                client_weights.append(weights)
                client_sizes.append(size)
                client_metrics.append(metrics)
                
                # Record on blockchain
                blockchain.record_client_update(
                    round_num + 1,
                    f"hospital_{hospital}",
                    size,
                    metrics
                )
        
        # Aggregate
        if len(client_weights) >= settings.min_clients:
            global_weights = orchestrator.run_round(
                client_weights,
                client_sizes,
                client_metrics
            )
            
            # Record on blockchain
            avg_metrics = orchestrator.history['global_metrics'][-1]
            blockchain.record_fl_round(
                round_num + 1,
                len(client_weights),
                avg_metrics
            )
        else:
            logger.warning(f"Not enough clients in round {round_num + 1}")
    
    # Save final model
    final_model_path = settings.models_dir / "final_global_model.pth"
    torch.save(global_model.state_dict(), final_model_path)
    logger.info(f"Saved final model to {final_model_path}")
    
    # Save blockchain
    blockchain_path = settings.project_root / "blockchain_ledger.json"
    blockchain.save_to_file(str(blockchain_path))
    
    logger.info("\nFederated learning complete!")
    logger.info(f"Total rounds: {fl_rounds}")
    logger.info(f"Blockchain validation: {blockchain.is_valid()}")


if __name__ == "__main__":
    main()
