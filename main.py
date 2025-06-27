from codal_checker import CodalChecker
from config import logger
import json

def run_checker():
    """Initializes and runs the Codal checker process."""
    logger.info("Starting Codal Checker...")
    checker = CodalChecker()
    
    processed_data = checker.process_announcements()
    
    if processed_data:
        logger.info("Successfully processed new announcement.")

        printable_data = processed_data.copy()
        has_image = "Yes" if printable_data.pop("PDFImageBase64", None) else "No"
        printable_data["HasPDFImage"] = has_image

        print("\n--- PROCESSED DATA ---")
        print(json.dumps(printable_data, indent=2, ensure_ascii=False))
        print("----------------------\n")
    else:
        logger.info("No new announcements were processed.")
        
    logger.info("Codal Checker finished.")


if __name__ == "__main__":
    run_checker()
