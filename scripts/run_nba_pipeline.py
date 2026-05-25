"""
Manual NBA Pipeline Runner
Triggers the full NBA pipeline for a given date without Airflow.

Usage:
    python scripts/run_nba_pipeline.py
    python scripts/run_nba_pipeline.py --date 2024-03-15
    python scripts/run_nba_pipeline.py --date 2024-03-15 --skip-snowflake
"""
import argparse
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nba_pipeline")


def parse_args():
    parser = argparse.ArgumentParser(description="Run NBA data pipeline manually.")
    parser.add_argument("--date", type=str, default=None,
                        help="Target date (YYYY-MM-DD). Defaults to yesterday.")
    parser.add_argument("--skip-snowflake", action="store_true",
                        help="Skip Snowflake loading (S3 upload only).")
    parser.add_argument("--skip-s3", action="store_true",
                        help="Skip S3 upload (local dry run).")
    return parser.parse_args()


def run(target_date: date, skip_snowflake: bool = False, skip_s3: bool = False):
    logger.info(f"Starting NBA pipeline for {target_date}")
    logger.info("=" * 60)

    # ── Step 1: Collect
    logger.info("Step 1/4 — Collecting NBA data from API...")
    from ingestion.nba_collector import NBACollector
    collector = NBACollector()

    games    = collector.get_games(target_date)
    stats    = collector.get_player_stats(target_date)
    standings = collector.get_standings()

    logger.info(f"  Games:     {len(games.get('data', []))} records")
    logger.info(f"  Stats:     {len(stats.get('data', []))} records")
    logger.info(f"  Standings: {len(standings.get('data', []))} records")

    # ── Step 2: Upload to S3
    if not skip_s3:
        logger.info("Step 2/4 — Uploading to S3...")
        from ingestion.s3_uploader import S3Uploader
        uploader = S3Uploader()
        uri_games    = uploader.upload_nba_games(games, target_date)
        uri_stats    = uploader.upload_nba_player_stats(stats, target_date)
        uri_standings = uploader.upload_nba_standings(standings, target_date)
        logger.info(f"  Games    → {uri_games}")
        logger.info(f"  Stats    → {uri_stats}")
        logger.info(f"  Standings → {uri_standings}")
    else:
        logger.info("Step 2/4 — Skipping S3 upload (--skip-s3).")

    # ── Step 3: Clean & transform
    logger.info("Step 3/4 — Cleaning data...")
    from transformation.cleaner import NBADataCleaner
    cleaner = NBADataCleaner()
    df_games    = cleaner.clean_games(games)
    df_stats    = cleaner.clean_player_stats(stats)
    df_standings = cleaner.clean_standings(standings)
    logger.info(f"  Games cleaned:    {len(df_games)} rows")
    logger.info(f"  Stats cleaned:    {len(df_stats)} rows")
    logger.info(f"  Standings cleaned:{len(df_standings)} rows")

    # ── Step 4: Load to Snowflake
    if not skip_snowflake:
        logger.info("Step 4/4 — Loading to Snowflake...")
        from transformation.snowflake_loader import SnowflakeLoader
        with SnowflakeLoader() as loader:
            if not df_games.empty:
                n = loader.load_dataframe(df_games, "NBA_GAMES", schema="raw")
                logger.info(f"  Loaded {n} game rows → RAW.NBA_GAMES")
            if not df_stats.empty:
                n = loader.load_dataframe(df_stats, "NBA_PLAYER_STATS", schema="raw")
                logger.info(f"  Loaded {n} stat rows → RAW.NBA_PLAYER_STATS")
            if not df_standings.empty:
                n = loader.load_dataframe(df_standings, "NBA_STANDINGS", schema="raw")
                logger.info(f"  Loaded {n} standing rows → RAW.NBA_STANDINGS")

            # Run SQL transformations
            sql_dir = Path("transformation/sql")
            for sql_file in sorted((sql_dir / "staging").glob("nba_*.sql")):
                logger.info(f"  Running staging: {sql_file.name}")
                loader.run_transformation(str(sql_file))
            for sql_file in sorted((sql_dir / "analytics").glob("nba_*.sql")):
                logger.info(f"  Running analytics: {sql_file.name}")
                loader.run_transformation(str(sql_file))
    else:
        logger.info("Step 4/4 — Skipping Snowflake load (--skip-snowflake).")

    logger.info("=" * 60)
    logger.info(f"NBA pipeline completed successfully for {target_date}")


if __name__ == "__main__":
    args = parse_args()
    if args.date:
        target = date.fromisoformat(args.date)
    else:
        target = date.today() - timedelta(days=1)
    run(target, skip_snowflake=args.skip_snowflake, skip_s3=args.skip_s3)
