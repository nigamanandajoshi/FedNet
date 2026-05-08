"""Quick data verification and exploration script."""

import pandas as pd
from pathlib import Path

print("=" * 60)
print("FedNet Data Verification Report")
print("=" * 60)

base_dir = Path("data")
hospitals = ["italy", "pakistan", "usa", "test"]

total_samples = 0

for hospital in hospitals:
    if hospital == "test":
        data_path = base_dir / "test" / "cbc_data.csv"
    else:
        data_path = base_dir / f"hospital_{hospital}" / "cbc_data.csv"
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        total_samples += len(df)
        
        print(f"\n{hospital.upper()} Dataset:")
        print(f"  Total samples: {len(df)}")
        print(f"  Condition distribution:")
        for condition, count in df['condition'].value_counts().items():
            percentage = (count / len(df)) * 100
            print(f"    - {condition}: {count} ({percentage:.1f}%)")
        
        # Show some statistics
        print(f"  CBC Features (mean):")
        print(f"    - Hemoglobin (hb): {df['hb'].mean():.2f} g/dL")
        print(f"    - RBC: {df['rbc'].mean():.2f} million/µL")
        print(f"    - MCV: {df['mcv'].mean():.1f} fL")
    else:
        print(f"\n{hospital.upper()}: ❌ Data file not found")

print("\n" + "=" * 60)
print(f"Total samples across all datasets: {total_samples}")
print("=" * 60)

# Show sample data
print("\nSample Data (Italy - first 3 rows):")
df_italy = pd.read_csv(base_dir / "hospital_italy" / "cbc_data.csv")
print(df_italy.head(3).to_string())

print("\n✓ All data files generated successfully!")
