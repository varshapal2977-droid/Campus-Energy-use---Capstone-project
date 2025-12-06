"""
campus_energy_dashboard.py
Implements: Data ingestion, aggregation, OOP modeling, visualization, and persistence
Run: python campus_energy_dashboard.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import logging
import sys

# ----- Configuration -----
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "ingestion.log"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)


# ----- Helper functions for ingestion & cleaning -----
def read_all_csvs(data_dir: Path) -> pd.DataFrame:
    """
    Reads all CSV files in data_dir and returns a combined DataFrame.
    Expects each CSV to have at least a timestamp or date column and a kwh/energy usage column.
    If building name isn't present, infer from filename.
    """
    csv_files = list(data_dir.glob("*.csv"))
    if not csv_files:
        logging.warning(f"No CSV files found in {data_dir.resolve()}")
        return pd.DataFrame()  # empty

    frames = []
    for f in csv_files:
        logging.info(f"Attempting to read: {f.name}")
        try:
            # try reading with default parser; skip bad lines
            df = pd.read_csv(f, on_bad_lines='skip')
        except Exception as e:
            logging.error(f"Failed to read {f.name}: {e}")
            continue

        # Attempt to detect date/time column and energy column
        cols_lower = [c.lower() for c in df.columns]
        # identify date column
        date_col = None
        for candidate in ["timestamp", "datetime", "date", "time"]:
            if candidate in cols_lower:
                date_col = df.columns[cols_lower.index(candidate)]
                break
        # identify kwh column
        kwh_col = None
        for candidate in ["kwh", "energy", "usage", "consumption"]:
            if candidate in cols_lower:
                kwh_col = df.columns[cols_lower.index(candidate)]
                break

        # If not found, try heuristics
        if date_col is None:
            # choose first column with date-like values by trying to parse few rows
            for c in df.columns:
                sample = df[c].astype(str).head(5).tolist()
                try:
                    pd.to_datetime(sample, errors="raise")
                    date_col = c
                    break
                except Exception:
                    continue

        if kwh_col is None:
            # choose numeric column other than date
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if numeric_cols:
                # choose the first numeric
                kwh_col = numeric_cols[0]

        if date_col is None or kwh_col is None:
            logging.error(f"Could not identify date or kwh columns in {f.name}; skipping file.")
            continue

        # Standardize columns
        df = df[[date_col, kwh_col]].rename(columns={date_col: "timestamp", kwh_col: "kwh"})
        # Parse timestamps
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        # Drop rows with invalid timestamps or kwh
        df = df.dropna(subset=["timestamp", "kwh"])
        # Add building metadata from filename if not present
        building_name = f.stem
        df["building"] = building_name

        frames.append(df)

    if not frames:
        return pd.DataFrame()
    df_combined = pd.concat(frames, ignore_index=True)
    # Convert kwh to float
    df_combined["kwh"] = pd.to_numeric(df_combined["kwh"], errors="coerce")
    df_combined = df_combined.dropna(subset=["kwh"])
    # Sort by timestamp
    df_combined = df_combined.sort_values("timestamp").reset_index(drop=True)
    logging.info(f"Combined DataFrame shape: {df_combined.shape}")
    return df_combined


# ----- Aggregation functions -----
def calculate_daily_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Return daily totals per building (Date index)."""
    if df.empty:
        return pd.DataFrame()
    df2 = df.copy()
    df2 = df2.set_index("timestamp")
    # ensure tz-naive datetime
    df2.index = pd.to_datetime(df2.index)
    daily = df2.groupby("building").resample("D")["kwh"].sum().reset_index()
    return daily


def calculate_weekly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Return weekly aggregates per building (week starting Monday)."""
    if df.empty:
        return pd.DataFrame()
    df2 = df.copy().set_index("timestamp")
    df2.index = pd.to_datetime(df2.index)
    weekly = df2.groupby("building").resample("W-MON")["kwh"].sum().reset_index()
    return weekly


def building_wise_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return summary (mean, min, max, total) per building."""
    if df.empty:
        return pd.DataFrame()
    summary = df.groupby("building")["kwh"].agg(['mean', 'min', 'max', 'sum']).rename(
        columns={'sum': 'total'}).reset_index()
    return summary


# ----- Object-oriented modeling -----
class MeterReading:
    def __init__(self, timestamp: pd.Timestamp, kwh: float):
        self.timestamp = pd.to_datetime(timestamp)
        self.kwh = float(kwh)


class Building:
    def __init__(self, name: str):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading: MeterReading):
        self.meter_readings.append(reading)

    def total_consumption(self) -> float:
        return sum(r.kwh for r in self.meter_readings)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.meter_readings:
            return pd.DataFrame(columns=["timestamp", "kwh", "building"])
        df = pd.DataFrame([{"timestamp": r.timestamp, "kwh": r.kwh} for r in self.meter_readings])
        df["building"] = self.name
        return df

    def generate_report_text(self) -> str:
        df = self.to_dataframe()
        if df.empty:
            return f"Building {self.name}: No data."
        total = df["kwh"].sum()
        mean = df["kwh"].mean()
        peak_idx = df["kwh"].idxmax()
        peak_time = df.loc[peak_idx, "timestamp"]
        return f"Building: {self.name}\nTotal (kWh): {total:.2f}\nMean (kWh): {mean:.2f}\nPeak at: {peak_time}\n"


class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def ingest_from_dataframe(self, df: pd.DataFrame):
        """Populate Building objects from combined DataFrame."""
        for _, row in df.iterrows():
            bname = row["building"]
            if bname not in self.buildings:
                self.buildings[bname] = Building(bname)
            mr = MeterReading(row["timestamp"], row["kwh"])
            self.buildings[bname].add_reading(mr)

    def combined_dataframe(self) -> pd.DataFrame:
        dfs = [b.to_dataframe() for b in self.buildings.values() if not b.to_dataframe().empty]
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs, ignore_index=True)


# ----- Visualization -----
def make_dashboard_image(daily_df: pd.DataFrame, weekly_df: pd.DataFrame, full_df: pd.DataFrame, out_path: Path):
    """
    Creates a 3-panel figure:
      1) Trend line: daily consumption for each building
      2) Bar chart: average weekly usage per building
      3) Scatter: top hourly readings (peak hours) vs timestamp
    """
    if full_df.empty:
        logging.warning("No data for visualization.")
        return

    plt.figure(figsize=(14, 10))

    # Panel 1: Daily trend lines
    ax1 = plt.subplot(2, 2, 1)
    if not daily_df.empty:
        for bname, group in daily_df.groupby("building"):
            ax1.plot(group["timestamp"], group["kwh"], label=bname)
    ax1.set_title("Daily Consumption Trend")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("kWh (daily total)")
    ax1.legend(loc="best", fontsize='small')

    # Panel 2: Average weekly usage bar chart
    ax2 = plt.subplot(2, 2, 2)
    if not weekly_df.empty:
        avg_weekly = weekly_df.groupby("building")["kwh"].mean().sort_values(ascending=False)
        ax2.bar(avg_weekly.index, avg_weekly.values)
        ax2.set_xticklabels(avg_weekly.index, rotation=45, ha="right")
    ax2.set_title("Average Weekly Usage per Building")
    ax2.set_ylabel("kWh (weekly avg)")

    # Panel 3: Scatter of top readings (peak hours)
    ax3 = plt.subplot(2, 1, 2)
    # pick top N readings across campus
    top_n = full_df.sort_values("kwh", ascending=False).head(100)
    ax3.scatter(top_n["timestamp"], top_n["kwh"], s=20)
    ax3.set_title("Top 100 Meter Readings (kWh) — Peak Hours")
    ax3.set_xlabel("Timestamp")
    ax3.set_ylabel("kWh")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    logging.info(f"Dashboard image saved to: {out_path}")


# ----- Persistence & summary -----
def save_outputs(cleaned_df: pd.DataFrame, building_summary_df: pd.DataFrame, daily_df: pd.DataFrame, weekly_df: pd.DataFrame, output_dir: Path):
    cleaned_out = output_dir / "cleaned_energy_data.csv"
    summary_out = output_dir / "building_summary.csv"
    daily_out = output_dir / "daily_totals.csv"
    weekly_out = output_dir / "weekly_totals.csv"

    if not cleaned_df.empty:
        cleaned_df.to_csv(cleaned_out, index=False)
        logging.info(f"Saved cleaned data to {cleaned_out}")
    if not building_summary_df.empty:
        building_summary_df.to_csv(summary_out, index=False)
        logging.info(f"Saved building summary to {summary_out}")
    if not daily_df.empty:
        daily_df.to_csv(daily_out, index=False)
        logging.info(f"Saved daily totals to {daily_out}")
    if not weekly_df.empty:
        weekly_df.to_csv(weekly_out, index=False)
        logging.info(f"Saved weekly totals to {weekly_out}")


def generate_text_summary(full_df: pd.DataFrame, building_summary_df: pd.DataFrame, output_dir: Path):
    out_txt = output_dir / "summary.txt"
    lines = []
    if full_df.empty:
        lines.append("No data available.")
    else:
        total_campus = full_df["kwh"].sum()
        lines.append(f"Total Campus Consumption (kWh): {total_campus:.2f}")

        if not building_summary_df.empty:
            highest = building_summary_df.sort_values("total", ascending=False).iloc[0]
            lines.append(f"Highest-consuming building: {highest['building']} ({highest['total']:.2f} kWh)")

        # Peak load time (timestamp with max kwh)
        idx = full_df["kwh"].idxmax()
        peak_time = full_df.loc[idx, "timestamp"]
        lines.append(f"Peak reading time: {peak_time}")

        # Weekly/daily trends (simple sentences)
        mean_daily = full_df.set_index("timestamp").resample("D")["kwh"].sum().mean()
        mean_weekly = full_df.set_index("timestamp").resample("W-MON")["kwh"].sum().mean()
        lines.append(f"Average daily campus consumption: {mean_daily:.2f} kWh")
        lines.append(f"Average weekly campus consumption: {mean_weekly:.2f} kWh")

    with open(out_txt, "w") as fh:
        fh.write("\n".join(lines))
    logging.info(f"Summary written to {out_txt}")


# ----- Main procedure -----
def main():
    logging.info("Starting campus energy dashboard pipeline")
    df_combined = read_all_csvs(DATA_DIR)

    if df_combined.empty:
        logging.error("No valid data available. Exiting.")
        return

    # Aggregations
    daily = calculate_daily_totals(df_combined)
    weekly = calculate_weekly_aggregates(df_combined)
    summary = building_wise_summary(df_combined)

    # OOP ingestion
    manager = BuildingManager()
    manager.ingest_from_dataframe(df_combined)
    # produce combined df from objects (should match df_combined)
    df_from_objects = manager.combined_dataframe()

    # Visualize
    dashboard_path = OUTPUT_DIR / "dashboard.png"
    make_dashboard_image(daily, weekly, df_combined, dashboard_path)

    # Save outputs
    save_outputs(df_combined, summary, daily, weekly, OUTPUT_DIR)
    generate_text_summary(df_combined, summary, OUTPUT_DIR)

    # Print short report to console
    print("\n--- Executive Summary (first lines) ---")
    summary_txt_path = OUTPUT_DIR / "summary.txt"
    with open(summary_txt_path) as fh:
        for _ in range(10):
            line = fh.readline()
            if not line:
                break
            print(line.strip())

    logging.info("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
