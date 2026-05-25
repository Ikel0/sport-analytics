"""Training script for the Sport Content Recommendation Engine."""
import joblib, logging, random
from pathlib import Path
from models.recommender import ContentItem, SportRecommender

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)
MODEL_PATH = Path("models/recommender.pkl")

NBA_TEAMS = [
    "Los Angeles Lakers","Boston Celtics","Golden State Warriors","Miami Heat",
    "Milwaukee Bucks","Denver Nuggets","Phoenix Suns","Philadelphia 76ers",
    "Dallas Mavericks","Memphis Grizzlies","Oklahoma City Thunder","Cleveland Cavaliers",
]
NBA_PLAYERS = [
    "LeBron James","Stephen Curry","Giannis Antetokounmpo","Luka Doncic",
    "Nikola Jokic","Kevin Durant","Joel Embiid","Jayson Tatum",
    "Anthony Davis","Damian Lillard","Shai Gilgeous-Alexander","Donovan Mitchell",
]
FOOTBALL_TEAMS = {
    "Premier League": ["Manchester City","Arsenal","Liverpool","Chelsea","Manchester United","Tottenham","Aston Villa","Newcastle"],
    "Ligue 1":        ["Paris Saint-Germain","Monaco","Marseille","Lyon","Lille","Nice","Lens","Brest"],
    "La Liga":        ["Real Madrid","Barcelona","Atletico Madrid","Real Sociedad","Athletic Bilbao","Villarreal","Sevilla","Girona"],
    "Serie A":        ["Inter Milan","AC Milan","Juventus","Napoli","Roma","Lazio","Atalanta","Bologna"],
}
FOOTBALL_PLAYERS = [
    "Kylian Mbappé","Erling Haaland","Vinicius Junior","Mohamed Salah",
    "Bukayo Saka","Rodri","Jude Bellingham","Lautaro Martinez",
    "Rafael Leao","Victor Osimhen","Phil Foden","Marcus Rashford",
]


def build_catalog() -> list:
    catalog, i = [], 1
    for season in [2022, 2023, 2024]:
        for _ in range(60):
            home = random.choice(NBA_TEAMS)
            catalog.append(ContentItem(f"nba_game_{i}","game","nba",team=home,season=season,
                popularity_score=round(random.uniform(0.3,1.0),2),
                recency_score=round((season-2022)/2+random.uniform(0,0.3),2))); i+=1
    for player in NBA_PLAYERS:
        for season in [2022,2023,2024]:
            catalog.append(ContentItem(f"nba_player_{i}","player","nba",
                team=random.choice(NBA_TEAMS),player=player,season=season,
                popularity_score=round(random.uniform(0.5,1.0),2),
                recency_score=round((season-2022)/2,2))); i+=1
    for team in NBA_TEAMS:
        for season in [2023,2024]:
            catalog.append(ContentItem(f"nba_team_{i}","team","nba",team=team,season=season,
                popularity_score=round(random.uniform(0.4,0.9),2),
                recency_score=round((season-2022)/2,2))); i+=1
    for league, teams in FOOTBALL_TEAMS.items():
        for season in [2022,2023,2024]:
            for _ in range(40):
                catalog.append(ContentItem(f"football_game_{i}","game","football",
                    team=random.choice(teams),league=league,season=season,
                    popularity_score=round(random.uniform(0.3,1.0),2),
                    recency_score=round((season-2022)/2+random.uniform(0,0.3),2))); i+=1
    for player in FOOTBALL_PLAYERS:
        for league, teams in FOOTBALL_TEAMS.items():
            catalog.append(ContentItem(f"football_player_{i}","player","football",
                team=random.choice(teams),player=player,league=league,season=2024,
                popularity_score=round(random.uniform(0.5,1.0),2),recency_score=0.9)); i+=1
    for league, teams in FOOTBALL_TEAMS.items():
        for team in teams:
            catalog.append(ContentItem(f"football_team_{i}","team","football",
                team=team,league=league,season=2024,
                popularity_score=round(random.uniform(0.4,0.95),2),recency_score=0.85)); i+=1
    logger.info(f"Catalog built: {len(catalog)} items")
    return catalog


def train():
    catalog = build_catalog()
    rec = SportRecommender()
    rec.fit(catalog)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(rec, MODEL_PATH)
    logger.info(f"Model saved → {MODEL_PATH}")
    from models.recommender import UserProfile
    profile = UserProfile(user_id="test",sport_preferences={"nba":0.7,"football":0.3},
        favorite_teams=["Los Angeles Lakers","Paris Saint-Germain"],
        favorite_players=["LeBron James"],consultation_history=["nba_game_1","nba_game_2"])
    recs = rec.recommend(profile, n=5)
    logger.info(f"Sample recs:\n{recs.to_string()}")


if __name__ == "__main__":
    train()
