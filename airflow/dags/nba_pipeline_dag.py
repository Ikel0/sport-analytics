"""
NBA Data Pipeline DAG
Runs daily at 08:00 UTC — collects yesterday's games & stats,
uploads to S3, loads into Snowflake, runs SQL transformations.
"""

import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

# Make project modules importable inside Airflow
sys.path.insert(0, "/opt/airflow")

# ── Default args ───────────────────────────────────────────────────────────
DEFAULT_ARGS = {
    "owner":            "ikel.ouedraogo",
    "depends_on_past":  False,
    "email_on_failure": False,
    "email_on_retry":   False,
    "retries":          2,
    "retry_delay":      timedelta(minutes=5),
}

# ── Task functions ─────────────────────────────────────────────────────────

def collect_games(**ctx):
    """Fetch NBA games from BallDontLie API and upload to S3."""
    from ingestion.nba_collector import NBACollector
    from ingestion.s3_uploader import S3Uploader

    execution_date = ctx["execution_date"].date()
    # Collect for the day before execution
    target_date = execution_date - timedelta(days=1)

    collector = NBACollector()
    uploader  = S3Uploader()

    data = collector.get_games(target_date)
    uri  = uploader.upload_nba_games(data, target_date)

    ctx["ti"].xcom_push(key="games_s3_uri", value=uri)
    ctx["ti"].xcom_push(key="target_date",  value=str(target_date))
    print(f"Games uploaded → {uri} ({len(data.get('data', []))} records)")


def collect_player_stats(**ctx):
    """Fetch NBA player box scores and upload to S3."""
    from ingestion.nba_collector import NBACollector
    from ingestion.s3_uploader import S3Uploader

    target_date_str = ctx["ti"].xcom_pull(key="target_date", task_ids="collect_games")
    target_date = date.fromisoformat(target_date_str)

    collector = NBACollector()
    uploader  = S3Uploader()

    data = collector.get_player_stats(target_date)
    uri  = uploader.upload_nba_player_stats(data, target_date)

    ctx["ti"].xcom_push(key="stats_s3_uri", value=uri)
    print(f"Player stats uploaded → {uri} ({len(data.get('data', []))} records)")


def collect_standings(**ctx):
    """Fetch NBA standings (runs weekly, skips if already done today)."""
    from ingestion.nba_collector import NBACollector
    from ingestion.s3_uploader import S3Uploader

    execution_date = ctx["execution_date"]
    # Only refresh standings on Mondays
    if execution_date.weekday() != 0:
        print("Skipping standings refresh (not Monday).")
        return

    collector = NBACollector()
    uploader  = S3Uploader()

    data = collector.get_standings()
    uri  = uploader.upload_nba_standings(data, execution_date.date())
    print(f"Standings uploaded → {uri}")


def clean_and_load_games(**ctx):
    """Clean raw game data and load into Snowflake RAW schema."""
    import json, boto3
    from ingestion.config import AWS_CONFIG, SNOWFLAKE_CONFIG
    from transformation.cleaner import NBADataCleaner
    from transformation.snowflake_loader import SnowflakeLoader

    uri = ctx["ti"].xcom_pull(key="games_s3_uri", task_ids="collect_games")
    bucket, key = uri.replace("s3://", "").split("/", 1)
    if key.endswith(".gz"):
        import gzip
        s3 = boto3.client("s3",
                          aws_access_key_id=AWS_CONFIG.access_key_id,
                          aws_secret_access_key=AWS_CONFIG.secret_access_key,
                          region_name=AWS_CONFIG.region)
        obj = s3.get_object(Bucket=bucket, Key=key)
        raw_json = json.loads(gzip.decompress(obj["Body"].read()))
    else:
        raw_json = {}

    cleaner = NBADataCleaner()
    df = cleaner.clean_games(raw_json)

    if df.empty:
        print("No games to load today.")
        return

    with SnowflakeLoader() as loader:
        n = loader.load_dataframe(df, table="NBA_GAMES", schema="raw")
    print(f"Loaded {n} game rows into Snowflake RAW.")


def clean_and_load_stats(**ctx):
    """Clean player stats and load into Snowflake RAW schema."""
    import json, gzip, boto3
    from ingestion.config import AWS_CONFIG
    from transformation.cleaner import NBADataCleaner
    from transformation.snowflake_loader import SnowflakeLoader

    uri = ctx["ti"].xcom_pull(key="stats_s3_uri", task_ids="collect_player_stats")
    bucket, key = uri.replace("s3://", "").split("/", 1)

    s3 = boto3.client("s3",
                      aws_access_key_id=AWS_CONFIG.access_key_id,
                      aws_secret_access_key=AWS_CONFIG.secret_access_key,
                      region_name=AWS_CONFIG.region)
    obj = s3.get_object(Bucket=bucket, Key=key)
    raw_json = json.loads(gzip.decompress(obj["Body"].read()))

    cleaner = NBADataCleaner()
    df = cleaner.clean_player_stats(raw_json)

    if df.empty:
        print("No player stats to load.")
        return

    with SnowflakeLoader() as loader:
        n = loader.load_dataframe(df, table="NBA_PLAYER_STATS", schema="raw")
    print(f"Loaded {n} player stat rows into Snowflake RAW.")


def run_staging_transformations(**ctx):
    """Run SQL transformations: RAW → STAGING (silver layer)."""
    from transformation.snowflake_loader import SnowflakeLoader

    sql_dir = Path("/opt/airflow/transformation/sql/staging")
    with SnowflakeLoader() as loader:
        for sql_file in sorted(sql_dir.glob("*.sql")):
            print(f"Running staging SQL: {sql_file.name}")
            loader.run_transformation(str(sql_file))


def run_analytics_transformations(**ctx):
    """Run SQL transformations: STAGING → ANALYTICS (gold layer)."""
    from transformation.snowflake_loader import SnowflakeLoader

    sql_dir = Path("/opt/airflow/transformation/sql/analytics")
    nba_files = ["nba_team_kpis.sql", "nba_player_kpis.sql"]

    with SnowflakeLoader() as loader:
        for fname in nba_files:
            fpath = sql_dir / fname
            if fpath.exists():
                print(f"Running analytics SQL: {fname}")
                loader.run_transformation(str(fpath))


# ── DAG definition ─────────────────────────────────────────────────────────

with DAG(
    dag_id="nba_daily_pipeline",
    description="NBA data pipeline: API → S3 → Snowflake → KPIs",
    default_args=DEFAULT_ARGS,
    start_date=days_ago(1),
    schedule_interval="0 8 * * *",   # Every day at 08:00 UTC
    catchup=False,
    max_active_runs=1,
    tags=["sport-analytics", "nba", "daily"],
) as dag:

    start = EmptyOperator(task_id="start")
    end   = EmptyOperator(task_id="end")

    t_collect_games = PythonOperator(
        task_id="collect_games",
        python_callable=collect_games,
    )

    t_collect_stats = PythonOperator(
        task_id="collect_player_stats",
        python_callable=collect_player_stats,
    )

    t_collect_standings = PythonOperator(
        task_id="collect_standings",
        python_callable=collect_standings,
    )

    t_load_games = PythonOperator(
        task_id="clean_and_load_games",
        python_callable=clean_and_load_games,
    )

    t_load_stats = PythonOperator(
        task_id="clean_and_load_stats",
        python_callable=clean_and_load_stats,
    )

    t_staging = PythonOperator(
        task_id="run_staging_transformations",
        python_callable=run_staging_transformations,
    )

    t_analytics = PythonOperator(
        task_id="run_analytics_transformations",
        python_callable=run_analytics_transformations,
    )

    # ── Pipeline graph
    #
    # start
    #   ├── collect_games ──► clean_and_load_games ──┐
    #   ├── collect_stats ──► clean_and_load_stats ──┤
    #   └── collect_standings                         │
    #                                                  ▼
    #                                     run_staging_transformations
    #                                                  │
    #                                                  ▼
    #                                    run_analytics_transformations
    #                                                  │
    #                                                 end

    start >> [t_collect_games, t_collect_stats, t_collect_standings]
    t_collect_games >> t_load_games
    t_collect_stats >> t_load_stats
    [t_load_games, t_load_stats, t_collect_standings] >> t_staging
    t_staging >> t_analytics >> end
