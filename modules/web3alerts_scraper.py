"""
Web3 Alerts Scraper Module

Fetches project data from Web3 Alerts API.
"""

import json
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)


class Web3AlertsScraper:
    """Scraper for Web3 Alerts API"""

    def __init__(self, cookies_path: str):
        """
        Initialize the scraper

        Args:
            cookies_path: Path to the cookies JSON file
        """
        self.base_url = "https://web3alerts.app"
        self.session = requests.Session()
        # Set headers to mimic browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://web3alerts.app/',
            'Origin': 'https://web3alerts.app'
        })
        self.load_cookies(cookies_path)

    def load_cookies(self, cookies_path: str):
        """Load exported cookies into the session"""
        with open(cookies_path, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
        logger.info(f"Loaded cookies from {cookies_path}")

    def get_new_projects(self, ts: str = None) -> List[Dict]:
        """
        Fetch new projects from the API

        Args:
            ts: Timestamp for pagination (optional)

        Returns:
            List of project dictionaries
        """
        url = f"{self.base_url}/api/new_projects"
        params = {'ts': ts} if ts else {}

        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_latest_projects(self, count: int = 10) -> List[Dict]:
        """
        Get the latest projects sorted by discovery date (newest first)

        Args:
            count: Number of projects to return

        Returns:
            List of project dictionaries, sorted by days_since_discovery ascending
        """
        projects = self.get_new_projects()

        # Sort by days_since_discovery (ascending = newest first)
        sorted_projects = sorted(
            projects,
            key=lambda x: x.get('days_since_discovery', float('inf'))
        )

        logger.info(f"Fetched {len(projects)} projects, returning top {count} newest")
        return sorted_projects[:count]
