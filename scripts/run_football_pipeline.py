"""
Manual Football Pipeline Runner
Triggers the full football pipeline for a given date without Airflow.

Usage:
    python scripts/run_football_pipeline.py
    python scripts/run_football_pipeline.py --date 2024-03-15
    python scripts/run_football_pipeline.py --league 39 --season 2023
    python scripts/run_football_pipeline.py --skip-snowflake
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
logger = logging.getLogger("football_pipeline")

TRACKED_LEAGUES = {
    39:  {"name": "Premier League", "season": 2023},
    61:  {"name": "Ligue 1",        "season": 2023},
    140: {"name": "La Liga",        "season": 2023},
    135: {"name": "Serie A",        "season": 2023},
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run football data pipeline manually.")
    parser.add_argument("--date", type=str, default=None,
                        help="Target date (YYYY-MM-DD). Defaults to yesterday.")
    parser.add_argument("--league", type=int, default=None,
                        help="Single league ID to process. Defaults to all leagues.")
    parser.add_argument("--season", type=int, default=2023,
                        help="Season year (default: 2023).")
    parser.add_argument("--skip-snowflake", action="store_true")
    parser.add_argument("--skip-s3", action="store_true")
    parser.add_argument("--standings-only", action="store_true",
                        help="Only refresh standings (no fixture collection).")
    return parser.parse_args()


def run(target_date: date, leagues: dict, skip_snowflake=False,
        skip_s3=False, standings_only=False):
    logger.info(f"Starting Football pipeline for {target_date}")
    logger.info(f"Leagues: {[v['name'] for v in leagues.values()]}")
    logger.info("=" * 60)

    from ingestion.football_collector import FootballCollector
    collector = FootballCollector()
    all_fixtures, all_standings = [], []

    for league_id, info in leagues.items():
        logger.info(f"Processing {info['name']} (id={league_id})...")

        # Standings
        logger.info(f"  Collecting standings...")
        try:
            standings = collector.get_standings(league_id, info["season"])
            all_standings.append((league_id, info["season"], standings))
            logger.info(f"  Standings: {len(standings.get('data', []))} entries")
        except Exception as e:
            logger.error(f"  Standings failed: {e}")

        if standings_only:
            continue

        # Fixtures
        logger.info(f"  Collecting fixtures for {target_date}...")
        try:
            fixtures = collector.get_fixtures(target_date, league_id=league_id,
                                              season=info["season"])
            n = len(fixtures.get("data", []))
            logger.info(f"  Fixtures: {n} matches")
            if n > 0:
                all_fixtures.append((league_id, fixtures))
        except Exception as e:
            logger.error(f"  Fixtures failed: {e}")

    # ── Upload to S3
    if not skip_s3 and (all_fixtures or all_standings):
        logger.info("Uploading to S3...")
        from ingestion.s3_uploader import S3Uploader
        uploader = S3Uploader()
        for league_id, fixtures in all_fixtures:
            uri = uploader.upload_football_matches(fixtures, league_id, target_date)
            logger.info(f"  Fixtures [{league_id}] → {uri}")
        for league_id, season, standings in all_standings:
            uri = uploader.upload_football_standings(standings, league_id, season)
            logger.info(f"  Standings [{league_id}] → {uri}")

    # ── Clean data
    logger.info("Cleaning data...")
    from transformation.cleaner import FootballDataCleaner
    import pandas as pd
    cleaner = FootballDataCleaner()
    fixture_dfs   = []
    standings_dfs = []

    for _, fixtures in all_fixtures:
        df = cleaner.clean_fixtures(fixtures)
        if not df.empty:
            fixture_dfs.append(df)

    for _, _, standings in all_standings:
        df = cleaner.clean_standings(standings)
        if not df.empty:
            standings_dfs.append(df)

    combined_fixtures  = pd.concat(fixture_dfs,   ignore_index=True) if fixture_dfs  else pd.DataFrame()
    combined_standings = pd.concat(standings_dfs, ignore_index=True) if standings_dfs else pd.DataFrame()
    logger.info(f"  Fixtures cleaned:  {len(combined_fixtures)} rows")
    logger.info(f"  Standings cleaned: {len(combined_standings)} rows")

    # ── Load to Snowflake
    if not skip_snowflake:
        logger.info("Loading to Snowflake...")
        from transformation.snowflake_loader import SnowflakeLoader
        with SnowflakeLoader() as loader:
            if not combined_fixtures.empty:
                n = loader.load_dataframe(combined_fixtures, "FOOTBALL_FIXTURES", schema="raw")
                logger.info(f"  Loaded {n} fixture rows → RAW.FOOTBALL_FIXTURES")
            if not combined_standings.empty:
                n = loader.load_dataframe(combined_standings, "FOOTBALL_STANDINGS", schema="raw")
                logger.info(f"  Loaded {n} standings rows → RAW.FOOTBALL_STANDINGS")

            sql_dir = Path("transformation/sql")
            for sql_file in sorted((sql_dir / "staging").glob("football_*.sql")):
                logger.info(f"  Running staging: {sql_file.name}")
                loader.run_transformation(str(sql_file))
            for sql_file in sorted((sql_dir / "analytics").glob("football_*.sql")):
                logger.info(f"  Running analytics: {sql_file.name}")
                loader.run_transformation(str(sql_file))
    else:
        logger.info("Skipping Snowflake load (--skip-snowflake).")

    logger.info("=" * 60)
    logger.info("Football pipeline completed successfully.")


if __name__ == "__main__":
    args = parse_args()
    target = date.fromisoformat(args.date) if args.date else date.today() - timedelta(days=1)
    leagues = {args.league: TRACKED_LEAGUES[args.league]} if args.league else TRACKED_LEAGUES
    run(target, leagues, skip_snowflake=args.skip_snowflake,
        skip_s3=args.skip_s3, standings_only=args.standings_only)
