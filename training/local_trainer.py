"""Local model trainer."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pathlib import Path
from typing import Optional, Dict
from tqdm import tqdm
from config.logging_config import get_logger
from models.model_utils import save_model, get_device
from .metrics import calculate_metrics

logger = get_logger(__name__)


class LocalTrainer:
    """Trainer for local model training."""
    
    def __init__(
        self,
        model: nn.Module,
        device: Optional[str] = None,
        learning_rate: float = 0.001,
        checkpoint_dir: Optional[Path] = None
    ):
        """
        Initialize local trainer.
        
        Args:
            model: PyTorch model
            device: Device (cuda/cpu)
            learning_rate: Learning rate
            checkpoint_dir: Directory to save checkpoints
        """
        self.model = model
        self.device = device if device else get_device()
        self.model.to(self.device)
        
        self.learning_rate = learning_rate
        self.checkpoint_dir = checkpoint_dir
        
        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        # Metrics
        self.history = {
            "train_loss": [],
            "train_acc": [],
            "val_loss": [],
            "val_acc": []
        }
    
    def train_epoch(self, dataloader: DataLoader) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        
        total_loss = 0.0
        all_preds = []
        all_labels = []
        
        pbar = tqdm(dataloader, desc="Training")
        
        for batch in pbar:
            # Handle different data types
            if len(batch) == 2:  # CBC or Image only
                data, labels = batch
                data = data.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(data)
            
            elif len(batch) == 3:  # Hybrid
                cbc_data, image_data, labels = batch
                cbc_data = cbc_data.to(self.device)
                image_data = image_data.to(self.device)
                labels = labels.to(self.device)
                
                # Forward pass
                outputs = self.model(cbc_data, image_data)
            
            # Calculate loss
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            # Track metrics
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({"loss": loss.item()})
        
        avg_loss = total_loss / len(dataloader)
        metrics = calculate_metrics(all_labels, all_preds)
        metrics["loss"] = avg_loss
        
        return metrics
    
    def validate(self, dataloader: DataLoader) -> Dict[str, float]:
        """Validate model."""
        self.model.eval()
        
        total_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Validating"):
                # Handle different data types
                if len(batch) == 2:
                    data, labels = batch
                    data = data.to(self.device)
                    labels = labels.to(self.device)
                    outputs = self.model(data)
                
                elif len(batch) == 3:
                    cbc_data, image_data, labels = batch
                    cbc_data = cbc_data.to(self.device)
                    image_data = image_data.to(self.device)
                    labels = labels.to(self.device)
                    outputs = self.model(cbc_data, image_data)
                
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                all_preds.extend(predicted.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        avg_loss = total_loss / len(dataloader)
        metrics = calculate_metrics(all_labels, all_preds)
        metrics["loss"] = avg_loss
        
        return metrics
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: Optional[DataLoader] = None,
        epochs: int = 10,
        save_best: bool = True
    ) -> Dict:
        """
        Train model.
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            save_best: Whether to save best model
            
        Returns:
            Training history
        """
        best_val_acc = 0.0
        
        for epoch in range(epochs):
            logger.info(f"Epoch {epoch + 1}/{epochs}")
            
            # Train
            train_metrics = self.train_epoch(train_loader)
            logger.info(f"Train Loss: {train_metrics['loss']:.4f}, "
                       f"Acc: {train_metrics['accuracy']:.4f}")
            
            self.history["train_loss"].append(train_metrics["loss"])
            self.history["train_acc"].append(train_metrics["accuracy"])
            
            # Validate
            if val_loader:
                val_metrics = self.validate(val_loader)
                logger.info(f"Val Loss: {val_metrics['loss']:.4f}, "
                           f"Acc: {val_metrics['accuracy']:.4f}")
                
                self.history["val_loss"].append(val_metrics["loss"])
                self.history["val_acc"].append(val_metrics["accuracy"])
                
                # Save best model
                if save_best and val_metrics["accuracy"] > best_val_acc:
                    best_val_acc = val_metrics["accuracy"]
                    if self.checkpoint_dir:
                        save_path = self.checkpoint_dir / "best_model.pth"
                        save_model(
                            self.model,
                            save_path,
                            epoch=epoch,
                            optimizer=self.optimizer,
                            metrics=val_metrics
                        )
        
        return self.history
    
    def get_model_weights(self) -> Dict:
        """Get model weights for federated aggregation."""
        return self.model.state_dict()
    
    def set_model_weights(self, weights: Dict):
        """Set model weights from federated aggregation."""
        self.model.load_state_dict(weights)
