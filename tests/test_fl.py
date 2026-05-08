"""Unit tests for federated learning."""

import pytest
import torch
import torch.nn as nn
from federated.aggregator import FederatedAggregator
from federated.orchestrator import FederatedOrchestrator
from models.thalassemia_models import CBCModel


def test_federated_averaging():
    """Test FedAvg aggregation."""
    aggregator = FederatedAggregator("fedavg")
    
    # Create dummy client weights
    model = CBCModel()
    weights1 = model.state_dict()
    weights2 = model.state_dict()
    
    # Aggregate
    aggregated = aggregator.aggregate(
        [weights1, weights2],
        client_data_sizes=[100, 200]
    )
    
    assert isinstance(aggregated, dict)
    assert len(aggregated) == len(weights1)


def test_orchestrator():
    """Test FL orchestrator."""
    global_model = CBCModel()
    orchestrator = FederatedOrchestrator(global_model, min_clients=2)
    
    # Create client updates
    client1_model = CBCModel()
    client2_model = CBCModel()
    
    client_weights = [
        client1_model.state_dict(),
        client2_model.state_dict()
    ]
    
    client_sizes = [100, 150]
    
    # Run round
    global_weights = orchestrator.run_round(
        client_weights,
        client_sizes,
        save_checkpoint=False
    )
    
    assert orchestrator.current_round == 1
    assert isinstance(global_weights, dict)
