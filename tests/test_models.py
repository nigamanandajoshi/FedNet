"""Unit tests for models."""

import pytest
import torch
from models.thalassemia_models import CBCModel, ImageModel, HybridModel, get_model


def test_cbc_model():
    """Test CBC model."""
    model = CBCModel(input_dim=8, num_classes=3)
    
    # Test forward pass
    x = torch.randn(16, 8)
    output = model(x)
    
    assert output.shape == (16, 3)


def test_image_model():
    """Test image model."""
    model = ImageModel(num_classes=3, pretrained=False)
    
    # Test forward pass
    x = torch.randn(4, 3, 224, 224)
    output = model(x)
    
    assert output.shape == (4, 3)


def test_hybrid_model():
    """Test hybrid model."""
    model = HybridModel(cbc_input_dim=8, num_classes=3, pretrained=False)
    
    # Test forward pass
    cbc_data = torch.randn(4, 8)
    image_data = torch.randn(4, 3, 224, 224)
    output = model(cbc_data, image_data)
    
    assert output.shape == (4, 3)


def test_get_model():
    """Test model factory."""
    model_cbc = get_model("cbc", num_classes=3)
    assert isinstance(model_cbc, CBCModel)
    
    model_image = get_model("image", num_classes=3, pretrained=False)
    assert isinstance(model_image, ImageModel)
    
    model_hybrid = get_model("hybrid", num_classes=3, pretrained=False)
    assert isinstance(model_hybrid, HybridModel)
