import os
from dotenv import load_dotenv
from sec_api import QueryApi
from supabase import create_client, Client

load_dotenv()

SEC_QUERY_API = QueryApi(api_key=os.getenv("QUERY_API_KEY"))
SEC_API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

SHOULD_SAVE_LOGS = os.getenv("SHOULD_SAVE_LOGS", "False").lower() in ("true", "1", "t")

_supabase_url: str = os.environ.get("SUPABASE_URL")
_supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
SUPABASE: Client = create_client(_supabase_url, _supabase_api_key)
SUPABASE_FILINGS_TABLE = "filings"
SUPABASE_COMPANIES_TABLE = "companies"
SUPABASE_TRANSACTIONS_TABLE = "transactions"

LOGGER_NAME = "springloading_insider_trades"
