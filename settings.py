import os
from dotenv import load_dotenv
from sec_api import QueryApi

load_dotenv()

SEC_QUERY_API = QueryApi(api_key=os.getenv("QUERY_API_KEY"))
print(os.getenv("QUERY_API_KEY"))

SHOULD_SAVE_LOGS = os.getenv("SHOULD_SAVE_LOGS", "False").lower() in ("true", "1", "t")

SEC_API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
