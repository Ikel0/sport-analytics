import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class NBAConfig:
    base_url: str = "https://api.balldontlie.io/v1"
    api_key: str = os.getenv("BALLDONTLIE_API_KEY", "")
    timeout: int = 30
    max_retries: int = 3
    per_page: int = 100

@dataclass(frozen=True)
class FootballConfig:
    base_url: str = "https://v3.football.api-sports.io"
    api_key: str = os.getenv("APIFOOTBALL_API_KEY", "")
    timeout: int = 30
    max_retries: int = 3
    leagues: tuple = (39, 61, 140, 135)
    seasons: tuple = (2023, 2024)

@dataclass(frozen=True)
class AWSConfig:
    access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    region: str = os.getenv("AWS_REGION", "eu-west-1")
    bucket_name: str = os.getenv("S3_BUCKET_NAME", "sport-analytics-raw")

@dataclass(frozen=True)
class SnowflakeConfig:
    account: str = os.getenv("SNOWFLAKE_ACCOUNT", "")
    user: str = os.getenv("SNOWFLAKE_USER", "")
    password: str = os.getenv("SNOWFLAKE_PASSWORD", "")
    database: str = os.getenv("SNOWFLAKE_DATABASE", "SPORT_ANALYTICS")
    warehouse: str = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    role: str = os.getenv("SNOWFLAKE_ROLE", "SYSADMIN")
    schemas: dict = None
    def __post_init__(self):
        object.__setattr__(self, "schemas", {"raw": "RAW", "staging": "STAGING", "analytics": "ANALYTICS"})

class S3Paths:
    @staticmethod
    def nba_games(date): return f"raw/nba/games/{date}/games.json"
    @staticmethod
    def nba_stats(date): return f"raw/nba/stats/{date}/player_stats.json"
    @staticmethod
    def nba_standings(date): return f"raw/nba/standings/{date}/standings.json"
    @staticmethod
    def football_matches(league_id, date): return f"raw/football/matches/league_{league_id}/{date}/matches.json"
    @staticmethod
    def football_standings(league_id, season): return f"raw/football/standings/league_{league_id}/season_{season}/standings.json"
    @staticmethod
    def football_player_stats(league_id, season): return f"raw/football/player_stats/league_{league_id}/season_{season}/stats.json"

NBA_CONFIG = NBAConfig()
FOOTBALL_CONFIG = FootballConfig()
AWS_CONFIG = AWSConfig()
SNOWFLAKE_CONFIG = SnowflakeConfig()
S3 = S3Paths()
