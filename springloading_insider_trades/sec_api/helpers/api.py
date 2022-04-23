from settings import SEC_QUERY_API, SEC_QUERY_SIZE


def get_sec_query_results(
    start_date_string: str,
    end_date_string: str,
    start: int = 0,
    size: int = SEC_QUERY_SIZE,
):
    query = {
        "query": {
            "query_string": {
                "query": f'formType:4 AND formType:(NOT "T-4") AND formType:(NOT "N-4") AND formType:(NOT "4/A")AND formType:(NOT "S-4") AND formType:(NOT "F-4") AND filedAt:[{start_date_string} TO {end_date_string}]'
            }
        },
        "from": f"{start}",
        "size": f"{size}",
        "sort": [{"filedAt": {"order": "desc"}}],
    }

    filings = SEC_QUERY_API.get_filings(query)

    return filings


"""
SEC_API QUERY SANDBOX
{
    "query": {
        "query_string": {
            "query": "formType:4 AND formType:(NOT \"T-4\") AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND formType:(NOT \"S-4\") AND formType:(NOT \"F-4\") AND filedAt:[2019-10-01 TO 2019-10-04]"
        }
    },
    "from": "0",
    "size": "200",
    "sort": [{ "filedAt": { "order": "desc" } }]
}
"""
