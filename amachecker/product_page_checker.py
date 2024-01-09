import re
from bs4 import BeautifulSoup
import logging
from requests_toolbelt.threaded import pool

logging.basicConfig(level=logging.DEBUG)
BASE_URL = "https://www.amazon.de/gp/product/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
}


def check_price_per_unit(
        asins: list[str], pattern: re.Pattern | None = None
):
    if pattern is None:
        pattern = re.compile(r"\d+,\d{2}€ / meter")

    urls = []
    out = {}

    for asin in asins:
        urls.append(f"https://www.amazon.de/gp/product/{asin}?th=1")

    p = pool.Pool.from_urls(urls, request_kwargs={"headers": HEADERS})
    p.join_all()

    for response in p.responses():
        url = response.request_kwargs['url']
        if 200 > response.status_code > 299:
            logging.warning("Could not retrieve page text.")
            out[url] = False
            continue

        soup = BeautifulSoup(response.content, features="html.parser")
        elem = soup.select_one("span.pricePerUnit")
        if elem is None:
            logging.warning("Could not find span.pricePerUnit in page text.")
            out[url] = False
            continue

        logging.debug("Searching for pattern.")
        out[url] = bool(pattern.search(elem.text))

    return out


if __name__ == "__main__":
    asins = [
        "B079D88PBH",
        "B079D8TYPV",
        "B079D94JTY",
        "B079D972T7",
        "B075P1QLXS",
        "B08HRV23LX",
    ]
    res = check_price_per_unit(asins)
    print(res)
