import os
from dotenv import load_dotenv
from sec_api import QueryApi

load_dotenv()

SEC_QUERY_API = QueryApi(api_key=os.getenv("QUERY_API_KEY"))

SHOULD_SAVE_LOGS = os.getenv("SHOULD_SAVE_LOGS", "False").lower() in ("true", "1", "t")


def test(
    num1,
    num2,
    num3,
    num4,
    num5,
    num6,
    num7,
    num8,
    num9,
    num10,
    num11,
    num12,
    num13,
    num14,num15,  
):
    print("cool")
