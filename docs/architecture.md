# Architecture & Technical Documentation

## Overview

Sport Analytics Pipeline is a production-grade data engineering project covering
the full lifecycle from raw API data to an interactive analytics dashboard with
AI-powered content recommendations.

---

## Data Flow

```
APIs (BallDontLie, API-Football)
        │
        ▼ Python collectors (ingestion/)
    AWS S3 — Raw Zone (JSON.gz)
        │
        ▼ Python cleaners (transformation/cleaner.py)
  Snowflake RAW schema (Bronze)
        │
        ▼ SQL MERGE (transformation/sql/staging/)
  Snowflake STAGING schema (Silver)
        │
        ▼ SQL CREATE OR REPLACE (transformation/sql/analytics/)
  Snowflake ANALYTICS schema (Gold)
        │
        ├──► Streamlit Dashboard (dashboard/)
        └──► Recommendation Engine (models/)
```

---

## Snowflake Schemas

| Schema     | Layer  | Purpose                                  |
|------------|--------|------------------------------------------|
| `RAW`      | Bronze | Raw ingested data, append-only           |
| `STAGING`  | Silver | Deduplicated, typed, validated data      |
| `ANALYTICS`| Gold   | Pre-aggregated KPIs for dashboard        |

### Key Tables

**RAW**
- `NBA_GAMES` — One row per game per day
- `NBA_PLAYER_STATS` — Box scores per player per game
- `NBA_STANDINGS` — Team standings snapshot
- `FOOTBALL_FIXTURES` — One row per match
- `FOOTBALL_STANDINGS` — League table snapshots
- `FOOTBALL_PLAYER_STATS` — Player season statistics

**ANALYTICS**
- `NBA_TEAM_KPIS` — Aggregated team metrics (win%, net rating, form)
- `NBA_PLAYER_KPIS` — Season averages, true shooting %, fantasy score
- `FOOTBALL_TEAM_KPIS` — Points, goals scored/conceded, form
- `FOOTBALL_PLAYER_KPIS` — Goals/90, assists/90, contributions

---

## Airflow DAGs

| DAG | Schedule | Purpose |
|-----|----------|---------|
| `nba_daily_pipeline` | `0 8 * * *` | Daily NBA collection + load |
| `football_daily_pipeline` | `0 9 * * *` | Daily football collection + load |
| `recommendation_weekly_retrain` | `0 6 * * 0` | Weekly model retraining |

### DAG: nba_daily_pipeline

```
start
  ├── collect_games ──► clean_and_load_games ──┐
  ├── collect_player_stats ──► clean_and_load_stats ──┤
  └── collect_standings                              │
                                                      ▼
                                        run_staging_transformations
                                                      │
                                                      ▼
                                       run_analytics_transformations
                                                      │
                                                     end
```

---

## Recommendation Engine

**Algorithm:** Content-based filtering with cosine similarity.

**Feature vector (4 dimensions):**
| Feature | Description |
|---------|-------------|
| `sport_enc` | Sport type (NBA=0, Football=1) |
| `type_enc` | Content type (game/player/team/stat_summary) |
| `popularity_score` | Engagement score [0–1] |
| `recency_score` | Content freshness [0–1] |

**User vector construction:**
1. Start from explicit sport preferences (slider in dashboard)
2. Average features of consultation history (implicit feedback)
3. Apply team/player boosts (+25% / +20%) for favorites

**Retraining:** Weekly via Airflow DAG, artifact backed up to S3.

---

## API Sources

### BallDontLie (NBA)
- **Base URL:** `https://api.balldontlie.io/v1`
- **Endpoints used:** `/games`, `/stats`, `/standings`, `/players`, `/season_averages`
- **Auth:** API key in header `Authorization`
- **Free tier:** Yes (rate limited)
- **Docs:** https://www.balldontlie.io/

### API-Football
- **Base URL:** `https://v3.football.api-sports.io`
- **Endpoints used:** `/fixtures`, `/standings`, `/players`, `/players/topscorers`
- **Auth:** `x-rapidapi-key` header
- **Free tier:** 100 requests/day
- **Docs:** https://www.api-football.com/documentation-v3

---

## Environment Setup

### Local (no Docker)
```bash
git clone https://github.com/ikel0/sport-analytics.git
cd sport-analytics
pip install -r requirements.txt
cp .env.example .env   # Fill credentials
make run-nba           # Test pipeline
make dashboard         # Launch dashboard
```

### With Docker (Airflow)
```bash
cp .env.example .env
make airflow-up
# UI → http://localhost:8080 (admin/admin)
# Dashboard → http://localhost:8501
```

### Snowflake setup
1. Create a free Snowflake trial account
2. Create database: `CREATE DATABASE SPORT_ANALYTICS;`
3. Create schemas: `CREATE SCHEMA RAW; CREATE SCHEMA STAGING; CREATE SCHEMA ANALYTICS;`
4. Fill `SNOWFLAKE_*` vars in `.env`

---

## Testing

```bash
make test        # Run all unit tests
make coverage    # Generate HTML coverage report
```

**Test coverage targets:**
- `ingestion/` — mocked HTTP (responses library)
- `transformation/` — synthetic DataFrames
- `models/` — synthetic catalog + user profiles

---

## Code Quality

```bash
make format   # black + isort (auto-fix)
make lint     # flake8 + isort check + black check
```

---

## Author

**Ikel Ouedraogo** — Data Engineer & Data Analyst  
Master Big Data & Machine Learning — EFREI Paris  
[LinkedIn](https://linkedin.com/in/ikel-ouedraogo) · [Portfolio](https://ikel0.github.io)
