"""PyTorch dataset for blood smear images."""

import torch
from torch.utils.data import Dataset
from pathlib import Path
from PIL import Image
from typing import Tuple, Optional, Callable
import albumentations as A
from albumentations.pytorch import ToTensorV2


class ImageDataset(Dataset):
    """Dataset for blood smear images."""
    
    LABEL_MAP = {"normal": 0, "minor": 1, "major": 2}
    
    def __init__(
        self,
        image_dir: Path,
        transform: Optional[Callable] = None,
        image_size: int = 224
    ):
        """
        Initialize Image dataset.
        
        Args:
            image_dir: Directory containing images organized by class
            transform: Image transformations
            image_size: Target image size
        """
        self.image_dir = Path(image_dir)
        self.transform = transform
        
        # If no transform provided, use default
        if self.transform is None:
            self.transform = self.get_default_transform(image_size)
        
        # Collect image paths and labels
        self.samples = []
        for label_name, label_idx in self.LABEL_MAP.items():
            label_dir = self.image_dir / label_name
            if label_dir.exists():
                for img_path in label_dir.glob("*.png"):
                    self.samples.append((img_path, label_idx))
                for img_path in label_dir.glob("*.jpg"):
                    self.samples.append((img_path, label_idx))
    
    @staticmethod
    def get_default_transform(image_size: int = 224, training: bool = True):
        """Get default image transformations."""
        if training:
            transform = A.Compose([
                A.Resize(image_size, image_size),
                A.HorizontalFlip(p=0.5),
                A.RandomRotate90(p=0.5),
                A.ShiftScaleRotate(shift_limit=0.1, scale_limit=0.1, rotate_limit=15, p=0.5),
                A.OneOf([
                    A.GaussNoise(p=1.0),
                    A.GaussianBlur(p=1.0),
                ], p=0.3),
                A.OneOf([
                    A.RandomBrightnessContrast(p=1.0),
                    A.HueSaturationValue(p=1.0),
                ], p=0.3),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2(),
            ])
        else:
            transform = A.Compose([
                A.Resize(image_size, image_size),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2(),
            ])
        
        return transform
    
    def __len__(self) -> int:
        """Get dataset length."""
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get item by index.
        
        Returns:
            Tuple of (image, label)
        """
        img_path, label = self.samples[idx]
        
        # Load image
        image = Image.open(img_path).convert("RGB")
        image = np.array(image)
        
        # Apply transformations
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented["image"]
        
        label = torch.LongTensor([label])[0]
        
        return image, label


import numpy as np


def create_image_dataloader(
    image_dir: Path,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    image_size: int = 224,
    training: bool = True
) -> torch.utils.data.DataLoader:
    """
    Create image data loader.
    
    Args:
        image_dir: Directory containing images
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of workers
        image_size: Target image size
        training: Whether training mode (affects augmentation)
        
    Returns:
        DataLoader instance
    """
    transform = ImageDataset.get_default_transform(image_size, training)
    dataset = ImageDataset(image_dir, transform=transform, image_size=image_size)
    
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return dataloader
