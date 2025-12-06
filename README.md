# Campus-Energy-use---Capstone-project
<img width="701" height="377" alt="2025-12-06 (14)" src="https://github.com/user-attachments/assets/6ba9be6c-9f2a-4bc9-b693-b8289d1faacd" />
<img width="313" height="219" alt="image" src="https://github.com/user-attachments/assets/91231473-62aa-4d31-b2e5-675e1b275d51" />
<img width="349" height="156" alt="2025-12-06 (16)" src="https://github.com/user-attachments/assets/a20ddf2d-4617-41fc-a9fd-f9900a79d615" />


data ingestion, processing, visualization, and building-level energy analysis pipeline.

🏫 Project Overview

The Campus Energy-Use Dashboard is a Python-based analytical system that ingests energy meter readings from multiple buildings on a campus, processes the data, performs aggregations, generates visual analytics, and produces structured reports.

This project fulfills the requirements of the Capstone Assignment: Campus Energy-Use Dashboard by implementing:

Automated data ingestion

Error-handling & logging

Data cleaning & transformation

Daily & weekly energy trends

Object-Oriented Modeling (OOP) of buildings and meter readings

Visualization dashboard

CSV and text report exports

Combined analysis for entire campus

📂 Repository Structure
📁 campus-energy-dashboard/
│
├── campus_energy_dashboard.py        # Main script (pipeline)
├── README.md                          # Project documentation
│
├── data/                              # Raw input CSV files
│   ├── admin.csv
│   ├── library.csv
│   ├── hostel_a.csv
│   ├── meter1.csv
│
├── output/                            # Generated outputs
│   ├── cleaned_energy_data.csv
│   ├── building_summary.csv
│   ├── daily_totals.csv
│   ├── weekly_totals.csv
│   ├── summary.txt
│   ├── dashboard.png
│   ├── ingestion.log
│
└── requirements.txt                   # Dependencies

📊 Features Implemented
✔ 1. Data Ingestion

Reads all CSV files inside data/

Auto-detects columns (timestamp, kwh)

Infers building name from filename

Handles:

Missing columns

Bad rows

Empty files

Format issues

Logs all ingestion activity to output/ingestion.log

✔ 2. Data Processing

Timestamp parsing

Removal of invalid entries

Standardized column structure

Combined dataset for all buildings

✔ 3. Aggregations

Daily totals per building

Weekly totals per building

Building-wise summaries (min, max, mean, total kWh)

✔ 4. Object-Oriented Modeling

Implemented classes:

MeterReading

Building

BuildingManager

Supports:

Adding readings

Summaries

Report generation

Combined DataFrame export

✔ 5. Visualization Dashboard

Generated file: dashboard.png

Includes:

Daily trends line chart

Weekly average bar chart

Top 100 highest hourly readings scatter plot

✔ 6. Output & Persistence

Exports the following:

File	Description
cleaned_energy_data.csv	Clean, standardized dataset
building_summary.csv	Summary metrics for each building
daily_totals.csv	Daily aggregated kWh usage
weekly_totals.csv	Weekly aggregated usage
summary.txt	Executive summary + key insights
dashboard.png	Visual dashboard
ingestion.log	Logs of ingestion process
🚀 How to Run the Project
1️⃣ Clone the Repository
git clone https://github.com/YOUR-USERNAME/campus-energy-dashboard.git
cd campus-energy-dashboard

2️⃣ Create Virtual Environment
Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Add Your CSV Files

Place all energy meter CSVs into:

data/


Each file must follow this format:

timestamp,kwh
2025-11-01 00:00,12.5
2025-11-01 01:00,13.2

5️⃣ Run the Pipeline
python campus_energy_dashboard.py

📈 Outputs Explained

After running the script, the output/ folder will contain:

📊 dashboard.png

A 3-panel visual report:

Daily trend line chart

Weekly average bar chart

Peak-hour scatter plot

📄 summary.txt

Includes:

Total campus energy usage

Highest consuming building

Peak load timestamp

Average daily & weekly consumption

📁 CSV Files

Cleaned dataset

Daily & weekly totals

Building summaries

📝 ingestion.log

Tracks:

File reads

Errors & warnings

Successful ingestion

🔧 Technologies Used

Python 3.8+

pandas

matplotlib

pathlib

logging

🧪 Sample CSV Data Included

Your repo includes realistic meter datasets for:

Admin Building

Library

Hostel A

Standalone Meter

These allow the dashboard to generate meaningful trends.

🏆 Project Learning Outcomes

This project demonstrates:

Data cleaning & wrangling

Working with timestamps

Weekly and daily time-series resampling

Error handling and logging

Multi-file ingestion pipeline

Object-oriented design (Python classes)

Static visualization using Matplotlib

Exporting structured outputs

Writing an analytical summary

Perfect for coursework, capstone evaluation, or future portfolio showcase.

🤝 Contributing

Pull requests are welcome!
Please open an issue first to discuss proposed changes.

📬 Contact

For feedback or help, feel free to reach out through GitHub Issues.
