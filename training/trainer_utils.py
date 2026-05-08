"""Training utility functions."""

import torch
from typing import Dict


def get_model_size(model: torch.nn.Module) -> float:
    """
    Get model size in MB.
    
    Args:
        model: PyTorch model
        
    Returns:
        Model size in MB
    """
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()
    
    size_mb = (param_size + buffer_size) / 1024**2
    
    return size_mb


def model_to_dict(model: torch.nn.Module) -> Dict:
    """Convert model state dict to regular dict for transmission."""
    state_dict = model.state_dict()
    return {k: v.cpu().numpy().tolist() for k, v in state_dict.items()}


def dict_to_model(model: torch.nn.Module, weights_dict: Dict):
    """Load weights from dict into model."""
    state_dict = {k: torch.tensor(v) for k, v in weights_dict.items()}
    model.load_state_dict(state_dict)
