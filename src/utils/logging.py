import datetime
import logging
from pathlib import Path

def configure_logger():
    # Create 'logs' directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Get the current date and time for the filename
    current_time = datetime.datetime.now()

    # Construct the log file path using Path
    filename = log_dir / current_time.strftime("log_%Y%m%d_%H%M%S.txt")

    # Configure logging
    logging.basicConfig(filename=str(filename), level=logging.INFO, 
                        format='%(asctime)s %(levelname)s:%(message)s', 
                        filemode='w', force=True)

    # Suppress supabase logging
    logging.getLogger('httpx').setLevel(logging.WARNING)
