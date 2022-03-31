from typing import List
import requests


def fetch_edgar_data(url: str) -> requests.Response:
    headers = {
        "User-Agent": "Connor Van Ooyen Personal connor.vanooyen@gmail.com",
        "Host": "www.sec.gov",
        "Accept-Encoding": "gzip,deflate",
    }

    response = requests.get(url, headers=headers)

    return response


def get_xml_url(url: str) -> str:
    """
    Get the xml url for the filing. SEC-API returns an xml url that we  remove a chunk from and then return

    Args:
        url (str): url from sec-api

    Returns:
        str: xml url
    """
    split_url: List[str] = url.split("/")
    last_url_item = split_url.pop()
    # pop one more and throw away. This part of the url prevents it from rendering as xml
    split_url.pop()

    return "/".join(split_url) + "/" + last_url_item


get_xml_url(
    "https://www.sec.gov/Archives/edgar/data/1060736/000089924321034984/xslF345X03/doc4.xml"
)
