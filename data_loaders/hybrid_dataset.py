"""PyTorch dataset for hybrid CBC + image data."""

import pandas as pd
import torch
from torch.utils.data import Dataset
from pathlib import Path
from PIL import Image
from typing import Tuple, Optional, Callable
import numpy as np
from sklearn.preprocessing import StandardScaler
import albumentations as A
from .cbc_dataset import CBCDataset
from .image_dataset import ImageDataset


class HybridDataset(Dataset):
    """Dataset combining CBC data and blood smear images."""
    
    FEATURE_COLUMNS = ["hb", "rbc", "mcv", "mch", "mchc", "rdw", "wbc", "platelets"]
    LABEL_MAP = {"normal": 0, "minor": 1, "major": 2}
    
    def __init__(
        self,
        csv_path: Path,
        image_dir: Path,
        scaler: Optional[StandardScaler] = None,
        fit_scaler: bool = True,
        transform: Optional[Callable] = None,
        image_size: int = 224
    ):
        """
        Initialize Hybrid dataset.
        
        Args:
            csv_path: Path to CBC CSV file
            image_dir: Directory containing blood smear images
            scaler: StandardScaler for CBC features
            fit_scaler: Whether to fit scaler
            transform: Image transformations
            image_size: Target image size
        """
        # Load CBC data
        self.cbc_data = pd.read_csv(csv_path)
        
        # Extract features and labels
        self.cbc_features = self.cbc_data[self.FEATURE_COLUMNS].values
        self.labels = self.cbc_data["condition"].map(self.LABEL_MAP).values
        self.patient_ids = self.cbc_data["patient_id"].values
        
        # Initialize scaler
        if scaler is None:
            self.scaler = StandardScaler()
        else:
            self.scaler = scaler
        
        # Fit or transform
        if fit_scaler:
            self.cbc_features = self.scaler.fit_transform(self.cbc_features)
        else:
            self.cbc_features = self.scaler.transform(self.cbc_features)
        
        # Image directory
        self.image_dir = Path(image_dir)
        
        # Image transform
        if transform is None:
            self.transform = ImageDataset.get_default_transform(image_size)
        else:
            self.transform = transform
    
    def __len__(self) -> int:
        """Get dataset length."""
        return len(self.cbc_data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Get item by index.
        
        Returns:
            Tuple of (cbc_features, image, label)
        """
        # Get CBC features
        cbc_features = torch.FloatTensor(self.cbc_features[idx])
        
        # Get label
        label = torch.LongTensor([self.labels[idx]])[0]
        
        # Get patient ID and find corresponding image
        patient_id = self.patient_ids[idx]
        condition = list(self.LABEL_MAP.keys())[self.labels[idx]]
        
        # Try to find image for this patient
        image_path = self.image_dir / condition / f"{patient_id}.png"
        if not image_path.exists():
            image_path = self.image_dir / condition / f"{patient_id}.jpg"
        
        # If still doesn't exist, use a placeholder or random image from same class
        if not image_path.exists():
            # Find any image from the same class
            class_dir = self.image_dir / condition
            if class_dir.exists():
                available_images = list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpg"))
                if available_images:
                    image_path = available_images[0]
        
        # Load and transform image
        if image_path.exists():
            image = Image.open(image_path).convert("RGB")
            image = np.array(image)
            
            if self.transform:
                augmented = self.transform(image=image)
                image = augmented["image"]
        else:
            # Create blank image if no image found
            blank_image = np.zeros((224, 224, 3), dtype=np.uint8)
            augmented = self.transform(image=blank_image)
            image = augmented["image"]
        
        return cbc_features, image, label
    
    def get_scaler(self) -> StandardScaler:
        """Get the fitted scaler."""
        return self.scaler


def create_hybrid_dataloader(
    csv_path: Path,
    image_dir: Path,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    scaler: Optional[StandardScaler] = None,
    fit_scaler: bool = True,
    image_size: int = 224,
    training: bool = True
) -> torch.utils.data.DataLoader:
    """
    Create hybrid data loader.
    
    Args:
        csv_path: Path to CBC CSV file
        image_dir: Directory containing images
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of workers
        scaler: StandardScaler instance
        fit_scaler: Whether to fit scaler
        image_size: Target image size
        training: Whether training mode
        
    Returns:
        DataLoader instance
    """
    transform = ImageDataset.get_default_transform(image_size, training)
    dataset = HybridDataset(
        csv_path,
        image_dir,
        scaler=scaler,
        fit_scaler=fit_scaler,
        transform=transform,
        image_size=image_size
    )
    
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return dataloader
