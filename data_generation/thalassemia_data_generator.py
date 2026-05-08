"""Synthetic thalassemia CBC data generator.

This module generates realistic Complete Blood Count (CBC) data for normal individuals
and patients with thalassemia minor and major.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple
from config.logging_config import get_logger

logger = get_logger(__name__)


class ThalassemiaDataGenerator:
    """Generate synthetic CBC data for thalassemia detection."""
    
    # Normal ranges and thalassemia characteristics
    CBC_PARAMETERS = {
        "normal": {
            "hb": (12.0, 16.0, 0.5),         # Hemoglobin (g/dL)
            "rbc": (4.5, 5.5, 0.2),           # RBC count (million/µL)
            "mcv": (80, 100, 3),              # Mean Corpuscular Volume (fL)
            "mch": (27, 31, 1),               # Mean Corpuscular Hemoglobin (pg)
            "mchc": (32, 36, 1),              # MCHC (g/dL)
            "rdw": (11.5, 14.5, 0.5),         # RBC Distribution Width (%)
            "wbc": (4.0, 11.0, 1.0),          # WBC count (thousand/µL)
            "platelets": (150, 400, 30),      # Platelet count (thousand/µL)
        },
        "minor": {
            "hb": (10.0, 12.0, 0.5),
            "rbc": (5.0, 6.5, 0.2),
            "mcv": (55, 75, 3),
            "mch": (20, 26, 1),
            "mchc": (30, 34, 1),
            "rdw": (13.0, 18.0, 0.8),
            "wbc": (4.0, 11.0, 1.0),
            "platelets": (150, 400, 30),
        },
        "major": {
            "hb": (6.0, 10.0, 0.5),
            "rbc": (2.5, 4.0, 0.2),
            "mcv": (50, 70, 3),
            "mch": (18, 24, 1),
            "mchc": (28, 32, 1),
            "rdw": (15.0, 25.0, 1.2),
            "wbc": (3.5, 15.0, 1.5),
            "platelets": (100, 350, 40),
        }
    }
    
    def __init__(self, seed: int = 42):
        """Initialize the data generator."""
        self.seed = seed
        np.random.seed(seed)
        
    def generate_sample(self, condition: str) -> Dict[str, float]:
        """Generate a single CBC sample."""
        if condition not in self.CBC_PARAMETERS:
            raise ValueError(f"Unknown condition: {condition}")
        
        params = self.CBC_PARAMETERS[condition]
        sample = {}
        
        for param_name, (min_val, max_val, std) in params.items():
            mean = (min_val + max_val) / 2
            value = np.random.normal(mean, std)
            value = np.clip(value, min_val - std, max_val + std)
            sample[param_name] = round(float(value), 2)
        
        return sample
    
    def generate_dataset(
        self,
        n_samples: int,
        distribution: Dict[str, float] = None
    ) -> pd.DataFrame:
        """
        Generate a complete dataset.
        
        Args:
            n_samples: Total number of samples
            distribution: Distribution of conditions (e.g., {"normal": 0.6, "minor": 0.3, "major": 0.1})
        """
        if distribution is None:
            distribution = {"normal": 0.6, "minor": 0.3, "major": 0.1}
        
        # Calculate samples per condition
        samples_per_condition = {
            condition: int(n_samples * ratio)
            for condition, ratio in distribution.items()
        }
        
        # Adjust for rounding errors
        total = sum(samples_per_condition.values())
        samples_per_condition["normal"] += n_samples - total
        
        # Generate samples
        data = []
        patient_id = 1
        
        for condition, n in samples_per_condition.items():
            logger.info(f"Generating {n} samples for {condition}")
            
            for _ in range(n):
                sample = self.generate_sample(condition)
                sample["patient_id"] = f"P{patient_id:05d}"
                sample["condition"] = condition
                sample["age"] = np.random.randint(1, 80)
                sample["gender"] = np.random.choice(["M", "F"])
                data.append(sample)
                patient_id += 1
        
        df = pd.DataFrame(data)
        
        # Shuffle
        df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
        
        return df
    
    def save_dataset(self, df: pd.DataFrame, output_path: Path):
        """Save dataset to CSV."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved dataset to {output_path} ({len(df)} samples)")


def generate_hospital_data(
    hospital_name: str,
    n_samples: int,
    output_dir: Path,
    seed: int = None
) -> pd.DataFrame:
    """Generate data for a specific hospital."""
    if seed is None:
        seed = hash(hospital_name) % 10000
    
    generator = ThalassemiaDataGenerator(seed=seed)
    
    # Different distributions for different hospitals
    distributions = {
        "italy": {"normal": 0.7, "minor": 0.25, "major": 0.05},
        "pakistan": {"normal": 0.5, "minor": 0.35, "major": 0.15},
        "usa": {"normal": 0.75, "minor": 0.20, "major": 0.05},
    }
    
    distribution = distributions.get(hospital_name.lower(), {"normal": 0.6, "minor": 0.3, "major": 0.1})
    
    df = generator.generate_dataset(n_samples, distribution)
    generator.save_dataset(df, output_dir / f"cbc_data.csv")
    
    return df
