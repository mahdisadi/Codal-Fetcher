from typing import Optional, List, Dict
import requests

from config import logger, API_URL, HEADERS, DEFAULT_PARAMS

class CodalAPIClient:
    """A client for interacting with the Codal search API."""

    def __init__(self):
        self.api_url = API_URL
        self.headers = HEADERS
        self.default_params = DEFAULT_PARAMS

    def fetch_announcements(self, extra_params: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Fetches a list of announcements from the Codal API.
        
        Args:
            extra_params: A dictionary of additional query parameters.

        Returns:
            A list of announcement dictionaries, or None on error.
        """
        params = self.default_params.copy()
        if extra_params:
            params.update(extra_params)
            
        try:
            response = requests.get(self.api_url, params=params, headers=self.headers)
            response.raise_for_status()  # Raises an exception for bad status codes
            data = response.json()
            letters = data.get("Letters", [])
            return letters if letters else None
        except requests.RequestException as e:
            logger.error(f"API request error: {e}")
        except ValueError as e:
            logger.error(f"API JSON decoding error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during API fetch: {e}")
        return None
