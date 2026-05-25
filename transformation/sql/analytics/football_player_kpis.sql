-- ============================================================
-- Football Player KPIs — Gold Layer
-- ============================================================

CREATE OR REPLACE TABLE SPORT_ANALYTICS.ANALYTICS.FOOTBALL_PLAYER_KPIS AS

SELECT
    player_id,
    player_name,
    age,
    nationality,
    position,
    team_id,
    team_name,
    league_id,
    league_name,
    season,
    appearances,
    minutes_played,
    goals,
    assists,
    goals + assists                                              AS goal_contributions,
    ROUND(goals   / NULLIF(minutes_played / 90, 0), 2)          AS goals_per_90,
    ROUND(assists / NULLIF(minutes_played / 90, 0), 2)          AS assists_per_90,
    ROUND((goals + assists) / NULLIF(minutes_played / 90, 0), 2) AS contributions_per_90,
    passes_total,
    key_passes,
    pass_accuracy,
    rating,
    CURRENT_TIMESTAMP()                                         AS _computed_at
FROM SPORT_ANALYTICS.RAW.FOOTBALL_PLAYER_STATS
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY player_id, league_id, season ORDER BY _loaded_at DESC
) = 1
ORDER BY season DESC, goals DESC;
