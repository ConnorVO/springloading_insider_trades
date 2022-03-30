from datetime import datetime
import json
import os
import logging
from typing import List

from settings import LOGGER_NAME, SHOULD_SAVE_LOGS
from springloading_insider_trades.db.db import insert_filing_data
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing
from springloading_insider_trades.sec_api.sec_api import get_filings

logger = logging.getLogger(LOGGER_NAME)


def _setup_logging(func_name: str, should_save_logs: bool = SHOULD_SAVE_LOGS):
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    if func_name != "test" and should_save_logs:
        # set up the logfile handler
        log_time = datetime.now()
        log_path = f"logs/{func_name}"
        log_filename = os.path.join(
            log_path, f"{func_name}-%s.log" % log_time.strftime("%Y%m%d-%H%M%S")
        )
        fh = logging.FileHandler(log_filename)
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # set up the console/stream handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    logger.propagate = False


def run_daily():
    """
    Run with => pipenv run python3 -c 'import springloading_insider_trades.runner; springloading_insider_trades.runner.run_daily()'
    """
    _setup_logging("daily")
    logger.info("Starting Daily")

    # load the date from local_db which we use in case python-anywhere restarts
    with open("./data/local_db.json", "r") as f:
        data = json.load(f)
        prev_start_date_string: str = data["prev_start_date_string"]

    logger.info(f"Getting daily data for {prev_start_date_string}")

    filings: List[Form4Filing] = []
    error_urls: List[str] = []
    filings, error_urls = get_filings(prev_start_date_string, prev_start_date_string)

    for filing in filings:
        import pprint

        pprint.PrettyPrinter().pprint(filing.__dict__)

    # for filing in filings:
    #     insert_filing_data(filing)

    if error_urls:
        # send email with errors (or save in DB)
        print("error urls")

    logger.info("Daily Finished")


def test():
    """
    Run with => pipenv run python3 -c 'import springloading_insider_trades.runner; springloading_insider_trades.runner.test()'
    """
    _setup_logging("test")
    logger.info("Starting Test")
    print("Testing")
    logger.info("Test Finished")
