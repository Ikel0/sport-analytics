"""
Unit tests for ingestion layer.
Uses mocked HTTP responses — no real API calls.
"""

import json
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
import responses

from ingestion.nba_collector import NBACollector
from ingestion.football_collector import FootballCollector


# ── Fixtures ───────────────────────────────────────────────────────────────

NBA_GAMES_RESPONSE = {
    "data": [
        {
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
    ],
    "meta": {"total_pages": 1, "current_page": 1, "next_page": None, "per_page": 100, "total_count": 1},
}

NBA_STATS_RESPONSE = {
    "data": [
        {
            "id": 101,
            "ast": 5, "blk": 1, "dreb": 6, "fg3_pct": 0.38,
            "fg3a": 8, "fg3m": 3, "fg_pct": 0.51, "fga": 18, "fgm": 9,
            "ft_pct": 0.85, "fta": 7, "ftm": 6,
            "min": "35:22", "oreb": 2, "pf": 3, "pts": 27, "reb": 8,
            "stl": 2, "turnover": 3,
            "game": {
                "id": 1, "date": "2024-01-15", "season": 2023,
                "home_team_id": 1, "visitor_team_id": 2,
                "home_team_score": 112, "visitor_team_score": 105,
            },
            "player": {"id": 10, "first_name": "Jayson", "last_name": "Tatum", "position": "SF"},
            "team": {"id": 1, "full_name": "Boston Celtics", "abbreviation": "BOS"},
        }
    ],
    "meta": {"total_pages": 1, "current_page": 1, "per_page": 100, "total_count": 1},
}

FOOTBALL_FIXTURES_RESPONSE = {
    "response": [
        {
            "fixture": {"id": 999, "date": "2024-01-15T15:00:00+00:00",
                        "status": {"long": "Match Finished", "short": "FT"},
                        "referee": "M. Dean", "venue": {"name": "Anfield"}},
            "league": {"id": 39, "name": "Premier League", "country": "England",
                       "season": 2023, "round": "Regular Season - 22"},
            "teams": {
                "home": {"id": 40, "name": "Liverpool", "winner": True},
                "away": {"id": 42, "name": "Arsenal",   "winner": False},
            },
            "goals": {"home": 2, "away": 1},
            "score": {"halftime": {"home": 1, "away": 0}},
        }
    ],
    "errors": {},
    "paging": {"current": 1, "total": 1},
}


# ── NBACollector tests ─────────────────────────────────────────────────────

class TestNBACollector:

    @responses.activate
    def test_get_games_success(self):
        responses.add(
            responses.GET,
            "https://api.balldontlie.io/v1/games",
            json=NBA_GAMES_RESPONSE,
            status=200,
        )
        collector = NBACollector()
        result = collector.get_games(date(2024, 1, 15))

        assert "data" in result
        assert len(result["data"]) == 1
        game = result["data"][0]
        assert game["id"] == 1
        assert game["home_team_score"] == 112

    @responses.activate
    def test_get_player_stats_success(self):
        responses.add(
            responses.GET,
            "https://api.balldontlie.io/v1/stats",
            json=NBA_STATS_RESPONSE,
            status=200,
        )
        collector = NBACollector()
        result = collector.get_player_stats(date(2024, 1, 15))

        assert len(result["data"]) == 1
        assert result["data"][0]["pts"] == 27

    @responses.activate
    def test_get_games_empty_response(self):
        responses.add(
            responses.GET,
            "https://api.balldontlie.io/v1/games",
            json={"data": [], "meta": {"total_pages": 1}},
            status=200,
        )
        collector = NBACollector()
        result = collector.get_games(date(2024, 1, 15))
        assert result["data"] == []

    @responses.activate
    def test_get_games_http_error(self):
        responses.add(
            responses.GET,
            "https://api.balldontlie.io/v1/games",
            json={"error": "Server Error"},
            status=500,
        )
        collector = NBACollector()
        with pytest.raises(RuntimeError):
            collector.get_games(date(2024, 1, 15))

    @responses.activate
    def test_pagination(self):
        """Test that paginated results are correctly merged."""
        page1 = {
            "data": [{"id": 1}],
            "meta": {"total_pages": 2, "current_page": 1},
        }
        page2 = {
            "data": [{"id": 2}],
            "meta": {"total_pages": 2, "current_page": 2},
        }
        responses.add(responses.GET, "https://api.balldontlie.io/v1/games", json=page1, status=200)
        responses.add(responses.GET, "https://api.balldontlie.io/v1/games", json=page2, status=200)

        collector = NBACollector()
        result = collector.get_games(date(2024, 1, 15))
        assert len(result["data"]) == 2


# ── FootballCollector tests ────────────────────────────────────────────────

class TestFootballCollector:

    @responses.activate
    def test_get_fixtures_success(self):
        responses.add(
            responses.GET,
            "https://v3.football.api-sports.io/fixtures",
            json=FOOTBALL_FIXTURES_RESPONSE,
            status=200,
        )
        collector = FootballCollector()
        result = collector.get_fixtures(date(2024, 1, 15), league_id=39)

        assert len(result["data"]) == 1
        fixture = result["data"][0]
        assert fixture["fixture"]["id"] == 999
        assert fixture["goals"]["home"] == 2

    @responses.activate
    def test_get_fixtures_api_error(self):
        responses.add(
            responses.GET,
            "https://v3.football.api-sports.io/fixtures",
            json={"response": [], "errors": {"token": "Invalid API key"}},
            status=200,
        )
        collector = FootballCollector()
        with pytest.raises(RuntimeError, match="API-Football error"):
            collector.get_fixtures(date(2024, 1, 15), league_id=39)

    @responses.activate
    def test_get_standings_success(self):
        mock_response = {
            "response": [{"league": {"id": 39, "name": "Premier League",
                                     "season": 2023, "standings": []}}],
            "errors": {},
            "paging": {"current": 1, "total": 1},
        }
        responses.add(
            responses.GET,
            "https://v3.football.api-sports.io/standings",
            json=mock_response,
            status=200,
        )
        collector = FootballCollector()
        result = collector.get_standings(league_id=39, season=2023)
        assert "data" in result
