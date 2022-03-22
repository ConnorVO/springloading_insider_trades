from settings import SEC_QUERY_API


def get_sec_query_results(
    start_date_string: str,
    end_date_string: str,
):
    query = {
        "query": {
            "query_string": {
                "query": f'formType:4 AND formType:(NOT "N-4") AND formType:(NOT "4/A") AND filedAt:{{{start_date_string} TO {end_date_string}}}'
            }
        },
        "from": "0",
        "size": "10",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    filings = SEC_QUERY_API.get_filings(query)

    return filings
