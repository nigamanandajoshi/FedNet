"""Model utility functions."""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Optional, Dict
from config.logging_config import get_logger

logger = get_logger(__name__)


def save_model(
    model: nn.Module,
    path: Path,
    epoch: Optional[int] = None,
    optimizer: Optional[torch.optim.Optimizer] = None,
    metrics: Optional[Dict] = None
):
    """
    Save model checkpoint.
    
    Args:
        model: PyTorch model
        path: Save path
        epoch: Current epoch
        optimizer: Optimizer state
        metrics: Training metrics
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    checkpoint = {
        "model_state_dict": model.state_dict(),
    }
    
    if epoch is not None:
        checkpoint["epoch"] = epoch
    
    if optimizer is not None:
        checkpoint["optimizer_state_dict"] = optimizer.state_dict()
    
    if metrics is not None:
        checkpoint["metrics"] = metrics
    
    torch.save(checkpoint, path)
    logger.info(f"Saved model checkpoint to {path}")


def load_model(
    model: nn.Module,
    path: Path,
    device: str = "cpu",
    load_optimizer: bool = False,
    optimizer: Optional[torch.optim.Optimizer] = None
) -> Dict:
    """
    Load model checkpoint.
    
    Args:
        model: PyTorch model
        path: Checkpoint path
        device: Device to load to
        load_optimizer: Whether to load optimizer state
        optimizer: Optimizer instance
        
    Returns:
        Checkpoint dictionary
    """
    checkpoint = torch.load(path, map_location=device)
    model.load_state_dict(checkpoint["model_state_dict"])
    
    if load_optimizer and optimizer is not None and "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    
    logger.info(f"Loaded model from {path}")
    
    return checkpoint


def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def freeze_layers(model: nn.Module, freeze_until: Optional[str] = None):
    """
    Freeze model layers.
    
    Args:
        model: PyTorch model
        freeze_until: Freeze layers until this layer name
    """
    freeze = True
    
    for name, param in model.named_parameters():
        if freeze_until and freeze_until in name:
            freeze = False
        
        param.requires_grad = not freeze
        
        if freeze:
            logger.debug(f"Frozen layer: {name}")


def get_device() -> str:
    """Get available device."""
    if torch.cuda.is_available():
        device = "cuda"
        logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        logger.info("Using CPU")
    
    return device
