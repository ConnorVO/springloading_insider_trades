from settings import SEC_QUERY_API, SEC_QUERY_SIZE


def get_sec_query_results(
    start_date_string: str,
    end_date_string: str,
    start: int = 0,
):
    query = {
        "query": {
            "query_string": {
                "query": f'formType:4 AND formType:(NOT "N-4") AND formType:(NOT "4/A")AND formType:(NOT "S-4") AND filedAt:[{start_date_string} TO {end_date_string}]'
            }
        },
        "from": f"{start}",
        "size": f"{SEC_QUERY_SIZE}",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    filings = SEC_QUERY_API.get_filings(query)

    return filings
