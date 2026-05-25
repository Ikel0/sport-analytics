"""
Recommendation Model Retraining DAG
Runs every Sunday at 06:00 UTC — retrains and evaluates the recommender.
"""

import sys
from datetime import timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago

sys.path.insert(0, "/opt/airflow")

DEFAULT_ARGS = {
    "owner":            "ikel.ouedraogo",
    "depends_on_past":  False,
    "retries":          1,
    "retry_delay":      timedelta(minutes=10),
}


def build_catalog_from_snowflake(**ctx):
    """
    Build content catalog from Snowflake ANALYTICS layer.
    Falls back to synthetic catalog if Snowflake not reachable.
    """
    try:
        from transformation.snowflake_loader import SnowflakeLoader
        from models.recommender import ContentItem

        catalog = []
        with SnowflakeLoader() as loader:
            # NBA games
            rows = loader.execute_sql("""
                SELECT game_id, home_team_name, season
                FROM SPORT_ANALYTICS.STAGING.NBA_GAMES
                WHERE is_final = TRUE
                LIMIT 500
            """)
            for row in rows:
                catalog.append(ContentItem(
                    content_id=f"nba_game_{row[0]}",
                    content_type="game", sport="nba",
                    team=row[1], season=row[2],
                    popularity_score=0.7, recency_score=0.8,
                ))

            # Football fixtures
            rows = loader.execute_sql("""
                SELECT fixture_id, home_team_name, league_name, season
                FROM SPORT_ANALYTICS.STAGING.FOOTBALL_FIXTURES
                WHERE status_short = 'FT'
                LIMIT 500
            """)
            for row in rows:
                catalog.append(ContentItem(
                    content_id=f"football_game_{row[0]}",
                    content_type="game", sport="football",
                    team=row[1], league=row[2], season=row[3],
                    popularity_score=0.7, recency_score=0.8,
                ))

        print(f"Built catalog from Snowflake: {len(catalog)} items")
    except Exception as e:
        print(f"Snowflake unavailable ({e}), using synthetic catalog.")
        from models.train import build_catalog
        catalog = build_catalog()

    ctx["ti"].xcom_push(key="catalog_size", value=len(catalog))
    return catalog


def train_model(**ctx):
    """Train and save the recommendation model."""
    import joblib
    from models.recommender import SportRecommender
    from models.train import build_catalog

    catalog = build_catalog()

    recommender = SportRecommender()
    recommender.fit(catalog)

    model_path = Path("/opt/airflow/models/recommender.pkl")
    model_path.parent.mkdir(exist_ok=True)
    joblib.dump(recommender, model_path)
    print(f"Model saved → {model_path}")
    ctx["ti"].xcom_push(key="model_path", value=str(model_path))


def evaluate_model(**ctx):
    """Evaluate model and log metrics."""
    import joblib
    from models.evaluate import evaluate
    evaluate()


def upload_model_to_s3(**ctx):
    """Backup model artifact to S3."""
    import boto3
    from datetime import datetime
    from ingestion.config import AWS_CONFIG

    model_path = ctx["ti"].xcom_pull(key="model_path", task_ids="train_model")
    if not model_path:
        return

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    s3_key = f"models/recommender/recommender_{timestamp}.pkl"

    s3 = boto3.client("s3",
                      aws_access_key_id=AWS_CONFIG.access_key_id,
                      aws_secret_access_key=AWS_CONFIG.secret_access_key,
                      region_name=AWS_CONFIG.region)
    s3.upload_file(model_path, AWS_CONFIG.bucket_name, s3_key)
    # Also overwrite 'latest'
    s3.upload_file(model_path, AWS_CONFIG.bucket_name, "models/recommender/latest.pkl")
    print(f"Model backed up → s3://{AWS_CONFIG.bucket_name}/{s3_key}")


with DAG(
    dag_id="recommendation_weekly_retrain",
    description="Weekly recommender model retraining",
    default_args=DEFAULT_ARGS,
    start_date=days_ago(1),
    schedule_interval="0 6 * * 0",   # Every Sunday at 06:00 UTC
    catchup=False,
    max_active_runs=1,
    tags=["sport-analytics", "ml", "weekly"],
) as dag:

    start = EmptyOperator(task_id="start")
    end   = EmptyOperator(task_id="end")

    t_catalog = PythonOperator(
        task_id="build_catalog",
        python_callable=build_catalog_from_snowflake,
    )
    t_train = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
    )
    t_evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model,
    )
    t_upload = PythonOperator(
        task_id="upload_model_to_s3",
        python_callable=upload_model_to_s3,
    )

    start >> t_catalog >> t_train >> t_evaluate >> t_upload >> end
