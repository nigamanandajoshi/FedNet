"""Training package for FedNet."""

from .local_trainer import LocalTrainer
from .metrics import calculate_metrics

__all__ = ["LocalTrainer", "calculate_metrics"]
