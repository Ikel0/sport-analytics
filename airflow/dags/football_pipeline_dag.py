"""
Football Data Pipeline DAG
Runs daily at 09:00 UTC — collects fixtures, standings & player stats
for all tracked leagues, uploads to S3, loads into Snowflake.
"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

sys.path.insert(0, "/opt/airflow")

DEFAULT_ARGS = {
    "owner":            "ikel.ouedraogo",
    "depends_on_past":  False,
    "email_on_failure": False,
    "retries":          2,
    "retry_delay":      timedelta(minutes=10),
}

TRACKED_LEAGUES = {
    39:  {"name": "Premier League", "season": 2023},
    61:  {"name": "Ligue 1",        "season": 2023},
    140: {"name": "La Liga",        "season": 2023},
    135: {"name": "Serie A",        "season": 2023},
}


def collect_fixtures(**ctx):
    """Collect yesterday's fixtures for all tracked leagues."""
    from ingestion.football_collector import FootballCollector
    from ingestion.s3_uploader import S3Uploader

    execution_date = ctx["execution_date"].date()
    target_date = execution_date - timedelta(days=1)

    collector = FootballCollector()
    uploader  = S3Uploader()

    uris = {}
    for league_id, info in TRACKED_LEAGUES.items():
        try:
            data = collector.get_fixtures(target_date, league_id=league_id)
            if data.get("data"):
                uri = uploader.upload_football_matches(data, league_id, target_date)
                uris[league_id] = uri
                print(f"Fixtures [{info['name']}] → {uri}")
            else:
                print(f"No fixtures for {info['name']} on {target_date}")
        except Exception as e:
            print(f"Error collecting fixtures for league {league_id}: {e}")

    ctx["ti"].xcom_push(key="fixture_uris",  value=uris)
    ctx["ti"].xcom_push(key="target_date",   value=str(target_date))


def collect_standings(**ctx):
    """Collect standings for all leagues (weekly on Sundays)."""
    from ingestion.football_collector import FootballCollector
    from ingestion.s3_uploader import S3Uploader

    execution_date = ctx["execution_date"]
    # Refresh standings every Sunday
    if execution_date.weekday() != 6:
        print("Skipping standings refresh (not Sunday).")
        return

    collector = FootballCollector()
    uploader  = S3Uploader()

    for league_id, info in TRACKED_LEAGUES.items():
        try:
            data = collector.get_standings(league_id, info["season"])
            uri  = uploader.upload_football_standings(data, league_id, info["season"])
            print(f"Standings [{info['name']}] → {uri}")
        except Exception as e:
            print(f"Error collecting standings for league {league_id}: {e}")


def collect_player_stats(**ctx):
    """Collect player statistics (weekly on Sundays)."""
    from ingestion.football_collector import FootballCollector
    from ingestion.s3_uploader import S3Uploader

    execution_date = ctx["execution_date"]
    if execution_date.weekday() != 6:
        print("Skipping player stats refresh (not Sunday).")
        return

    collector = FootballCollector()
    uploader  = S3Uploader()

    for league_id, info in TRACKED_LEAGUES.items():
        try:
            data = collector.get_player_stats(league_id, info["season"])
            uri  = uploader.upload_football_player_stats(data, league_id, info["season"])
            print(f"Player stats [{info['name']}] → {uri}")
        except Exception as e:
            print(f"Error collecting player stats for league {league_id}: {e}")


def clean_and_load_fixtures(**ctx):
    """Clean fixture data and load into Snowflake RAW."""
    import json, gzip, boto3
    from ingestion.config import AWS_CONFIG
    from transformation.cleaner import FootballDataCleaner
    from transformation.snowflake_loader import SnowflakeLoader
    import pandas as pd

    uris = ctx["ti"].xcom_pull(key="fixture_uris", task_ids="collect_fixtures")
    if not uris:
        print("No fixture URIs to process.")
        return

    s3 = boto3.client("s3",
                      aws_access_key_id=AWS_CONFIG.access_key_id,
                      aws_secret_access_key=AWS_CONFIG.secret_access_key,
                      region_name=AWS_CONFIG.region)

    cleaner = FootballDataCleaner()
    all_dfs = []

    for league_id, uri in uris.items():
        try:
            bucket, key = uri.replace("s3://", "").split("/", 1)
            obj = s3.get_object(Bucket=bucket, Key=key)
            raw_json = json.loads(gzip.decompress(obj["Body"].read()))
            df = cleaner.clean_fixtures(raw_json)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            print(f"Error cleaning fixtures for league {league_id}: {e}")

    if not all_dfs:
        print("No fixture data to load.")
        return

    combined = pd.concat(all_dfs, ignore_index=True)
    with SnowflakeLoader() as loader:
        n = loader.load_dataframe(combined, table="FOOTBALL_FIXTURES", schema="raw")
    print(f"Loaded {n} fixture rows into Snowflake RAW.")


def run_staging_transformations(**ctx):
    from transformation.snowflake_loader import SnowflakeLoader
    sql_dir = Path("/opt/airflow/transformation/sql/staging")
    football_files = sorted(sql_dir.glob("football_*.sql"))
    with SnowflakeLoader() as loader:
        for sql_file in football_files:
            print(f"Running: {sql_file.name}")
            loader.run_transformation(str(sql_file))


def run_analytics_transformations(**ctx):
    from transformation.snowflake_loader import SnowflakeLoader
    sql_dir = Path("/opt/airflow/transformation/sql/analytics")
    football_files = ["football_team_kpis.sql", "football_player_kpis.sql"]
    with SnowflakeLoader() as loader:
        for fname in football_files:
            fpath = sql_dir / fname
            if fpath.exists():
                print(f"Running: {fname}")
                loader.run_transformation(str(fpath))


with DAG(
    dag_id="football_daily_pipeline",
    description="Football pipeline: API → S3 → Snowflake → KPIs",
    default_args=DEFAULT_ARGS,
    start_date=days_ago(1),
    schedule_interval="0 9 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["sport-analytics", "football", "daily"],
) as dag:

    start = EmptyOperator(task_id="start")
    end   = EmptyOperator(task_id="end")

    t_fixtures = PythonOperator(
        task_id="collect_fixtures",
        python_callable=collect_fixtures,
    )
    t_standings = PythonOperator(
        task_id="collect_standings",
        python_callable=collect_standings,
    )
    t_player_stats = PythonOperator(
        task_id="collect_player_stats",
        python_callable=collect_player_stats,
    )
    t_load = PythonOperator(
        task_id="clean_and_load_fixtures",
        python_callable=clean_and_load_fixtures,
    )
    t_staging = PythonOperator(
        task_id="run_staging_transformations",
        python_callable=run_staging_transformations,
    )
    t_analytics = PythonOperator(
        task_id="run_analytics_transformations",
        python_callable=run_analytics_transformations,
    )

    start >> [t_fixtures, t_standings, t_player_stats]
    t_fixtures >> t_load
    [t_load, t_standings, t_player_stats] >> t_staging
    t_staging >> t_analytics >> end
