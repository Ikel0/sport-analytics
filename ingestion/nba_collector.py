"""NBA Data Collector — BallDontLie API v1"""
import logging, time
from datetime import date, datetime, timedelta
from typing import Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ingestion.config import NBA_CONFIG
logger = logging.getLogger(__name__)

class NBACollector:
    def __init__(self):
        self.session = self._build_session()
        self.headers = {"Authorization": NBA_CONFIG.api_key}

    def _build_session(self):
        s = requests.Session()
        retry = Retry(total=NBA_CONFIG.max_retries, backoff_factor=1, status_forcelist=[429,500,502,503,504])
        s.mount("https://", HTTPAdapter(max_retries=retry))
        return s

    def _get(self, endpoint, params=None):
        url = f"{NBA_CONFIG.base_url}/{endpoint}"
        params = params or {}
        params["per_page"] = NBA_CONFIG.per_page
        all_data, page = [], 1
        while True:
            params["page"] = page
            try:
                r = self.session.get(url, headers=self.headers, params=params, timeout=NBA_CONFIG.timeout)
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if r.status_code == 429:
                    time.sleep(60); continue
                raise RuntimeError(f"HTTP error on {url}: {e}") from e
            payload = r.json()
            data = payload.get("data", [])
            all_data.extend(data)
            meta = payload.get("meta", {})
            if page >= meta.get("total_pages", 1): break
            page += 1
            time.sleep(0.3)
        logger.info(f"Collected {len(all_data)} records from /{endpoint}")
        return {"data": all_data, "collected_at": datetime.utcnow().isoformat()}

    def get_games(self, target_date=None):
        if target_date is None: target_date = date.today() - timedelta(days=1)
        return self._get("games", params={"dates[]": target_date.strftime("%Y-%m-%d")})

    def get_player_stats(self, target_date=None):
        if target_date is None: target_date = date.today() - timedelta(days=1)
        return self._get("stats", params={"dates[]": target_date.strftime("%Y-%m-%d")})

    def get_standings(self, season=None):
        if season is None:
            now = datetime.now()
            season = now.year if now.month >= 10 else now.year - 1
        return self._get("standings", params={"season": season})

    def get_teams(self):
        return self._get("teams")

    def get_season_averages(self, player_ids, season=None):
        if season is None:
            now = datetime.now()
            season = now.year if now.month >= 10 else now.year - 1
        params = {"season": season}
        for pid in player_ids:
            params.setdefault("player_ids[]", []).append(pid)
        return self._get("season_averages", params=params)
