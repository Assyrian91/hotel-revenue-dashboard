> ⚠️ **This repo has moved.** It's now maintained as part of
> [`hotel-intelligence-suite`](https://github.com/Assyrian91/hotel-intelligence-suite),
> a consolidated collection of hotel operations projects, with full commit
> history preserved. This repo is archived and kept read-only for reference.

---
# 🏨 Hotel Revenue Intelligence Dashboard

> End-to-end data engineering + BI project tracking Occupancy Rate, ADR, and RevPAR
> with a 90-day AI-powered forecast and plain-English insights.

![Dashboard Screenshot](docs/screenshot.png)

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-red?logo=streamlit)](YOUR_STREAMLIT_URL)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🔴 Live Demo
👉 [Open Dashboard](YOUR_STREAMLIT_URL)

## 📐 Architecture
Raw CSV → ETL Pipeline → SQLite DB → KPI Engine → Prophet Forecast → Streamlit Dashboard

↓

Groq AI Narratives

## 📊 KPIs Tracked
| KPI | Formula | Insight |
|-----|---------|---------|
| Occupancy Rate | Rooms Sold ÷ Rooms Available × 100 | Demand signal |
| ADR | Room Revenue ÷ Rooms Sold | Pricing power |
| RevPAR | ADR × Occupancy Rate | Overall performance |

## 🛠 Tech Stack
- **ETL**: Python, Pandas, SQLAlchemy, SQLite
- **KPIs**: SQL views, Python functions
- **Forecasting**: Facebook Prophet (90-day horizon)
- **AI Insights**: Groq API (Llama 3.1)
- **Dashboard**: Streamlit + Plotly
- **BI**: Power BI Desktop

## 🚀 Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/hotel-revenue-dashboard
cd hotel-revenue-dashboard
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # add your GROQ_API_KEY
python data/raw/generate_data.py
python run_etl.py
python forecasting/forecast.py
streamlit run dashboard/app.py
```

## 📁 Project Structure
├── data/raw/          # Raw synthetic booking data

├── data/processed/    # SQLite DB + KPI CSVs

├── etl/               # Extract, Transform, Load scripts

├── kpis/              # KPI calculation layer

├── forecasting/       # Prophet model + Groq AI narratives

├── dashboard/         # Streamlit app

└── notebooks/         # EDA + validation notebooks
