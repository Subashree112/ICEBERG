from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
ICEBERG_DIR = PROJECT_ROOT / "data" / "iceberg" / "processed"
SEA_ICE_DIR = PROJECT_ROOT / "data" / "sea_ice" / "processed"
ICEBERG_DIR.mkdir(parents=True, exist_ok=True)
SEA_ICE_DIR.mkdir(parents=True, exist_ok=True)

# Create a compact but valid iceberg prediction dataset.
# The app only needs a recent snapshot with predicted positions and a risk level.
base_date = pd.Timestamp("2026-08-20")
rows = []
for i in range(20):
    lat = -58.0 - (i % 8) * 1.2 + (i // 8) * 0.3
    lon = -40.0 + (i % 10) * 6.5 - (i // 10) * 2.0
    risk = ["LOW", "MEDIUM", "HIGH", "CRITICAL"][i % 4]
    rows.append(
        {
            "Iceberg": f"ICB-{i+1:03d}",
            "Last Update": (base_date - pd.Timedelta(days=(i % 6))).strftime("%Y-%m-%d"),
            "predicted_latitude": round(lat, 3),
            "predicted_longitude": round(lon, 3),
            "risk_level": risk,
        }
    )

iceberg_df = pd.DataFrame(rows)
iceberg_df.to_csv(ICEBERG_DIR / "iceberg_baseline_predictions.csv", index=False)

# Create a valid sea-ice grid covering the Antarctic operating region.
# Each point uses a concentration between 0 and 1 and a matching date.
sea_rows = []
for day_offset in range(3):
    date = base_date - pd.Timedelta(days=day_offset)
    for lat in [ -50.0, -55.0, -60.0, -65.0, -70.0, -75.0 ]:
        for lon in [-180.0, -150.0, -120.0, -90.0, -60.0, -30.0, 0.0, 30.0, 60.0, 90.0, 120.0, 150.0]:
            concentration = 0.05 + ((abs(lat) + abs(lon) / 5) % 0.6) / 1.5
            if concentration > 1.0:
                concentration = 1.0
            sea_rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "latitude": round(lat, 3),
                    "longitude": round(lon, 3),
                    "ice_concentration": round(min(concentration, 0.95), 4),
                }
            )

sea_df = pd.DataFrame(sea_rows)
sea_df.to_csv(SEA_ICE_DIR / "sea_ice_concentration.csv", index=False)

print("Created:")
print(ICEBERG_DIR / "iceberg_baseline_predictions.csv")
print(SEA_ICE_DIR / "sea_ice_concentration.csv")
