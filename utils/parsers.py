import base64
import re
from io import BytesIO
from typing import Optional
from config import CODAL_URL

import requests
from bs4 import BeautifulSoup
from pdf2image import convert_from_bytes

from config import logger, BASE_URL, HEADERS, POPPLER_PATH

def convert_persian_to_english(datetime_str: str) -> str:
    """Translates Persian digits in a string to English digits."""
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    english_digits = '0123456789'
    translation_table = str.maketrans(persian_digits, english_digits)
    return datetime_str.translate(translation_table)

def parse_datetime(datetime_str: str) -> tuple:
    """Parses a Persian datetime string into a tuple of ints (Y, M, D, h, m, s)."""
    eng_str = convert_persian_to_english(datetime_str)
    date_part, time_part = eng_str.split()
    year, month, day = map(int, date_part.split('/'))
    hour, minute, second = map(int, time_part.split(':'))
    return (year, month, day, hour, minute, second)

def extract_dpm_code(announcement: dict) -> Optional[str]:
    """Extracts DPM code from the announcement detail page's HTML."""
    if not announcement or "Url" not in announcement:
        return None

    report_url = BASE_URL + announcement["Url"]
    try:
        response = requests.get(report_url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        dpm_text = ""

        for element_id in ['ucCapitalIncreaseLicense_lblLicenseCode', 'lblLicenseDesc']:
            element = soup.find(id=element_id)
            if element:
                dpm_text = element.get_text(strip=True)
                break

        if dpm_text:
            matches = re.findall(r'DPM-IOP-[A-Z0-9]+-[A-Z0-9]', dpm_text)
            return matches[0] if matches else None
    except Exception as e:
        logger.warning(f"Failed to extract DPM code from {report_url}: {e}")
    return None

def convert_pdf_to_base64_image(announcement: dict) -> Optional[str]:
    """
    Downloads a PDF from an announcement and converts its first page to a base64 encoded PNG image.
    """
    pdf_url = CODAL_URL + announcement.get("PdfUrl")
    if not pdf_url:
        logger.warning("No PdfUrl found in announcement.")
        return None

    try:
        response = requests.get(pdf_url, headers=HEADERS)
        response.raise_for_status()

        # Convert PDF bytes to an image object
        images = convert_from_bytes(response.content, first_page=1, last_page=1, poppler_path=POPPLER_PATH)
        if not images:
            logger.warning("No image could be generated from PDF.")
            return None

        # Save image to a memory buffer
        buffer = BytesIO()
        images[0].save(buffer, format="PNG")
        buffer.seek(0)
        
        # Encode buffer content to base64 string
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        return image_base64
    except Exception as e:
        logger.error(f"Failed to convert PDF to image for url {pdf_url}: {e}")
        return None
