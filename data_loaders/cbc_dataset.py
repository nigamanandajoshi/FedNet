"""PyTorch dataset for CBC data."""

import pandas as pd
import torch
from torch.utils.data import Dataset
from pathlib import Path
from typing import Tuple, Optional
from sklearn.preprocessing import StandardScaler


class CBCDataset(Dataset):
    """Dataset for Complete Blood Count (CBC) data."""
    
    FEATURE_COLUMNS = ["hb", "rbc", "mcv", "mch", "mchc", "rdw", "wbc", "platelets","Age"]
    LABEL_MAP = {"normal": 0, "minor": 1, "major": 2}
    LABEL_MAP = {}
    
    def __init__(
        self,
        csv_path: Path,
        scaler: Optional[StandardScaler] = None,
        fit_scaler: bool = True
    ):
        """
        Initialize CBC dataset.
        
        Args:
            csv_path: Path to CSV file
            scaler: StandardScaler instance
            fit_scaler: Whether to fit the scaler on this data
        """
        self.data = pd.read_csv(csv_path)
        
        # Extract features and labels
        self.features = self.data[self.FEATURE_COLUMNS].values
        self.labels = self.data["condition"].map(self.LABEL_MAP).values
        
        # Initialize scaler
        if scaler is None:
            self.scaler = StandardScaler()
        else:
            self.scaler = scaler
        
        # Fit or transform
        if fit_scaler:
            self.features = self.scaler.fit_transform(self.features)
        else:
            self.features = self.scaler.transform(self.features)
    
    def __len__(self) -> int:
        """Get dataset length."""
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get item by index.
        
        Returns:
            Tuple of (features, label)
        """
        features = torch.FloatTensor(self.features[idx])
        label = torch.LongTensor([self.labels[idx]])[0]
        
        return features, label
    
    def get_scaler(self) -> StandardScaler:
        """Get the fitted scaler."""
        return self.scaler


def create_cbc_dataloader(
    csv_path: Path,
    batch_size: int = 32,
    shuffle: bool = True,
    num_workers: int = 4,
    scaler: Optional[StandardScaler] = None,
    fit_scaler: bool = True
) -> torch.utils.data.DataLoader:
    """
    Create CBC data loader.
    
    Args:
        csv_path: Path to CSV file
        batch_size: Batch size
        shuffle: Whether to shuffle
        num_workers: Number of workers
        scaler: StandardScaler instance
        fit_scaler: Whether to fit scaler
        
    Returns:
        DataLoader instance
    """
    dataset = CBCDataset(csv_path, scaler=scaler, fit_scaler=fit_scaler)
    
    dataloader = torch.utils.data.DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return dataloader
