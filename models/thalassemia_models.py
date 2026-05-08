"""Thalassemia detection models - CBC, Image, and Hybrid architectures."""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict


class CBCModel(nn.Module):
    """Neural network for CBC-based thalassemia detection."""
    
    def __init__(self, input_dim: int = 8, hidden_dims: list = [64, 32], num_classes: int = 3):
        """
        Initialize CBC model.
        
        Args:
            input_dim: Number of CBC features
            hidden_dims: List of hidden layer dimensions
            num_classes: Number of output classes
        """
        super(CBCModel, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.3)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        
        self.model = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.model(x)


class ImageModel(nn.Module):
    """CNN for blood smear image-based thalassemia detection."""
    
    def __init__(self, num_classes: int = 3, pretrained: bool = True):
        """
        Initialize Image model.
        
        Args:
            num_classes: Number of output classes
            pretrained: Use pretrained weights
        """
        super(ImageModel, self).__init__()
        
        # Use ResNet18 as backbone
        self.backbone = models.resnet18(pretrained=pretrained)
        
        # Replace final layer
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, num_classes)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        return self.backbone(x)


class HybridModel(nn.Module):
    """Hybrid model combining CBC data and blood smear images."""
    
    def __init__(
        self,
        cbc_input_dim: int = 8,
        cbc_hidden_dims: list = [64, 32],
        num_classes: int = 3,
        pretrained: bool = True
    ):
        """
        Initialize Hybrid model.
        
        Args:
            cbc_input_dim: Number of CBC features
            cbc_hidden_dims: Hidden dimensions for CBC branch
            num_classes: Number of output classes
            pretrained: Use pretrained weights for image branch
        """
        super(HybridModel, self).__init__()
        
        # CBC branch
        self.cbc_branch = CBCModel(
            input_dim=cbc_input_dim,
            hidden_dims=cbc_hidden_dims,
            num_classes=128  # Output features for fusion
        )
        # Remove last layer to get features
        self.cbc_branch = nn.Sequential(*list(self.cbc_branch.model.children())[:-1])
        
        # Image branch
        self.image_branch = models.resnet18(pretrained=pretrained)
        in_features = self.image_branch.fc.in_features
        self.image_branch.fc = nn.Linear(in_features, 128)  # Output features for fusion
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(256, 128),  # 128 from CBC + 128 from image
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, cbc_data: torch.Tensor, image_data: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            cbc_data: CBC features (batch_size, cbc_input_dim)
            image_data: Blood smear images (batch_size, 3, H, W)
            
        Returns:
            Class logits (batch_size, num_classes)
        """
        cbc_features = self.cbc_branch(cbc_data)
        image_features = self.image_branch(image_data)
        
        # Concatenate features
        combined = torch.cat([cbc_features, image_features], dim=1)
        
        # Fusion and classification
        output = self.fusion(combined)
        
        return output


def get_model(model_type: str, **kwargs) -> nn.Module:
    """
    Factory function to get model by type.
    
    Args:
        model_type: One of 'cbc', 'image', 'hybrid'
        **kwargs: Model-specific arguments
        
    Returns:
        Model instance
    """
    models_dict = {
        "cbc": CBCModel,
        "image": ImageModel,
        "hybrid": HybridModel,
    }
    
    if model_type not in models_dict:
        raise ValueError(f"Unknown model type: {model_type}")
    
    return models_dict[model_type](**kwargs)
