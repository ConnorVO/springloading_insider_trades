import logging
from typing import List

from settings import (
    LOGGER_NAME,
    SUPABASE,
    SUPABASE_COMPANIES_TABLE,
    SUPABASE_ERROR_URLS_TABLE,
    SUPABASE_EXECS_TABLE,
    SUPABASE_FILINGS_TABLE,
    SUPABASE_PRICES_TABLE,
    SUPABASE_TRANSACTIONS_TABLE,
)
from springloading_insider_trades.sec_api.classes.Company import Company
from springloading_insider_trades.sec_api.classes.Form4Filing import Form4Filing

logger = logging.getLogger(LOGGER_NAME)


def _update_exec_data(data: object):
    if not data["stock_prices"]["90_day"] or not data["stock_prices"]["open"]:
        # there is nothing to update unless is 90_day data
        return None

    exec_get_res = (
        SUPABASE.table(SUPABASE_EXECS_TABLE)
        .select("*")
        .filter("cik", "eq", data["owner_cik"])
        .execute()
    )
    # Current Data
    exec_num_trades = (
        exec_get_res.data[0]["num_trades"] if exec_get_res.data[0]["num_trades"] else 0
    )
    ninety_day_return = exec_get_res.data[0]["ninety_day_return"]
    num_correct = (
        exec_get_res.data[0]["num_correct"]
        if exec_get_res.data[0]["num_correct"]
        else 0
    )
    # Update the data
    if ninety_day_return or ninety_day_return == 0:
        if exec_num_trades == 0:
            ninety_day_return = (
                data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1
            )
        else:
            ninety_day_return = (
                ninety_day_return * exec_num_trades
                + (data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1)
            ) / (exec_num_trades + 1)

    if not ninety_day_return:
        ninety_day_return = (
            data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1
        )

    if data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1 > 0:
        num_correct += 1
    # if exec_num_trades > 0:
    #     ninety_day_return = (
    #         ninety_day_return * exec_num_trades
    #         + (data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1)
    #     ) / (exec_num_trades + 1)

    #     if data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1 > 0:
    #         num_correct += 1
    # else:
    #     ninety_day_return =  (data["stock_prices"]["90_day"] / data["stock_prices"]["open"] - 1)

    update_data = {
        "num_trades": exec_num_trades + 1,
        "ninety_day_return": ninety_day_return,
        "num_correct": num_correct,
    }
    exec_update_res = (
        SUPABASE.table(SUPABASE_EXECS_TABLE)
        .update(update_data)
        .filter("cik", "eq", data["owner_cik"])
        .execute()
    )  # .eq doesn't work)

    return exec_update_res


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
    # does_company_exist = _does_company_exist(filing.company.cik)
    # if not does_company_exist:
    company_res = (
        SUPABASE.table(SUPABASE_COMPANIES_TABLE)
        .upsert(filing.company.get_db_json())
        .execute()
    )
    logger.info(f"Upserting Company: {company_res.data[0]['cik']}")
    if not company_res.data:
        logger.error(f"Couldn't upsert company\n{filing.company.__dict__}")
        return False

    # Create Exec
    exec_res = (
        SUPABASE.table(SUPABASE_EXECS_TABLE).upsert(filing.exec.get_db_json()).execute()
    )
    logger.info(f"Upserting Exec: {exec_res.data[0]['cik']}")
    if not exec_res.data:
        logger.error(f"Couldn't upsert Exec\n{filing.exec,__dict__}")
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
            logger.exception(f"Couldn't insert error url\n{url}")
            return False

    return True


def insert_price_data(price_data: List[object]):
    for data in price_data:
        try:
            prices_res = (
                SUPABASE.table(SUPABASE_PRICES_TABLE)
                .insert(
                    {
                        "open": data["stock_prices"]["open"],
                        "90_day": data["stock_prices"]["90_day"],
                    }
                )
                .execute()
            )

            filings_res = (
                SUPABASE.table(SUPABASE_FILINGS_TABLE)
                .update(
                    {
                        "prices_id": prices_res.data[0]["id"],
                    }
                )
                .filter("id", "eq", data["filing_id"])  # .eq doesn't work
                .execute()
            )

            _update_exec_data(data)

            logger.info(f'Updated prices for filing ID {data["filing_id"]}')
        except Exception as e:
            logger.exception(e)


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


def delete_exec(owner_cik: int):
    exec_res = (
        SUPABASE.table(SUPABASE_EXECS_TABLE)
        .delete()
        .match({"cik": owner_cik})
        .execute()
    )

    logger.info(f"Deleting Exec (cik: {owner_cik}): {exec_res}")
    if not exec_res.data:
        logger.error(f"Couldn't delete Exec (cik: {owner_cik} from db")
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


def get_filings_for_prices(now_date: str):
    """Gets filings from before given date with proper data

    Args:
        now_date (str): the date it gets prices before

    Returns:
        _type_: list of filings
    """
    try:
        filing_res = (
            # SUPABASE.table(SUPABASE_FILINGS_TABLE)
            # .select("*, companies (ticker)")
            # .filter("prices", "is", "null")
            # .filter("filing_date", "lt", now_date)
            # .execute()
            SUPABASE.rpc(
                "get_purchase_filings_for_adding_prices",
                {"date_input": now_date},
            )
        )
        return filing_res.json()
    except Exception as e:
        logger.exception(e)

    # returning empty list because we do same behavior if we don't have any data or there is an error
    return []


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
