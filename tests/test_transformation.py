"""
Unit tests for data cleaning / transformation layer.
"""

import numpy as np
import pandas as pd
import pytest

from transformation.cleaner import FootballDataCleaner, NBADataCleaner


# ── NBA Cleaner ────────────────────────────────────────────────────────────

class TestNBADataCleaner:

    def setup_method(self):
        self.cleaner = NBADataCleaner()

    def _make_games_payload(self, overrides=None):
        record = {
            "id": 1,
            "date": "2024-01-15",
            "season": 2023,
            "status": "Final",
            "period": 4,
            "time": "",
            "postseason": False,
            "home_team": {
                "id": 1, "full_name": "Boston Celtics",
                "abbreviation": "BOS", "conference": "East", "division": "Atlantic",
            },
            "visitor_team": {
                "id": 2, "full_name": "Los Angeles Lakers",
                "abbreviation": "LAL", "conference": "West", "division": "Pacific",
            },
            "home_team_score": 112,
            "visitor_team_score": 105,
        }
        if overrides:
            record.update(overrides)
        return {"data": [record]}

    def test_clean_games_basic(self):
        df = self.cleaner.clean_games(self._make_games_payload())
        assert len(df) == 1
        assert "game_id" in df.columns
        assert "home_score" in df.columns
        assert df.iloc[0]["home_score"] == 112
        assert df.iloc[0]["away_score"] == 105

    def test_clean_games_feature_engineering(self):
        df = self.cleaner.clean_games(self._make_games_payload())
        assert df.iloc[0]["home_win"] == 1
        assert df.iloc[0]["total_points"] == 217
        assert df.iloc[0]["point_diff"] == 7
        assert df.iloc[0]["is_final"] == True

    def test_clean_games_home_loss(self):
        payload = self._make_games_payload({"home_team_score": 100, "visitor_team_score": 110})
        df = self.cleaner.clean_games(payload)
        assert df.iloc[0]["home_win"] == 0

    def test_clean_games_empty(self):
        df = self.cleaner.clean_games({"data": []})
        assert df.empty

    def test_clean_games_dedup(self):
        payload = self._make_games_payload()
        payload["data"] = payload["data"] * 3   # 3 identical records
        df = self.cleaner.clean_games(payload)
        assert len(df) == 1   # deduplicated

    def test_clean_player_stats_minutes_parsing(self):
        record = {
            "id": 1, "ast": 5, "blk": 1, "dreb": 4,
            "fg3_pct": 0.38, "fg3a": 8, "fg3m": 3,
            "fg_pct": 0.51, "fga": 18, "fgm": 9,
            "ft_pct": 0.85, "fta": 7, "ftm": 6,
            "min": "35:30", "oreb": 2, "pf": 3,
            "pts": 27, "reb": 6, "stl": 1, "turnover": 2,
            "game": {"id": 1, "date": "2024-01-15", "season": 2023,
                     "home_team_id": 1, "visitor_team_id": 2,
                     "home_team_score": 112, "visitor_team_score": 105},
            "player": {"id": 10, "first_name": "Jayson", "last_name": "Tatum", "position": "SF"},
            "team": {"id": 1, "full_name": "Boston Celtics", "abbreviation": "BOS"},
        }
        df = self.cleaner.clean_player_stats({"data": [record]})
        assert len(df) == 1
        assert abs(df.iloc[0]["minutes"] - 35.5) < 0.1

    def test_clean_player_stats_dnp_filtered(self):
        """Players with 0 minutes (DNP) should be filtered out."""
        record = {
            "id": 2, "ast": 0, "blk": 0, "dreb": 0,
            "fg3_pct": None, "fg3a": 0, "fg3m": 0,
            "fg_pct": None, "fga": 0, "fgm": 0,
            "ft_pct": None, "fta": 0, "ftm": 0,
            "min": "",   # DNP
            "oreb": 0, "pf": 0, "pts": 0, "reb": 0, "stl": 0, "turnover": 0,
            "game": {"id": 1, "date": "2024-01-15", "season": 2023,
                     "home_team_id": 1, "visitor_team_id": 2,
                     "home_team_score": 112, "visitor_team_score": 105},
            "player": {"id": 99, "first_name": "Bench", "last_name": "Player", "position": ""},
            "team": {"id": 1, "full_name": "Boston Celtics", "abbreviation": "BOS"},
        }
        df = self.cleaner.clean_player_stats({"data": [record]})
        assert df.empty


# ── Football Cleaner ───────────────────────────────────────────────────────

class TestFootballDataCleaner:

    def setup_method(self):
        self.cleaner = FootballDataCleaner()

    def _make_fixture_payload(self, home_goals=2, away_goals=1, status="FT"):
        return {"data": [{
            "fixture": {
                "id": 999,
                "date": "2024-01-15T15:00:00+00:00",
                "status": {"long": "Match Finished", "short": status},
                "referee": "M. Dean",
                "venue": {"name": "Anfield"},
            },
            "league": {
                "id": 39, "name": "Premier League", "country": "England",
                "season": 2023, "round": "Regular Season - 22",
            },
            "teams": {
                "home": {"id": 40, "name": "Liverpool", "winner": home_goals > away_goals},
                "away": {"id": 42, "name": "Arsenal",   "winner": away_goals > home_goals},
            },
            "goals": {"home": home_goals, "away": away_goals},
            "score": {"halftime": {"home": 1, "away": 0}},
        }]}

    def test_clean_fixtures_basic(self):
        df = self.cleaner.clean_fixtures(self._make_fixture_payload())
        assert len(df) == 1
        assert df.iloc[0]["home_goals"] == 2
        assert df.iloc[0]["away_goals"] == 1

    def test_clean_fixtures_goal_diff(self):
        df = self.cleaner.clean_fixtures(self._make_fixture_payload(3, 1))
        assert df.iloc[0]["goal_diff"] == 2

    def test_clean_fixtures_draw(self):
        df = self.cleaner.clean_fixtures(self._make_fixture_payload(1, 1))
        assert df.iloc[0]["is_draw"] == 1

    def test_clean_fixtures_empty(self):
        df = self.cleaner.clean_fixtures({"data": []})
        assert df.empty

    def test_clean_standings_basic(self):
        payload = {"data": [{
            "league": {
                "id": 39, "name": "Premier League", "season": 2023,
                "standings": [[
                    {
                        "rank": 1,
                        "team": {"id": 50, "name": "Manchester City"},
                        "points": 58,
                        "goalsDiff": 40,
                        "form": "WWWWW",
                        "all": {"played": 22, "win": 18, "draw": 4, "lose": 0,
                                "goals": {"for": 56, "against": 16}},
                        "home": {"played": 11, "win": 10},
                        "away": {"played": 11, "win": 8},
                    }
                ]],
            }
        }]}
        df = self.cleaner.clean_standings(payload)
        assert len(df) == 1
        assert df.iloc[0]["team_name"] == "Manchester City"
        assert df.iloc[0]["points"] == 58
        assert df.iloc[0]["win_pct"] == pytest.approx(18 / 22, rel=1e-3)
