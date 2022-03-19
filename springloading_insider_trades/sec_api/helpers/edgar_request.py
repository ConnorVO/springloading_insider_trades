import requests


def fetch_edgar_data(url: str) -> requests.Response:
    headers = {
        "User-Agent": "Connor Van Ooyen Personal connor.vanooyen@gmail.com",
        "Host": "www.sec.gov",
        "Accept-Encoding": "gzip,deflate",
    }

    response = requests.get(url, headers=headers)

    return response
