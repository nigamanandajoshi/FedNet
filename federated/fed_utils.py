"""Federated learning utilities."""

import torch
from typing import Dict, List


def compare_models(model1: torch.nn.Module, model2: torch.nn.Module) -> bool:
    """
    Compare if two models have the same weights.
    
    Args:
        model1: First model
        model2: Second model
        
    Returns:
        True if models are identical
    """
    for p1, p2 in zip(model1.parameters(), model2.parameters()):
        if not torch.equal(p1, p2):
            return False
    return True


def clip_gradients(model: torch.nn.Module, max_norm: float = 1.0):
    """
    Clip model gradients for privacy.
    
    Args:
        model: PyTorch model
        max_norm: Maximum gradient norm
    """
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)


def add_noise_to_weights(
    weights: Dict,
    noise_scale: float = 0.01,
    device: str = "cpu"
) -> Dict:
    """
    Add Gaussian noise to model weights for differential privacy.
    
    Args:
        weights: Model weights
        noise_scale: Scale of Gaussian noise
        device: Device
        
    Returns:
        Noisy weights
    """
    noisy_weights = {}
    
    for key, value in weights.items():
        noise = torch.randn_like(value) * noise_scale
        noisy_weights[key] = value + noise.to(device)
    
    return noisy_weights
