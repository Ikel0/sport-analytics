"""Football Data Collector — API-Football v3"""
import logging, time
from datetime import date, datetime, timedelta
from typing import Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from ingestion.config import FOOTBALL_CONFIG
logger = logging.getLogger(__name__)

class FootballCollector:
    def __init__(self):
        self.session = self._build_session()
        self.headers = {"x-rapidapi-host": "v3.football.api-sports.io", "x-rapidapi-key": FOOTBALL_CONFIG.api_key}

    def _build_session(self):
        s = requests.Session()
        retry = Retry(total=FOOTBALL_CONFIG.max_retries, backoff_factor=2, status_forcelist=[429,500,502,503,504])
        s.mount("https://", HTTPAdapter(max_retries=retry))
        return s

    def _get(self, endpoint, params=None):
        url = f"{FOOTBALL_CONFIG.base_url}/{endpoint}"
        try:
            r = self.session.get(url, headers=self.headers, params=params or {}, timeout=FOOTBALL_CONFIG.timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if r.status_code == 429:
                time.sleep(30); return self._get(endpoint, params)
            raise RuntimeError(f"HTTP error: {e}") from e
        payload = r.json()
        errors = payload.get("errors", {})
        if errors: raise RuntimeError(f"API-Football error: {errors}")
        results = payload.get("response", [])
        logger.info(f"Collected {len(results)} records from /{endpoint}")
        return {"data": results, "collected_at": datetime.utcnow().isoformat(), "params": params, "paging": payload.get("paging", {})}

    def _get_paginated(self, endpoint, params=None):
        params = params or {}
        all_data, page = [], 1
        while True:
            params["page"] = page
            resp = self._get(endpoint, params)
            all_data.extend(resp.get("data", []))
            total = resp.get("paging", {}).get("total", 1)
            if page >= total: break
            page += 1; time.sleep(0.5)
        return {"data": all_data, "collected_at": datetime.utcnow().isoformat(), "params": params}

    def get_fixtures(self, target_date=None, league_id=None, season=None):
        if target_date is None: target_date = date.today() - timedelta(days=1)
        if season is None: season = target_date.year if target_date.month >= 8 else target_date.year - 1
        params = {"date": target_date.strftime("%Y-%m-%d"), "season": season}
        if league_id: params["league"] = league_id
        return self._get("fixtures", params)

    def get_standings(self, league_id, season):
        return self._get("standings", {"league": league_id, "season": season})

    def get_player_stats(self, league_id, season, team_id=None):
        params = {"league": league_id, "season": season}
        if team_id: params["team"] = team_id
        return self._get_paginated("players", params)

    def get_top_scorers(self, league_id, season):
        return self._get("players/topscorers", {"league": league_id, "season": season})

    def get_fixture_stats(self, fixture_id):
        return self._get("fixtures/statistics", {"fixture": fixture_id})
