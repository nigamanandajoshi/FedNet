"""Federated aggregation strategies."""

import torch
import numpy as np
from typing import List, Dict
from config.logging_config import get_logger

logger = get_logger(__name__)


class FederatedAggregator:
    """Federated learning model aggregator."""
    
    def __init__(self, aggregation_method: str = "fedavg"):
        """
        Initialize aggregator.
        
        Args:
            aggregation_method: Aggregation method (fedavg, fedprox, weighted)
        """
        self.aggregation_method = aggregation_method
        logger.info(f"Initialized aggregator with method: {aggregation_method}")
    
    def federated_averaging(
        self,
        client_weights: List[Dict],
        client_data_sizes: List[int]
    ) -> Dict:
        """
        Federated averaging (FedAvg) aggregation.
        
        Args:
            client_weights: List of client model weights
            client_data_sizes: List of dataset sizes for each client
            
        Returns:
            Aggregated model weights
        """
        total_size = sum(client_data_sizes)
        
        # Initialize aggregated weights with zeros
        aggregated_weights = {}
        
        # Get the structure from first client
        for key in client_weights[0].keys():
            aggregated_weights[key] = torch.zeros_like(client_weights[0][key])
        
        # Weighted average
        for client_weight, data_size in zip(client_weights, client_data_sizes):
            weight = data_size / total_size
            
            for key in aggregated_weights.keys():
                aggregated_weights[key] += client_weight[key] * weight
        
        logger.info(f"Aggregated {len(client_weights)} client models using FedAvg")
        
        return aggregated_weights
    
    def weighted_aggregation(
        self,
        client_weights: List[Dict],
        weights: List[float]
    ) -> Dict:
        """
        Custom weighted aggregation.
        
        Args:
            client_weights: List of client model weights
            weights: Custom weights for each client
            
        Returns:
            Aggregated model weights
        """
        # Normalize weights
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # Initialize aggregated weights
        aggregated_weights = {}
        for key in client_weights[0].keys():
            aggregated_weights[key] = torch.zeros_like(client_weights[0][key])
        
        # Weighted average
        for client_weight, weight in zip(client_weights, normalized_weights):
            for key in aggregated_weights.keys():
                aggregated_weights[key] += client_weight[key] * weight
        
        logger.info(f"Aggregated {len(client_weights)} client models with custom weights")
        
        return aggregated_weights
    
    def aggregate(
        self,
        client_weights: List[Dict],
        client_data_sizes: List[int] = None,
        custom_weights: List[float] = None
    ) -> Dict:
        """
        Aggregate client models.
        
        Args:
            client_weights: List of client model weights
            client_data_sizes: Dataset sizes (for FedAvg)
            custom_weights: Custom weights (for weighted aggregation)
            
        Returns:
            Aggregated model weights
        """
        if self.aggregation_method == "fedavg":
            if client_data_sizes is None:
                # Equal weights if no data sizes provided
                client_data_sizes = [1] * len(client_weights)
            return self.federated_averaging(client_weights, client_data_sizes)
        
        elif self.aggregation_method == "weighted":
            if custom_weights is None:
                custom_weights = [1.0] * len(client_weights)
            return self.weighted_aggregation(client_weights, custom_weights)
        
        else:
            raise ValueError(f"Unknown aggregation method: {self.aggregation_method}")
    
    def compute_model_diff(
        self,
        old_weights: Dict,
        new_weights: Dict
    ) -> float:
        """
        Compute L2 norm of model weight difference.
        
        Args:
            old_weights: Old model weights
            new_weights: New model weights
            
        Returns:
            L2 norm of difference
        """
        diff_norm = 0.0
        
        for key in old_weights.keys():
            diff = new_weights[key] - old_weights[key]
            diff_norm += torch.norm(diff).item() ** 2
        
        diff_norm = np.sqrt(diff_norm)
        
        return diff_norm
