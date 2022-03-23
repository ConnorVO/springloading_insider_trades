import logging

from settings import (
    LOGGER_NAME,
    SUPABASE,
    SUPABASE_COMPANIES_TABLE,
    SUPABASE_FILINGS_TABLE,
)
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing

logger = logging.getLogger(LOGGER_NAME)

# ADD TRY CATCHES


def _does_company_exist(cik: str) -> bool:
    data = SUPABASE.table(SUPABASE_COMPANIES_TABLE).select("*").eq("cik", cik).execute()

    return True if data else False


def insert_filing_data(filing: Form4Filing):
    # Create company if it doesn't exist
    does_company_exist = _does_company_exist(filing.company.cik)
    if not does_company_exist:
        company_res = (
            SUPABASE.table(SUPABASE_COMPANIES_TABLE)
            .insert(filing.company.get_db_json())
            .execute()
        )
        if not company_res.data:
            logger.error(f"Couldn't insert company\n{filing.company.__dict__}")
            return

    # Create filing that references company
    filing_res = (
        SUPABASE.table(SUPABASE_FILINGS_TABLE).insert(filing.get_db_json()).execute()
    )
    if not filing_res.data:
        logger.error(f"Couldn't insert filing\n{filing.__dict__}")
        return

    # create the transactions that reference the filing
