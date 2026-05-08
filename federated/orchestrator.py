"""Federated learning orchestrator."""

import torch
from pathlib import Path
from typing import List, Dict, Optional
from config.logging_config import get_logger
from config.settings import settings
from .aggregator import FederatedAggregator
from models.model_utils import save_model

logger = get_logger(__name__)


class FederatedOrchestrator:
    """Orchestrates federated learning across multiple clients."""
    
    def __init__(
        self,
        global_model: torch.nn.Module,
        aggregation_method: str = "fedavg",
        min_clients: int = 2,
        checkpoint_dir: Optional[Path] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            global_model: Global model
            aggregation_method: Aggregation method
            min_clients: Minimum number of clients
            checkpoint_dir: Directory to save checkpoints
        """
        self.global_model = global_model
        self.aggregator = FederatedAggregator(aggregation_method)
        self.min_clients = min_clients
        self.checkpoint_dir = checkpoint_dir or settings.checkpoints_dir
        
        self.current_round = 0
        self.history = {
            "rounds": [],
            "num_clients": [],
            "global_metrics": []
        }
        
        logger.info(f"Initialized FL orchestrator (min_clients={min_clients})")
    
    def get_global_weights(self) -> Dict:
        """Get current global model weights."""
        return self.global_model.state_dict()
    
    def distribute_global_model(self) -> Dict:
        """Distribute global model to clients."""
        logger.info(f"Round {self.current_round}: Distributing global model")
        return self.get_global_weights()
    
    def aggregate_client_updates(
        self,
        client_weights: List[Dict],
        client_data_sizes: List[int],
        client_metrics: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Aggregate client model updates.
        
        Args:
            client_weights: List of client model weights
            client_data_sizes: List of client dataset sizes
            client_metrics: Optional client metrics
            
        Returns:
            Aggregated weights
        """
        if len(client_weights) < self.min_clients:
            raise ValueError(
                f"Not enough clients: got {len(client_weights)}, "
                f"need at least {self.min_clients}"
            )
        
        # Aggregate
        aggregated_weights = self.aggregator.aggregate(
            client_weights,
            client_data_sizes=client_data_sizes
        )
        
        # Update global model
        old_weights = self.get_global_weights()
        self.global_model.load_state_dict(aggregated_weights)
        
        # Compute update magnitude
        diff_norm = self.aggregator.compute_model_diff(old_weights, aggregated_weights)
        logger.info(f"Round {self.current_round}: Model update L2 norm = {diff_norm:.4f}")
        
        # Update history
        self.history["rounds"].append(self.current_round)
        self.history["num_clients"].append(len(client_weights))
        
        if client_metrics:
            avg_metrics = self._average_client_metrics(client_metrics, client_data_sizes)
            self.history["global_metrics"].append(avg_metrics)
            logger.info(f"Round {self.current_round}: Avg metrics: {avg_metrics}")
        
        return aggregated_weights
    
    def _average_client_metrics(
        self,
        client_metrics: List[Dict],
        client_data_sizes: List[int]
    ) -> Dict:
        """Average client metrics weighted by data size."""
        total_size = sum(client_data_sizes)
        avg_metrics = {}
        
        # Get all metric keys
        metric_keys = client_metrics[0].keys()
        
        for key in metric_keys:
            weighted_sum = sum(
                metrics[key] * size
                for metrics, size in zip(client_metrics, client_data_sizes)
            )
            avg_metrics[key] = weighted_sum / total_size
        
        return avg_metrics
    
    def run_round(
        self,
        client_weights: List[Dict],
        client_data_sizes: List[int],
        client_metrics: Optional[List[Dict]] = None,
        save_checkpoint: bool = True
    ) -> Dict:
        """
        Run a single federated learning round.
        
        Args:
            client_weights: Client model weights
            client_data_sizes: Client dataset sizes
            client_metrics: Client metrics
            save_checkpoint: Whether to save checkpoint
            
        Returns:
            Aggregated global weights
        """
        self.current_round += 1
        
        logger.info(f"=== Federated Learning Round {self.current_round} ===")
        
        # Aggregate
        global_weights = self.aggregate_client_updates(
            client_weights,
            client_data_sizes,
            client_metrics
        )
        
        # Save checkpoint
        if save_checkpoint:
            checkpoint_path = self.checkpoint_dir / f"global_model_round_{self.current_round}.pth"
            save_model(
                self.global_model,
                checkpoint_path,
                epoch=self.current_round,
                metrics=self.history["global_metrics"][-1] if self.history["global_metrics"] else None
            )
        
        return global_weights
    
    def get_history(self) -> Dict:
        """Get training history."""
        return self.history
