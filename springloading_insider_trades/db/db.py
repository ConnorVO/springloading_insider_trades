import logging

from settings import (
    LOGGER_NAME,
    SUPABASE,
    SUPABASE_COMPANIES_TABLE,
    SUPABASE_ERROR_URLS_TABLE,
    SUPABASE_FILINGS_TABLE,
    SUPABASE_TRANSACTIONS_TABLE,
)
from springloading_insider_trades.sec_api.classes.Company import Company
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing

logger = logging.getLogger(LOGGER_NAME)


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


def _does_transaction_exist(id: str) -> bool:
    transactions_res = (
        SUPABASE.table(SUPABASE_TRANSACTIONS_TABLE).select("*").eq("id", id).execute()
    )

    return True if transactions_res.data else False


def insert_filing_data(filing: Form4Filing) -> bool:
    # Create company if it doesn't exist
    does_company_exist = _does_company_exist(filing.company.cik)
    if not does_company_exist:
        company_res = (
            SUPABASE.table(SUPABASE_COMPANIES_TABLE)
            .insert(filing.company.get_db_json())
            .execute()
        )
        logger.info(f"Inserting Company: {company_res.data[0]['cik']}")
        if not company_res.data:
            logger.error(f"Couldn't insert company\n{filing.company.__dict__}")
            return False

    # Create filing that references company
    does_filing_exist = _does_filing_exist(filing.id)
    if not does_filing_exist:
        filing_res = (
            SUPABASE.table(SUPABASE_FILINGS_TABLE)
            .insert(filing.get_db_json())
            .execute()
        )
        logger.info(f"Inserting Filing: {filing_res.data[0]['id']}")
        if not filing_res.data:
            logger.error(f"Couldn't insert filing\n{filing.__dict__}")
            return False

    # create the transactions that reference the filing
    # does_transaction_exist = _does_transaction_exist()
    # only insert if filing has been created
    if not does_filing_exist:
        transactions_res = (
            SUPABASE.table(SUPABASE_TRANSACTIONS_TABLE)
            .insert([t.get_db_json() for t in filing.get_all_transactions()])
            .execute()
        )
        logger.info(
            f"Inserting Transactions: {[t['id'] for t in transactions_res.data]}"
        )
        if not transactions_res.data:
            logger.error(
                f"Couldn't insert transactions\n{[t.__dict__ for t in filing.get_all_transactions()]}"
            )
            return False

    return True


def _does_error_url_exist(url: str) -> bool:
    error_res = (
        SUPABASE.table(SUPABASE_ERROR_URLS_TABLE)
        .select("*")
        # .eq() doesn't work with urls so have to use filter
        .filter("url", "eq", url)
        .execute()
    )
    logger.info(error_res)
    return True if error_res.data else False


def insert_error_url(url: str):
    does_error_url_exist = _does_error_url_exist(url)
    if not does_error_url_exist:
        error_res = (
            SUPABASE.table(SUPABASE_ERROR_URLS_TABLE).insert({"url": url}).execute()
        )
        logger.info(f"Inserting Error Url: {error_res}")
        if not error_res.data:
            logger.error(f"Couldn't insert error url\n{url}")
            return False

    return True


def delete_filing(filing: Form4Filing) -> bool:
    filing_res = (
        SUPABASE.table(SUPABASE_FILINGS_TABLE)
        .delete()
        .match({"id": filing.id})
        .execute()
    )
    logger.info(f"Deleting Filing (id: {filing.id}): {filing_res}")
    if not filing_res.data:
        logger.error(f"Couldn't delete filing (id: {filing.id} from db")
        return False

    return True


def delete_error_url(url: str) -> bool:
    error_url_res = (
        SUPABASE.table(SUPABASE_ERROR_URLS_TABLE)
        .delete()
        # .eq() doesn't work with urls so have to use filter
        .filter("url", "eq", url)
        .execute()
    )

    logger.info(f"Deleting Error URL (url: {url}): {error_url_res}")
    if not error_url_res.data:
        logger.error(f"Couldn't delete error url (url: {url} from db")
        return False

    return True


## NOTE: Shouldn't ever really need to delete company because it is referenced by multiple filings
# def delete_company(company: Company) -> bool:
#     company_res = (
#         SUPABASE.table(SUPABASE_COMPANIES_TABLE)
#         .delete()
#         .match({"cik": company.cik})
#         .execute()
#     )
#     logger.info(f"Deleting Company (cik: {company.cik}): {company_res}")
#     if not company_res.data:
#         logger.error(f"Couldn't delete company (cik: {company.cik} from db")
#         return False

#     return True
