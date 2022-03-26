import logging

from settings import (
    LOGGER_NAME,
    SUPABASE,
    SUPABASE_COMPANIES_TABLE,
    SUPABASE_FILINGS_TABLE,
    SUPABASE_TRANSACTIONS_TABLE,
)
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing

logger = logging.getLogger(LOGGER_NAME)

# ADD TRY CATCHES


def _does_company_exist(cik: str) -> bool:
    companies_res = (
        SUPABASE.table(SUPABASE_COMPANIES_TABLE).select("*").eq("cik", cik).execute()
    )

    return True if companies_res.data else False


def _does_filing_exist(id: str) -> bool:
    filings_res = (
        SUPABASE.table(SUPABASE_FILINGS_TABLE).select("*").eq("id", id).execute()
    )

    return True if filings_res.data else False


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
    does_filing_exist = _does_filing_exist(filing.id)
    if not does_filing_exist:
        filing_res = (
            SUPABASE.table(SUPABASE_FILINGS_TABLE)
            .insert(filing.get_db_json())
            .execute()
        )
        if not filing_res.data:
            logger.error(f"Couldn't insert filing\n{filing.__dict__}")
            return

    # create the transactions that reference the filing
    transactions_res = (
        SUPABASE.table(SUPABASE_TRANSACTIONS_TABLE)
        .insert([t.get_db_json() for t in filing.get_all_transactions()])
        .execute()
    )
    if not transactions_res.data:
        logger.error(
            f"Couldn't insert transactions\n{[t.__dict__ for t in filing.get_all_transactions()]}"
        )
        return
