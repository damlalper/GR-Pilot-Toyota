import pandas as pd
from pathlib import Path

race2_dir = Path(r"C:\Users\Lenovo\Desktop\hackathons\TOYOTA\COTA\Race 2")

datasets = {
    "Provisional Results": "03_Provisional Results_ Race 2_Anonymized.CSV",
    "Class Results": "05_Provisional Results by Class_ Race 2_Anonymized.CSV",
    "Sector Analysis": "23_AnalysisEnduranceWithSections_ Race 2_Anonymized.CSV",
    "Weather": "26_Weather_ Race 2_Anonymized.CSV",
    "Best Laps": "99_Best 10 Laps By Driver_ Race 2_Anonymized.CSV",
    "Lap End Times": "COTA_lap_end_time_R2.csv",
    "Lap Start Times": "COTA_lap_start_time_R2.csv",
    "Lap Times": "COTA_lap_time_R2.csv",
}

print("=" * 80)
print("RACE 2 DATASET ANALYSIS - Unused Goldmine!")
print("=" * 80)

for name, filename in datasets.items():
    filepath = race2_dir / filename
    print(f"\n{'='*80}")
    print(f"[DATASET] {name.upper()}")
    print(f"{'='*80}")

    try:
        # Auto-detect separator
        with open(filepath, 'r') as f:
            first_line = f.readline()
            sep = ';' if ';' in first_line else ','

        df = pd.read_csv(filepath, sep=sep, nrows=10)

        print(f"File: {filename}")
        print(f"Rows (sample): {len(df)} | Columns: {len(df.columns)}")
        print(f"\nCOLUMNS:")
        print(df.columns.tolist())

        print(f"\nSAMPLE DATA (first 3 rows):")
        print(df.head(3).to_string())

        # Data types
        print(f"\nDATA TYPES:")
        print(df.dtypes.to_string())

        # Potential use cases
        print(f"\nPOTENTIAL USE CASES:")

        if "sector" in name.lower() or "analysis" in name.lower():
            print("   - Turn-by-turn performance analysis")
            print("   - Sector time comparison (19 turns!)")
            print("   - Identify slow corners")
            print("   - Pit stop analysis")

        elif "weather" in name.lower():
            print("   - Temperature correlation with lap times")
            print("   - Grip prediction based on track temp")
            print("   - Rain impact analysis")
            print("   - Tire strategy optimization")

        elif "best" in name.lower() or "laps" in name.lower():
            print("   - Driver benchmarking")
            print("   - Perfect lap construction (best sectors)")
            print("   - Consistency analysis")
            print("   - Driver DNA clustering")

        elif "lap_end" in name.lower() or "lap_start" in name.lower():
            print("   - Precise lap timing")
            print("   - Sector boundary detection")
            print("   - Telemetry segmentation")
            print("   - Lap validation")

        elif "results" in name.lower():
            print("   - Final standings visualization")
            print("   - Class-based analysis")
            print("   - Race strategy insights")
            print("   - Position changes over time")

        print()

    except Exception as e:
        print(f"[ERROR] {e}")
        print()

print("\n" + "=" * 80)
print("[SUMMARY] 8 Unutilized Datasets = MAJOR OPPORTUNITY!")
print("=" * 80)
print("""
RECOMMENDED PRIORITY:

[HIGH VALUE] (Implement NOW):
1. Sector Analysis (23_AnalysisEnduranceWithSections) - 19 turns data!
2. Best Laps (99_Best 10 Laps) - Driver benchmarking
3. Lap Times (COTA_lap_time) - Ground truth for ML

[MEDIUM VALUE] (Implement Soon):
4. Weather (26_Weather) - Already loaded but not used properly
5. Lap Start/End Times - Precise timing validation

[LOW VALUE] (Nice to Have):
6. Provisional Results - Static race results
7. Class Results - Static standings
""")
