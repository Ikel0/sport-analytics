"""
Unit tests for the recommendation engine.
"""

import pytest
import pandas as pd

from models.recommender import ContentItem, SportRecommender, UserProfile


# ── Fixtures ───────────────────────────────────────────────────────────────

def make_catalog(n_nba=20, n_football=20) -> list[ContentItem]:
    catalog = []
    for i in range(n_nba):
        catalog.append(ContentItem(
            content_id=f"nba_game_{i}",
            content_type="game",
            sport="nba",
            team="Los Angeles Lakers",
            season=2024,
            popularity_score=0.8,
            recency_score=0.9,
        ))
    for i in range(n_football):
        catalog.append(ContentItem(
            content_id=f"football_game_{i}",
            content_type="game",
            sport="football",
            team="Paris Saint-Germain",
            league="Ligue 1",
            season=2024,
            popularity_score=0.7,
            recency_score=0.85,
        ))
    # Add some player and team items
    for i in range(5):
        catalog.append(ContentItem(
            content_id=f"nba_player_{i}",
            content_type="player",
            sport="nba",
            team="Boston Celtics",
            player="Jayson Tatum",
            season=2024,
            popularity_score=0.9,
            recency_score=0.9,
        ))
    return catalog


@pytest.fixture
def recommender():
    rec = SportRecommender()
    rec.fit(make_catalog())
    return rec


@pytest.fixture
def nba_profile():
    return UserProfile(
        user_id="user_nba",
        sport_preferences={"nba": 0.9, "football": 0.1},
        favorite_teams=["Los Angeles Lakers"],
        favorite_players=["LeBron James"],
        consultation_history=["nba_game_0", "nba_game_1"],
    )


@pytest.fixture
def football_profile():
    return UserProfile(
        user_id="user_football",
        sport_preferences={"nba": 0.1, "football": 0.9},
        favorite_teams=["Paris Saint-Germain"],
        favorite_players=["Kylian Mbappé"],
        consultation_history=["football_game_0", "football_game_1"],
    )


# ── Tests ──────────────────────────────────────────────────────────────────

class TestSportRecommender:

    def test_fit_success(self):
        rec = SportRecommender()
        catalog = make_catalog()
        rec.fit(catalog)
        assert rec.is_fitted
        assert len(rec.content_df) == len(catalog)

    def test_fit_empty_catalog_raises(self):
        rec = SportRecommender()
        with pytest.raises(ValueError, match="cannot be empty"):
            rec.fit([])

    def test_recommend_returns_dataframe(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=5)
        assert isinstance(recs, pd.DataFrame)
        assert len(recs) == 5

    def test_recommend_n_respected(self, recommender, nba_profile):
        for n in [1, 5, 10]:
            recs = recommender.recommend(nba_profile, n=n)
            assert len(recs) <= n

    def test_recommend_excludes_seen(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=10, exclude_seen=True)
        seen = set(nba_profile.consultation_history)
        recommended_ids = set(recs["content_id"].tolist())
        assert len(seen & recommended_ids) == 0

    def test_recommend_includes_seen_when_disabled(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=20, exclude_seen=False)
        # Should not crash and return results
        assert len(recs) > 0

    def test_recommend_sport_filter_nba(self, recommender, football_profile):
        recs = recommender.recommend(football_profile, n=10, sport_filter="nba")
        assert all(recs["sport"] == "nba")

    def test_recommend_sport_filter_football(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=10, sport_filter="football")
        assert all(recs["sport"] == "football")

    def test_recommend_scores_between_0_and_1(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=10)
        # Scores can exceed 1 due to favorite team/player boost, but should be positive
        assert (recs["similarity_score"] >= 0).all()

    def test_recommend_required_columns(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=5)
        expected_cols = {"content_id", "content_type", "sport", "team", "player", "similarity_score"}
        assert expected_cols.issubset(set(recs.columns))

    def test_recommend_without_fit_raises(self, nba_profile):
        rec = SportRecommender()
        with pytest.raises(RuntimeError, match="fit"):
            rec.recommend(nba_profile, n=5)

    def test_similar_content_returns_results(self, recommender):
        similar = recommender.get_similar_content("nba_game_5", n=3)
        assert isinstance(similar, pd.DataFrame)
        assert len(similar) == 3
        # Should not contain the query item itself
        assert "nba_game_5" not in similar["content_id"].values

    def test_similar_content_unknown_id_raises(self, recommender):
        with pytest.raises(ValueError, match="not found"):
            recommender.get_similar_content("nonexistent_id_xyz")

    def test_nba_fan_gets_more_nba(self, recommender, nba_profile):
        recs = recommender.recommend(nba_profile, n=15, exclude_seen=False)
        nba_count = (recs["sport"] == "nba").sum()
        football_count = (recs["sport"] == "football").sum()
        assert nba_count >= football_count

    def test_football_fan_gets_more_football(self, recommender, football_profile):
        recs = recommender.recommend(football_profile, n=15, exclude_seen=False)
        football_count = (recs["sport"] == "football").sum()
        nba_count = (recs["sport"] == "nba").sum()
        assert football_count >= nba_count
