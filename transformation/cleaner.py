"""
Data Cleaning Pipeline — Silver layer.
Cleans raw JSON into structured Pandas DataFrames.
"""
import logging
from datetime import datetime
from typing import Any
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class NBADataCleaner:

    def clean_games(self, raw: dict) -> pd.DataFrame:
        records = raw.get("data", [])
        if not records:
            return pd.DataFrame()
        df = pd.json_normalize(records)
        rename = {
            "id": "game_id", "date": "game_date", "season": "season",
            "status": "status", "period": "period", "postseason": "is_postseason",
            "home_team.id": "home_team_id", "home_team.full_name": "home_team_name",
            "home_team.abbreviation": "home_team_abbr", "home_team.conference": "home_conference",
            "home_team.division": "home_division",
            "visitor_team.id": "away_team_id", "visitor_team.full_name": "away_team_name",
            "visitor_team.abbreviation": "away_team_abbr",
            "home_team_score": "home_score", "visitor_team_score": "away_score",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        df["game_date"]   = pd.to_datetime(df["game_date"], errors="coerce").dt.date
        df["home_score"]  = pd.to_numeric(df.get("home_score", 0), errors="coerce").fillna(0).astype(int)
        df["away_score"]  = pd.to_numeric(df.get("away_score", 0), errors="coerce").fillna(0).astype(int)
        df["is_postseason"] = df["is_postseason"].fillna(False).astype(bool)
        df["home_win"]    = (df["home_score"] > df["away_score"]).astype(int)
        df["total_points"] = df["home_score"] + df["away_score"]
        df["point_diff"]  = (df["home_score"] - df["away_score"]).abs()
        df["is_final"]    = df["status"].str.upper().str.contains("FINAL", na=False)
        df = df.drop_duplicates(subset=["game_id"])
        df["_loaded_at"]  = datetime.utcnow()
        df["_source"]     = "balldontlie"
        logger.info(f"Cleaned {len(df)} NBA games.")
        return df

    def clean_player_stats(self, raw: dict) -> pd.DataFrame:
        records = raw.get("data", [])
        if not records:
            return pd.DataFrame()
        df = pd.json_normalize(records)
        rename = {
            "id": "stat_id", "ast": "assists", "blk": "blocks", "dreb": "def_rebounds",
            "fg3_pct": "fg3_pct", "fg3a": "fg3_attempts", "fg3m": "fg3_made",
            "fg_pct": "fg_pct", "fga": "fg_attempts", "fgm": "fg_made",
            "ft_pct": "ft_pct", "fta": "ft_attempts", "ftm": "ft_made",
            "min": "minutes", "oreb": "off_rebounds", "pf": "personal_fouls",
            "pts": "points", "reb": "total_rebounds", "stl": "steals", "turnover": "turnovers",
            "game.id": "game_id", "game.date": "game_date", "game.season": "season",
            "game.home_team_score": "home_score", "game.visitor_team_score": "away_score",
            "player.id": "player_id", "player.first_name": "first_name",
            "player.last_name": "last_name", "player.position": "position",
            "team.id": "team_id", "team.full_name": "team_name", "team.abbreviation": "team_abbr",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})

        def parse_min(val):
            if pd.isna(val) or val in ("", "None", None): return 0.0
            try:
                parts = str(val).split(":")
                return float(parts[0]) + float(parts[1]) / 60 if len(parts) == 2 else float(parts[0])
            except: return 0.0

        df["minutes"] = df["minutes"].apply(parse_min)
        num_cols = ["assists","blocks","def_rebounds","fg3_pct","fg3_attempts","fg3_made",
                    "fg_pct","fg_attempts","fg_made","ft_pct","ft_attempts","ft_made",
                    "off_rebounds","personal_fouls","points","total_rebounds","steals","turnovers"]
        for c in num_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        df["player_name"] = (df.get("first_name","").fillna("") + " " + df.get("last_name","").fillna("")).str.strip()
        df["game_date"] = pd.to_datetime(df.get("game_date"), errors="coerce").dt.date
        df = df[df["minutes"] > 0].copy()
        df = df.drop_duplicates(subset=["stat_id"])
        df["_loaded_at"] = datetime.utcnow()
        df["_source"] = "balldontlie"
        logger.info(f"Cleaned {len(df)} NBA player stats.")
        return df

    def clean_standings(self, raw: dict) -> pd.DataFrame:
        records = raw.get("data", [])
        if not records:
            return pd.DataFrame()
        df = pd.json_normalize(records)
        rename = {
            "team.id": "team_id", "team.full_name": "team_name",
            "team.abbreviation": "team_abbr", "team.conference": "conference",
            "team.division": "division", "season": "season",
            "wins": "wins", "losses": "losses",
        }
        df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
        df["wins"]   = pd.to_numeric(df.get("wins", 0), errors="coerce").fillna(0).astype(int)
        df["losses"] = pd.to_numeric(df.get("losses", 0), errors="coerce").fillna(0).astype(int)
        df["games_played"] = df["wins"] + df["losses"]
        df["win_pct"] = (df["wins"] / df["games_played"].replace(0, np.nan)).round(3)
        df["_loaded_at"] = datetime.utcnow()
        logger.info(f"Cleaned {len(df)} NBA standings.")
        return df


class FootballDataCleaner:

    def clean_fixtures(self, raw: dict) -> pd.DataFrame:
        records = raw.get("data", [])
        if not records:
            return pd.DataFrame()
        rows = []
        for rec in records:
            fix = rec.get("fixture", {})
            lg  = rec.get("league", {})
            tm  = rec.get("teams", {})
            gl  = rec.get("goals", {})
            sc  = rec.get("score", {})
            rows.append({
                "fixture_id":      fix.get("id"),
                "match_date":      fix.get("date"),
                "status":          fix.get("status", {}).get("long"),
                "status_short":    fix.get("status", {}).get("short"),
                "referee":         fix.get("referee"),
                "venue":           fix.get("venue", {}).get("name"),
                "league_id":       lg.get("id"),
                "league_name":     lg.get("name"),
                "country":         lg.get("country"),
                "season":          lg.get("season"),
                "round":           lg.get("round"),
                "home_team_id":    tm.get("home", {}).get("id"),
                "home_team_name":  tm.get("home", {}).get("name"),
                "home_team_winner":tm.get("home", {}).get("winner"),
                "away_team_id":    tm.get("away", {}).get("id"),
                "away_team_name":  tm.get("away", {}).get("name"),
                "away_team_winner":tm.get("away", {}).get("winner"),
                "home_goals":      gl.get("home"),
                "away_goals":      gl.get("away"),
                "ht_home":         sc.get("halftime", {}).get("home"),
                "ht_away":         sc.get("halftime", {}).get("away"),
            })
        df = pd.DataFrame(rows)
        df["match_date"] = pd.to_datetime(df["match_date"], utc=True, errors="coerce").dt.date
        for c in ["home_goals","away_goals","ht_home","ht_away"]:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        mask = df["status_short"] == "FT"
        df["total_goals"] = np.where(mask, df["home_goals"] + df["away_goals"], np.nan)
        df["is_draw"]     = (mask & (df["home_goals"] == df["away_goals"])).astype(int)
        df["goal_diff"]   = (df["home_goals"] - df["away_goals"]).abs()
        df = df.drop_duplicates(subset=["fixture_id"])
        df["_loaded_at"] = datetime.utcnow()
        df["_source"] = "api-football"
        logger.info(f"Cleaned {len(df)} football fixtures.")
        return df

    def clean_standings(self, raw: dict) -> pd.DataFrame:
        records = raw.get("data", [])
        if not records:
            return pd.DataFrame()
        rows = []
        for entry in records:
            lg = entry.get("league", {})
            for group in lg.get("standings", []):
                for row in group:
                    team  = row.get("team", {})
                    all_s = row.get("all", {})
                    goals = all_s.get("goals", {})
                    home  = row.get("home", {})
                    away  = row.get("away", {})
                    rows.append({
                        "league_id": lg.get("id"), "league_name": lg.get("name"),
                        "season": lg.get("season"), "team_id": team.get("id"),
                        "team_name": team.get("name"), "rank": row.get("rank"),
                        "points": row.get("points"), "goal_diff": row.get("goalsDiff"),
                        "form": row.get("form"), "played": all_s.get("played"),
                        "wins": all_s.get("win"), "draws": all_s.get("draw"),
                        "losses": all_s.get("lose"), "goals_for": goals.get("for"),
                        "goals_against": goals.get("against"),
                        "home_wins": home.get("win"), "away_wins": away.get("win"),
                    })
        df = pd.DataFrame(rows)
        for c in ["rank","points","goal_diff","played","wins","draws","losses","goals_for","goals_against"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        df["win_pct"]        = (df["wins"] / df["played"].replace(0, np.nan)).round(3)
        df["goals_per_game"] = (df["goals_for"] / df["played"].replace(0, np.nan)).round(2)
        df["_loaded_at"] = datetime.utcnow()
        df["_source"] = "api-football"
        logger.info(f"Cleaned {len(df)} football standings.")
        return df

    def clean_player_stats(self, raw: dict) -> pd.DataFrame:
        records = raw.get("data", [])
        if not records:
            return pd.DataFrame()
        rows = []
        for rec in records:
            player = rec.get("player", {})
            for stats in rec.get("statistics", []):
                team   = stats.get("team", {})
                league = stats.get("league", {})
                games  = stats.get("games", {})
                goals  = stats.get("goals", {})
                passes = stats.get("passes", {})
                rows.append({
                    "player_id":       player.get("id"),
                    "player_name":     player.get("name"),
                    "age":             player.get("age"),
                    "nationality":     player.get("nationality"),
                    "position":        games.get("position"),
                    "team_id":         team.get("id"),
                    "team_name":       team.get("name"),
                    "league_id":       league.get("id"),
                    "league_name":     league.get("name"),
                    "season":          league.get("season"),
                    "appearances":     games.get("appearences"),
                    "minutes_played":  games.get("minutes"),
                    "rating":          games.get("rating"),
                    "goals":           goals.get("total"),
                    "assists":         goals.get("assists"),
                    "passes_total":    passes.get("total"),
                    "key_passes":      passes.get("key"),
                    "pass_accuracy":   passes.get("accuracy"),
                })
        df = pd.DataFrame(rows)
        for c in ["appearances","minutes_played","goals","assists","passes_total","key_passes"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df["goals_per_90"] = (df["goals"] / (df["minutes_played"] / 90).replace(0, np.nan)).round(2)
        df["_loaded_at"] = datetime.utcnow()
        df["_source"] = "api-football"
        logger.info(f"Cleaned {len(df)} football player stats.")
        return df
