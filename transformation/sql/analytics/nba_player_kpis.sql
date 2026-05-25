-- ============================================================
-- NBA Player KPIs — Gold Layer
-- Aggregates per-player per-season averages.
-- ============================================================

CREATE OR REPLACE TABLE SPORT_ANALYTICS.ANALYTICS.NBA_PLAYER_KPIS AS

WITH raw_stats AS (
    SELECT
        season,
        player_id,
        player_name,
        team_id,
        team_name,
        position,
        COUNT(*)                        AS games_played,
        ROUND(AVG(points), 1)           AS pts_avg,
        ROUND(AVG(total_rebounds), 1)   AS reb_avg,
        ROUND(AVG(assists), 1)          AS ast_avg,
        ROUND(AVG(steals), 1)           AS stl_avg,
        ROUND(AVG(blocks), 1)           AS blk_avg,
        ROUND(AVG(turnovers), 1)        AS tov_avg,
        ROUND(AVG(minutes), 1)          AS min_avg,
        ROUND(AVG(fg_pct), 3)           AS fg_pct,
        ROUND(AVG(fg3_pct), 3)          AS fg3_pct,
        ROUND(AVG(ft_pct), 3)           AS ft_pct,
        MAX(points)                     AS pts_max,
        -- True Shooting % approximation
        ROUND(
            AVG(points) / NULLIF(2 * (AVG(fg_attempts) + 0.44 * AVG(ft_attempts)), 0),
            3
        )                               AS ts_pct
    FROM SPORT_ANALYTICS.STAGING.NBA_PLAYER_STATS
    GROUP BY season, player_id, player_name, team_id, team_name, position
),

-- Fantasy score: PTS + 1.2*REB + 1.5*AST + 3*STL + 3*BLK - TOV
fantasy AS (
    SELECT
        player_id, season,
        ROUND(pts_avg + 1.2*reb_avg + 1.5*ast_avg + 3*stl_avg + 3*blk_avg - tov_avg, 1)
            AS fantasy_score
    FROM raw_stats
)

SELECT
    rs.*,
    f.fantasy_score,
    CURRENT_TIMESTAMP() AS _computed_at
FROM raw_stats rs
JOIN fantasy f ON rs.player_id = f.player_id AND rs.season = f.season
ORDER BY season DESC, pts_avg DESC;
