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
        # This will store the announcement dictionary *including all extracted details*.
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
        """
        Checks for a new announcement, fetches its full details, and updates 
        the internal state if found.
        """
        latest = self.fetch_last_announcement()
        
        # Check if the announcement is genuinely new by comparing TracingNo (a unique identifier)
        is_new = latest and (not self.last_announcement or latest.get('TracingNo') != self.last_announcement.get('TracingNo'))

        if is_new:
            logger.info(f"New announcement detected: {latest.get('Title')}")
            logger.info("Fetching full details for the new announcement...")
            
            # Fetch details once and store the enriched dictionary
            detailed_announcement = parsers.extract_announcement_details(latest)
            if not detailed_announcement:
                logger.error(f"Failed to fetch details for announcement TracingNo: {latest.get('TracingNo')}. Aborting this cycle.")
                return False

            self.last_announcement = detailed_announcement
            return True
        
        logger.info("No new announcements found.")
        return False

    def validate_by_dpm(self, current_announcement: Dict) -> bool:
        """
        Validates an announcement by comparing its DPM code to the reference.
        This function no longer makes network calls; it reads from pre-fetched data.
        """
        if not current_announcement:
            logger.warning("Empty announcement cannot be validated by DPM.")
            return False
        
        if current_announcement.get("LetterCode") in NONE_DPM_CODES:
            return False # These codes are not validated by DPM

        if not self.last_announcement:
            logger.warning("No reference announcement to compare DPM code against.")
            return False
            
        # Read the DPM code directly from the enriched dictionaries
        reference_dpm = self.last_announcement.get('DpmCode')
        if not reference_dpm:
            logger.warning("Reference DPM not found. Cannot validate.")
            return False

        current_dpm = current_announcement.get('DpmCode')
        return current_dpm == reference_dpm

    def get_previous_reports(self, symbol: str, current_letter_code: str) -> List[Dict]:
        """
        Fetches and validates a history of reports for a given symbol.
        It now fetches full details for each report once.
        """
        results = []
        reference_dpm = self.last_announcement.get('DpmCode') if self.last_announcement else None

        for code in LETTER_CODES:
            params = {"Symbol": symbol, "LetterCode": code}
            announcements = self.api_client.fetch_announcements(params)
            report = announcements[0] if announcements else None
            
            if report:
                # Fetch full details for the historical report *once*
                detailed_report = parsers.extract_announcement_details(report)
                if not detailed_report:
                    logger.warning(f"Could not fetch details for historical report {report.get('Title')}. Skipping.")
                    continue

                is_valid = False
                if code in NONE_DPM_CODES:
                    is_valid = True
                elif reference_dpm and self.validate_by_dpm(detailed_report):
                    is_valid = True

                if is_valid:
                    logger.info(f"Found valid historical report: {detailed_report.get('Title')}")
                    # The detailed_report already contains all necessary data
                    results.append(detailed_report)
            
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