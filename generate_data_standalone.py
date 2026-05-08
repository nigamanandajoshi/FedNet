"""Standalone data generator - no external dependencies needed."""

import numpy as np
import pandas as pd
from pathlib import Path

# Normal ranges and thalassemia characteristics
CBC_PARAMETERS = {
    "normal": {
        "hb": (12.0, 16.0, 0.5),
        "rbc": (4.5, 5.5, 0.2),
        "mcv": (80, 100, 3),
        "mch": (27, 31, 1),
        "mchc": (32, 36, 1),
        "rdw": (11.5, 14.5, 0.5),
        "wbc": (4.0, 11.0, 1.0),
        "platelets": (150, 400, 30),
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

def generate_sample(condition, seed=None):
    """Generate a single CBC sample."""
    if seed is not None:
        np.random.seed(seed)
    
    params = CBC_PARAMETERS[condition]
    sample = {}
    
    for param_name, (min_val, max_val, std) in params.items():
        mean = (min_val + max_val) / 2
        value = np.random.normal(mean, std)
        value = np.clip(value, min_val - std, max_val + std)
        sample[param_name] = round(float(value), 2)
    
    return sample

def generate_hospital_data(hospital_name, n_samples=1000, seed=42):
    """Generate data for a hospital."""
    np.random.seed(seed)
    
    distributions = {
        "italy": {"normal": 0.7, "minor": 0.25, "major": 0.05},
        "pakistan": {"normal": 0.5, "minor": 0.35, "major": 0.15},
        "usa": {"normal": 0.75, "minor": 0.20, "major": 0.05},
        "test": {"normal": 0.6, "minor": 0.3, "major": 0.1}
    }
    
    distribution = distributions.get(hospital_name, {"normal": 0.6, "minor": 0.3, "major": 0.1})
    
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
        for _ in range(n):
            sample = generate_sample(condition)
            sample["patient_id"] = f"P{patient_id:05d}"
            sample["condition"] = condition
            sample["age"] = int(np.random.randint(1, 80))
            sample["gender"] = np.random.choice(["M", "F"])
            data.append(sample)
            patient_id += 1
    
    df = pd.DataFrame(data)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    
    return df

# Main execution
if __name__ == "__main__":
    print("Generating FedNet Demo Data")
    print("=" * 50)
    
    base_dir = Path("data")
    
    # Generate for each hospital
    hospitals = ["italy", "pakistan", "usa"]
    for hospital in hospitals:
        print(f"\nGenerating data for hospital: {hospital}")
        
        hospital_dir = base_dir / f"hospital_{hospital}"
        hospital_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate data
        seed = hash(hospital) % 10000
        df = generate_hospital_data(hospital, n_samples=1000, seed=seed)
        
        # Save
        output_path = hospital_dir / "cbc_data.csv"
        df.to_csv(output_path, index=False)
        print(f"  ✓ Saved {len(df)} samples to {output_path}")
        print(f"    - Normal: {len(df[df['condition']=='normal'])}")
        print(f"    - Minor: {len(df[df['condition']=='minor'])}")
        print(f"    - Major: {len(df[df['condition']=='major'])}")
    
    # Generate test data
    print(f"\nGenerating test data")
    test_dir = base_dir / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    df_test = generate_hospital_data("test", n_samples=300, seed=9999)
    test_path = test_dir / "cbc_data.csv"
    df_test.to_csv(test_path, index=False)
    print(f"  ✓ Saved {len(df_test)} samples to {test_path}")
    
    print("\n" + "=" * 50)
    print("✓ Data generation complete!")
    print(f"\nGenerated {1000*3 + 300} total samples across 4 datasets")
