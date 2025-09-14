import logging

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- API and URL Configuration ---
BASE_URL = "https://codal.ir/"
API_URL = "https://search.codal.ir/api/search/v2/q"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://codal.ir",
    "Referer": "https://codal.ir/"
}

DEFAULT_PARAMS = {
    "PageNumber": 1,
    "search": "true"
}

# --- Business Logic Constants ---
LETTER_CODES = ['ن-۶۰', 'ن-۶۱', 'ن-۶۳', 'ن-۶۲', 'ن-۷۱', 'ن-۷۲', 'ن-۵۶', 'ن-۷۳', 'ن-۶۴', 'ن-۶۵', 'ن-۶۶', 'ن-۶۷']
NONE_DPM_CODES = ['ن-۶۰', 'ن-۶۱']

# --- External Tool Paths ---
# IMPORTANT: Update this path to your Poppler installation
POPPLER_PATH = "" 
