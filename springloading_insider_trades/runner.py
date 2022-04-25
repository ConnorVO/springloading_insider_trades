from datetime import datetime, timedelta
import pendulum as pdl
import json
import os
import logging
from typing import List
import pprint


from settings import (
    LOGGER_NAME,
    SEC_API_DATETIME_FORMAT,
    SHOULD_SAVE_LOGS,
    SUPABASE,
    SUPABASE_FILINGS_TABLE,
)
from springloading_insider_trades.db.db import (
    get_filings_for_prices,
    insert_error_url,
    insert_filing_data,
    insert_price_data,
)
from springloading_insider_trades.email.email import send_error_urls_email
from springloading_insider_trades.intrinio_api.get_prices_between_dates import (
    get_prices_between_dates,
)
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing
from springloading_insider_trades.sec_api.sec_api import (
    _get_form_4_filing_from_url,
    get_filings,
)

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

    prev_date = datetime.strptime(prev_start_date_string, "%Y-%m-%d")
    curr_date = prev_date + timedelta(days=1)
    curr_date_str = datetime.strftime(curr_date, "%Y-%m-%d")

    logger.info(f"Getting daily data for {curr_date_str}")

    filings: List[Form4Filing] = []
    error_urls: List[str] = []
    # THIS MUST RETURN LESS THAN 10,000 RESULTS OR SEC_API BREAKS. SO BREAK UP THE DATES IF YOU NEED MORE
    filings, error_urls = get_filings(curr_date_str, curr_date_str)

    logger.info("Adding filings to DB")
    for filing in filings:
        insert_filing_data(filing)

    logger.info("Adding Errors to DB")
    if error_urls:
        for url in error_urls:
            insert_error_url(url)

    logger.info(f"Sending Error Email for {len(error_urls)} errors")
    send_error_urls_email()

    logger.info("Writing date to local db")
    with open("./data/local_db.json", "w", encoding="utf-8") as f:
        obj = {
            "prev_start_date_string": curr_date_str,
        }
        json.dump(obj, f, ensure_ascii=False, indent=4)

    logger.info(f"Found {len(filings)} final filings")
    logger.info(f"Found {len(error_urls)} errors")
    logger.info("Daily Finished")


def run_between_dates():
    """
    Run with => pipenv run python3 -c 'import springloading_insider_trades.runner; springloading_insider_trades.runner.run_between_dates()'
    """
    program_start_date_string = "2020-10-01"
    program_end_date_string = "2020-10-01"

    _setup_logging("multi-day")
    logger.info("Starting Between Dates")

    # Break into chunks because SEC-API only returns up to 10k filings and there can be weird issues when we do more
    day_delta: int = 3
    start_date = datetime.strptime(program_start_date_string, "%Y-%m-%d")
    stop_program_date = datetime.strptime(program_end_date_string, "%Y-%m-%d")
    end_date = start_date + timedelta(
        days=day_delta
    )  # making it too many days causes a lot of SEC-API json issues

    filings: List[Form4Filing] = []
    error_urls: List[str] = []

    while start_date <= stop_program_date:
        logger.info(f"Getting filings for {start_date} - {end_date}")
        # don't want to get data past the stop_program date
        if end_date > stop_program_date:
            end_date = stop_program_date

        # THIS MUST RETURN LESS THAN 10,000 RESULTS OR SEC_API BREAKS. SO BREAK UP THE DATES IF YOU NEED MORE
        filings_data = get_filings(
            start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        )
        filings.extend(filings_data[0])
        error_urls.extend(filings_data[1])

        # update the start and end dates to get the next chunk
        start_date = end_date + timedelta(days=1)
        end_date = start_date + timedelta(days=day_delta)

    logger.info("Adding filings to DB")
    for filing in filings:
        try:
            insert_filing_data(filing)
        except Exception as e:
            logger.error(
                f"Error inserting filings into db\nFiling: {filing.__dict__}\nError: {e}"
            )

    logger.info("Adding Errors to DB")
    if error_urls:
        for url in error_urls:
            logger.info(f"ERROR URL -> {url}")
            try:
                insert_error_url(url)
            except Exception as e:
                logger.error(
                    f"Error inserting error url into db\Error Url: {url}\nError: {e}"
                )

    logger.info(f"Found {len(filings)} final filings")
    logger.info(f"Found {len(error_urls)} errors")
    logger.info("Between Dates Finished")


def run_intrinio_prices():
    """
    Run with => pipenv run python3 -c 'import springloading_insider_trades.runner; springloading_insider_trades.runner.run_intrinio_prices()'
    """
    _setup_logging("run_intrinio_prices")
    logger.info("Starting Intrinio Prices")

    # Get Date strings
    ## - 1 day ago string
    ## - 90 day ago string
    now = pdl.now("America/Indianapolis")
    now_string = now.to_date_string()
    # Get filings from supabase older than 1 day and 90 days
    ## Get tickers
    filings = get_filings_for_prices(now_string)

    # Get and update prices for those filings from intrinio
    # stock_prices = get_prices_between_dates("AAPL", start_date="2021-01-01", end_date="2022-01-01")

    ### Get the closest price AFTER given date
    stock_price_data = []
    for filing in filings:
        date = pdl.parse(filing["filing_date"], tz="America/Indianapolis")
        next_day_date = date.add(days=1)
        ninety_day_date = date.add(days=90)
        # could be a weekend or market is closed, so need to get the next closest price
        next_day_buffer = next_day_date.add(days=5)
        ninety_day_buffer_string = ninety_day_date.add(days=5)
        next_day_price_data = get_prices_between_dates(
            filing["ticker"],
            next_day_date.to_date_string(),
            next_day_buffer.to_date_string(),
        )
        ninety_day_price_data = get_prices_between_dates(
            filing["ticker"],
            ninety_day_date.to_date_string(),
            ninety_day_buffer_string.to_date_string(),
        )

        if not next_day_price_data and not ninety_day_price_data:
            continue

        stock_price_data.append(
            {
                "filing_id": filing["filing_id"],
                "stock_prices": {
                    "open": next_day_price_data[-1].open
                    if next_day_price_data
                    else None,
                    "90_day": ninety_day_price_data[-1].close
                    if ninety_day_price_data
                    else None,
                },
            }
        )

    insert_price_data(stock_price_data)


def seed_db():
    """Seed DB with older than 90 days, exactly 90 days, earlier than 90 days, exactly 1 day, and earlier than 1 day

    Run with => pipenv run python3 -c 'import springloading_insider_trades.runner; springloading_insider_trades.runner.seed_db()'
    """
    now = pdl.now("America/Indianapolis")
    now_string = now.to_date_string()
    one_day_ago_string = now.subtract(days=1).to_date_string()
    thirty_day_ago_string = now.subtract(days=30).to_date_string()
    ninety_days_ago_string = now.subtract(days=90).to_date_string()
    hundred_days_ago_string = now.subtract(days=100).to_date_string()

    now_filings, now_error_urls = get_filings(now_string, now_string, size=3)
    one_day_ago_filings, one_day_ago_error_urls = get_filings(
        one_day_ago_string, one_day_ago_string, size=3
    )
    thirty_day_ago_filings, thirty_day_ago_error_urls = get_filings(
        thirty_day_ago_string, thirty_day_ago_string, size=3
    )
    ninety_days_ago_filings, ninety_days_ago_error_urls = get_filings(
        ninety_days_ago_string, ninety_days_ago_string, size=3
    )
    hundred_days_ago_filings, hundred_days_ago_error_urls = get_filings(
        hundred_days_ago_string, hundred_days_ago_string, size=3
    )

    all_filings = (
        now_filings
        + one_day_ago_filings
        + thirty_day_ago_filings
        + ninety_days_ago_filings
        + hundred_days_ago_filings
    )
    all_errors = (
        now_error_urls
        + one_day_ago_error_urls
        + thirty_day_ago_error_urls
        + ninety_days_ago_error_urls
        + hundred_days_ago_error_urls
    )

    logger.info("Adding filings to DB")
    for filing in all_filings:
        try:
            insert_filing_data(filing)
        except Exception as e:
            logger.error(
                f"Error inserting filings into db\nFiling: {filing.__dict__}\nError: {e}"
            )

    logger.info(f"Found {len(all_filings)} final filings")
    logger.info(f"Found {len(all_errors)} errors")

    pprint.PrettyPrinter().pprint(f"Errors: {all_errors}")


def test():
    """
    Run with => pipenv run python3 -c 'import springloading_insider_trades.runner; springloading_insider_trades.runner.test()'
    """
    _setup_logging("test")
    logger.info("Starting Test")

    ## TEST UPDATE
    # res = (
    #     SUPABASE.table(SUPABASE_FILINGS_TABLE)
    #     .update({"prices_id": 25})
    #     .filter("id", "eq", "00013977022022-01-13T18:55:11-05:000001769940") # .eq doesn't work
    #     .execute()
    # )

    ## TEST INSERTING FORM 4
    # form4_filing = _get_form_4_filing_from_url(
    #     (
    #         datetime.strptime("2022-02-23", "%Y-%m-%d"),
    #         "https://www.sec.gov/Archives/edgar/data/1397702/000159396822000213/xslF345X03/primary_01.xml",
    #         # "https://www.sec.gov/Archives/edgar/data/1114995/000124636019002198/xslF345X03/form.xml",
    #     )
    # )

    # try:
    #     insert_filing_data(form4_filing)
    # except Exception as e:
    #     logger.error(
    #         f"Error inserting filings into db\nFiling: {form4_filing.__dict__}\nError: {e}"
    #     )

    # pprint.PrettyPrinter().pprint(form4_filing.__dict__)

    logger.info("Test Finished")
