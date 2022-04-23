import os
from dotenv import load_dotenv
import intrinio_sdk as intrinio
from sec_api import QueryApi
from supabase import create_client, Client

load_dotenv()

SEC_QUERY_API = QueryApi(api_key=os.getenv("QUERY_API_KEY"))
SEC_API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
SEC_QUERY_SIZE = 200

SHOULD_SAVE_LOGS = os.getenv("SHOULD_SAVE_LOGS", "False").lower() in ("true", "1", "t")

_supabase_url: str = os.environ.get("SUPABASE_URL")
_supabase_api_key: str = os.environ.get("SUPABASE_API_KEY")
SUPABASE: Client = create_client(_supabase_url, _supabase_api_key)
SUPABASE_FILINGS_TABLE = "filings"
SUPABASE_COMPANIES_TABLE = "companies"
SUPABASE_TRANSACTIONS_TABLE = "transactions"
SUPABASE_ERROR_URLS_TABLE = "error_urls"

LOGGER_NAME = "springloading_insider_trades"

EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

intrinio.ApiClient().set_api_key(os.getenv("INTRINIO_API_KEY"))
intrinio.ApiClient().allow_retries(True)
