import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("/app/output")
merged_file = OUTPUT_DIR / "training_data.csv"

csv_files = [f for f in OUTPUT_DIR.glob("training_data_*.csv")]
if not csv_files:
    print("❌ No CSV files found.")
else:
    dfs = [pd.read_csv(f) for f in csv_files]
    combined = pd.concat(dfs, ignore_index=True)
    combined.to_csv(merged_file, index=False, encoding="utf-8")
    print(f"✅ Merged {len(csv_files)} files → {merged_file.name} ({len(combined)} rows)")
