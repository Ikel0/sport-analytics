# Power BI Dashboard — Setup Guide

> This guide explains how to connect Power BI Desktop to the Snowflake
> ANALYTICS schema and reproduce the dashboard described in the project.

---

## Prerequisites

- Power BI Desktop (free, Windows)
- Snowflake ODBC Driver ([download](https://developers.snowflake.com/odbc/))
- Access to `SPORT_ANALYTICS.ANALYTICS` schema

---

## 1. Connect Power BI to Snowflake

1. Open Power BI Desktop → **Get Data** → **Snowflake**
2. Enter:
   - **Server:** `your_account.snowflakecomputing.com`
   - **Warehouse:** `COMPUTE_WH`
   - **Database:** `SPORT_ANALYTICS`
   - **Schema:** `ANALYTICS`
3. Authenticate with username/password
4. Select tables:
   - `NBA_TEAM_KPIS`
   - `NBA_PLAYER_KPIS`
   - `FOOTBALL_TEAM_KPIS`
   - `FOOTBALL_PLAYER_KPIS`

---

## 2. Recommended Pages

### Page 1 — NBA Standings
| Visual | Fields | Notes |
|--------|--------|-------|
| Clustered bar chart | Y=Team, X=WIN_PCT | Color by conference |
| Scatter chart | X=PTS_ALLOWED_AVG, Y=PTS_AVG, Size=WINS | Net rating quadrant |
| Table | Team, W, L, Win%, Net RTG, Form | Sorted by Win% |
| Card | Top Win% | Filtered to leader |
| Slicer | SEASON | Allow season switching |

### Page 2 — NBA Players
| Visual | Fields | Notes |
|--------|--------|-------|
| Scatter chart | X=AST_AVG, Y=PTS_AVG, Size=REB_AVG | Color by Pos |
| Bar chart | Top 10 by PTS_AVG | |
| Radar chart | PTS/REB/AST/FG%/3P%/FT% | Use custom visual |
| Table | Full player stats | |
| Slicer | SEASON, POSITION | |

### Page 3 — Football Standings
| Visual | Fields | Notes |
|--------|--------|-------|
| Table | Rank, Team, Pts, W, D, L, GF, GA, GD, Form | Per league |
| Stacked bar | W/D/L per team | |
| Scatter | X=GOALS_CONCEDED_AVG, Y=GOALS_SCORED_AVG, Size=POINTS | |
| Slicer | LEAGUE_NAME, SEASON | |

### Page 4 — Football Players
| Visual | Fields | Notes |
|--------|--------|-------|
| Bar | Top scorers (GOALS) | |
| Scatter | X=ASSISTS_PER_90, Y=GOALS_PER_90 | |
| Table | Full player stats | |
| Slicer | LEAGUE_NAME, POSITION | |

---

## 3. DAX Measures

```dax
-- Win% formatted
Win% = DIVIDE(SUM(NBA_TEAM_KPIS[WINS]), SUM(NBA_TEAM_KPIS[GAMES_PLAYED]), 0)

-- Net Rating color coding
Net RTG Color =
    IF(SELECTEDVALUE(NBA_TEAM_KPIS[NET_RATING]) >= 0, "#27ae60", "#c0392b")

-- Goal Difference sign
GD Display =
    IF(SELECTEDVALUE(FOOTBALL_TEAM_KPIS[GOAL_DIFF]) > 0,
       "+" & SELECTEDVALUE(FOOTBALL_TEAM_KPIS[GOAL_DIFF]),
       FORMAT(SELECTEDVALUE(FOOTBALL_TEAM_KPIS[GOAL_DIFF]), "0"))

-- Form badges (conditional formatting on Form column)
-- W = Green, D = Orange, L = Red (via conditional formatting rules)
```

---

## 4. Scheduled Refresh

1. Publish report to **Power BI Service**
2. Go to **Dataset Settings** → **Data Source Credentials** → Enter Snowflake credentials
3. Set **Scheduled Refresh** → Daily at 10:00 AM (after Airflow pipelines complete)

---

## 5. Snowflake DirectQuery vs Import

| Mode | Pros | Cons | Recommended for |
|------|------|------|----------------|
| **Import** | Fast, offline | Data not real-time | Historical analysis |
| **DirectQuery** | Always live | Slower, Snowflake compute cost | KPI monitoring |

→ **Recommendation:** Use **Import** with daily scheduled refresh.

---

*For questions: [Ikel Ouedraogo](https://linkedin.com/in/ikel-ouedraogo)*
