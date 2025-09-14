from typing import Optional, Dict, List
from config import logger, LETTER_CODES, NONE_DPM_CODES
from services.codal_api import CodalAPIClient
from utils import parsers

class CodalChecker:
    """
    Orchestrates the process of checking for, validating, and processing
    new announcements from Codal.
    """
    def __init__(self):
        self.api_client = CodalAPIClient()
        self.last_announcement: Optional[Dict] = None

    def fetch_last_announcement(self) -> Optional[Dict]:
        """Fetches the most recent announcement from categories 6 and 7."""
        params_cat6 = {"Category": 6, "LetterCode": 'ن-۵۶'}
        params_cat7 = {"Category": 7}
        
        announcements_cat6 = self.api_client.fetch_announcements(params_cat6)
        announcements_cat7 = self.api_client.fetch_announcements(params_cat7)
        
        latest_cat6 = announcements_cat6[0] if announcements_cat6 else None
        latest_cat7 = announcements_cat7[0] if announcements_cat7 else None

        if latest_cat6 and latest_cat7:
            return max([latest_cat6, latest_cat7], key=lambda x: parsers.parse_datetime(x.get('PublishDateTime')))
        
        return latest_cat6 or latest_cat7

    def update_last_announcement_if_new(self) -> bool:
        """Checks for a new announcement and updates the internal state if found."""
        latest = self.fetch_last_announcement()
        if latest and latest != self.last_announcement:
            logger.info(f"New announcement detected: {latest.get('Title')}")
            self.last_announcement = latest
            return True
        
        logger.info("No new announcements found.")
        return False

    def validate_by_dpm(self, current_announcement: Dict) -> bool:
        """Validates an announcement by comparing its DPM code to the reference."""
        if not current_announcement:
            logger.warning("Empty announcement cannot be validated by DPM.")
            return False
        
        if current_announcement.get("LetterCode") in NONE_DPM_CODES:
            return False # These codes are not validated by DPM

        # We must have a reference announcement with a DPM code
        if not self.last_announcement:
            logger.warning("No reference announcement to compare DPM code against.")
            return False
            
        reference_dpm = parsers.extract_dpm_code(self.last_announcement)
        if not reference_dpm:
            logger.warning("Reference DPM not found. Cannot validate.")
            return False

        current_dpm = parsers.extract_dpm_code(current_announcement)
        return current_dpm == reference_dpm

    def get_previous_reports(self, symbol: str, current_letter_code: str) -> List[Dict]:
        """Fetches and validates a history of reports for a given symbol."""
        results = []
        reference_dpm_exists = bool(parsers.extract_dpm_code(self.last_announcement))

        for code in LETTER_CODES:
            params = {"Symbol": symbol, "LetterCode": code}
            announcements = self.api_client.fetch_announcements(params)
            report = announcements[0] if announcements else None
            
            if report:
                is_valid = False
                if code in NONE_DPM_CODES:
                    is_valid = True
                elif reference_dpm_exists and self.validate_by_dpm(report):
                    is_valid = True

                if is_valid:
                    logger.info(f"Found valid historical report: {report.get('Title')}")
                    report = parsers.extract_data_from_url(report)
                    results.append(report)
            
            if code == current_letter_code:
                break
        
        return results

    def process_announcements(self) -> Optional[Dict]:
        """Main processing routine."""
        if not self.update_last_announcement_if_new():
            return None # No new announcements

        if not self.last_announcement:
            logger.info("No announcement available to process.")
            return None
        
        symbol = self.last_announcement.get("Symbol")
        letter_code = self.last_announcement.get("LetterCode")
        
        logger.info(f"Processing reports for symbol: {symbol}")
        reports = self.get_previous_reports(symbol, letter_code)
        
        logger.info("Converting latest announcement PDF to image...")
        image_base64 = parsers.convert_pdf_to_base64_image(self.last_announcement)
        
        announcement_data = {
            "Symbol": symbol,
            "PublishDateTime": self.last_announcement.get("PublishDateTime"),
            "LatestAnnouncement": self.last_announcement,
            "HistoricalReports": reports,
            "PDFImageBase64": image_base64
        }
        
        logger.info("Processing complete.")
        return announcement_data
