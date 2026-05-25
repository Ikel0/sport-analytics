"""
Sport Content Recommendation Engine — Content-based filtering.
"""
import logging
from dataclasses import dataclass, field
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    user_id: str
    sport_preferences: dict = field(default_factory=dict)
    favorite_teams: list = field(default_factory=list)
    favorite_players: list = field(default_factory=list)
    consultation_history: list = field(default_factory=list)


@dataclass
class ContentItem:
    content_id: str
    content_type: str
    sport: str
    team: str = ""
    player: str = ""
    league: str = ""
    season: int = 0
    popularity_score: float = 0.5
    recency_score: float = 0.5


class SportRecommender:
    SPORT_MAP = {"nba": 0, "football": 1}
    TYPE_MAP  = {"game": 0, "player": 1, "team": 2, "stat_summary": 3}

    def __init__(self):
        self.content_df    = pd.DataFrame()
        self.feature_matrix = np.array([])
        self.scaler        = MinMaxScaler()
        self.is_fitted     = False

    def fit(self, catalog: list) -> "SportRecommender":
        if not catalog:
            raise ValueError("Content catalog cannot be empty.")
        rows = [{
            "content_id":   c.content_id,
            "content_type": c.content_type,
            "sport":        c.sport,
            "team":         c.team,
            "player":       c.player,
            "league":       c.league,
            "season":       c.season,
            "popularity_score": c.popularity_score,
            "recency_score":    c.recency_score,
            "sport_enc": self.SPORT_MAP.get(c.sport.lower(), -1),
            "type_enc":  self.TYPE_MAP.get(c.content_type.lower(), -1),
        } for c in catalog]
        self.content_df = pd.DataFrame(rows)
        matrix = self.content_df[["sport_enc","type_enc","popularity_score","recency_score"]].values.astype(float)
        self.feature_matrix = self.scaler.fit_transform(matrix)
        self.is_fitted = True
        logger.info(f"Recommender fitted on {len(catalog)} items.")
        return self

    def _build_user_vector(self, profile: UserProfile) -> np.ndarray:
        if not self.is_fitted:
            raise RuntimeError("Call .fit() before recommending.")
        sport_score = profile.sport_preferences.get("nba", 0.5)
        sport_enc   = sport_score * self.SPORT_MAP["nba"] + (1 - sport_score) * self.SPORT_MAP["football"]
        type_enc    = np.mean(list(self.TYPE_MAP.values()))
        if profile.consultation_history:
            seen = self.content_df[self.content_df["content_id"].isin(profile.consultation_history)]
            if not seen.empty:
                h = seen[["sport_enc","type_enc","popularity_score","recency_score"]].values.astype(float).mean(axis=0)
                sport_enc, type_enc = h[0], h[1]
        return self.scaler.transform(np.array([[sport_enc, type_enc, 0.7, 0.8]]))

    def recommend(self, profile: UserProfile, n: int = 10,
                  sport_filter: str = None, exclude_seen: bool = True) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("Call .fit() before recommending.")
        user_vec = self._build_user_vector(profile)
        sims     = cosine_similarity(user_vec, self.feature_matrix)[0]
        df       = self.content_df.copy()
        df["similarity_score"] = sims
        if exclude_seen and profile.consultation_history:
            df = df[~df["content_id"].isin(profile.consultation_history)]
        if sport_filter:
            df = df[df["sport"].str.lower() == sport_filter.lower()]
        if profile.favorite_teams:
            df.loc[df["team"].isin(profile.favorite_teams), "similarity_score"] *= 1.25
        if profile.favorite_players:
            df.loc[df["player"].isin(profile.favorite_players), "similarity_score"] *= 1.20
        return (df.sort_values("similarity_score", ascending=False)
                  .head(n)
                  [["content_id","content_type","sport","team","player","league","season","similarity_score"]]
                  .reset_index(drop=True))

    def get_similar_content(self, content_id: str, n: int = 5) -> pd.DataFrame:
        if not self.is_fitted:
            raise RuntimeError("Call .fit() before querying.")
        idx = self.content_df.index[self.content_df["content_id"] == content_id]
        if len(idx) == 0:
            raise ValueError(f"Content '{content_id}' not found in catalog.")
        sims = cosine_similarity(self.feature_matrix[idx[0]].reshape(1,-1), self.feature_matrix)[0]
        df   = self.content_df.copy()
        df["similarity_score"] = sims
        df   = df[df["content_id"] != content_id]
        return (df.sort_values("similarity_score", ascending=False)
                  .head(n)
                  [["content_id","content_type","sport","team","player","similarity_score"]]
                  .reset_index(drop=True))
