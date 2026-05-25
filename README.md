![CI](https://github.com/ikel0/sport-analytics/actions/workflows/ci.yml/badge.svg)
# 🏀⚽ Sport Analytics Pipeline

> End-to-end data pipeline for basketball and football analytics — from public API ingestion to an interactive dashboard with a content recommendation engine.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Airflow](https://img.shields.io/badge/Airflow-2.8-red?logo=apacheairflow)
![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake)
![AWS](https://img.shields.io/badge/AWS-S3-FF9900?logo=amazonaws)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)

---

## 📌 Overview

| Stage | Tech | Description |
|---|---|---|
| **Ingestion** | Python, REST APIs | NBA (BallDontLie) + Football (API-Football) |
| **Storage** | AWS S3 | Raw data lake (JSON.gz → Parquet) |
| **Transformation** | Snowflake, SQL, PySpark | Bronze → Silver → Gold |
| **Orchestration** | Apache Airflow | Daily DAGs, retries, XCom |
| **ML** | Scikit-learn | Content-based recommendation engine |
| **Dashboard** | Streamlit + Power BI | Interactive multi-sport analytics |

---

## 🏗️ Architecture

```
APIs (BallDontLie / API-Football)
         │
         ▼  Python collectors
     AWS S3 (Raw JSON.gz)
         │
         ▼  Python cleaners
  Snowflake RAW (Bronze)
         │
         ▼  SQL MERGE
  Snowflake STAGING (Silver)
         │
         ▼  SQL CREATE OR REPLACE
  Snowflake ANALYTICS (Gold)
         │
    ┌────┴────┐
    ▼         ▼
Streamlit  Power BI
Dashboard  Dashboard
```

---

## 📁 Structure

```
sport-analytics/
├── ingestion/           # API collectors + S3 uploader
├── transformation/      # Cleaners + Snowflake loader + SQL models
│   └── sql/
│       ├── staging/     # Silver layer MERGE statements
│       └── analytics/   # Gold layer KPI tables
├── models/              # Recommendation engine (train/evaluate)
├── dashboard/           # Streamlit multi-page app
│   ├── pages/           # NBA / Football / Recommender pages
│   └── components/      # Reusable chart components
├── airflow/dags/        # 3 Airflow DAGs (NBA / Football / ML)
├── scripts/             # Manual pipeline runners
├── tests/               # Unit tests (ingestion / transform / ML)
├── docs/                # Architecture + Power BI guide
├── docker-compose.yml   # Airflow + dashboard stack
├── Makefile             # Developer commands
└── requirements.txt
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/ikel0/sport-analytics.git
cd sport-analytics
pip install -r requirements.txt
cp .env.example .env      # Fill your API keys + Snowflake + AWS creds

# Launch dashboard (demo mode — no credentials needed)
make dashboard
# → http://localhost:8501

# Run full NBA pipeline manually
make run-nba

# Start Airflow (requires Docker)
make airflow-up
# → http://localhost:8080

# Train recommendation model
make train

# Run tests
make test
```

---

## 📊 KPIs Tracked

**NBA:** Win%, Net Rating, Offensive/Defensive Efficiency, Form (last 5), True Shooting%, Fantasy Score

**Football:** Points, Goals/Game, xG proxy, Clean Sheets, Form (last 5), Goals+Assists per 90

---

## 🤖 Recommendation Engine

Content-based filtering using cosine similarity on 4-dimensional feature vectors:
`sport type · content type · popularity · recency`

Personalized by explicit preferences (sport/team/player sliders) and implicit feedback (consultation history).

---

## 👤 Author

**Ikel Ouedraogo** — Data Engineer & Data Analyst  
[LinkedIn](https://linkedin.com/in/ikel-ouedraogo) · [Portfolio](https://ikel0.github.io)

---

## 📄 License

MIT
