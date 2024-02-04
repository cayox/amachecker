import logging
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)
BASE_URL = "https://www.amazon.de/gp/product/"

# List of user agents for rotating
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
]

session = requests.Session()

HTTP_OK_STATUS_RANGE = 200, 299


def fetch_url(asin: str) -> tuple[requests.Response, str] | tuple[str, str]:
    """Fetches content from a given ASIN on Amazon using a GET request.

    Args:
        asin (str): The Amazon Standard Identification Number (ASIN).

    Returns:
        tuple: A tuple containing the response object and the ASIN, or an error message and the ASIN.
    """
    try:
        url = build_url_from_asin(asin)
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
        }
        response = session.get(url, headers=headers, timeout=30)
        time.sleep(random.uniform(3, 10))  # Random delay between requests
    except requests.RequestException as e:
        return str(e), asin
    else:
        return response, asin


def build_url_from_asin(asin: str) -> str:
    """Build german amazon link for `asin`."""
    return f"https://www.amazon.de/gp/product/{asin}?th=1"


def http_status_ok(status: int) -> bool:
    """Check if http status is in acceptable range."""
    return HTTP_OK_STATUS_RANGE[0] >= status >= HTTP_OK_STATUS_RANGE[1]


def check_for_pattern(
    response: requests.Response, asin: str, log_func: callable, pattern: re.Pattern,
) -> dict[str, bool | str]:
    """Check if the page from `response` has the expected pattern.

    Args:
        response: the response with the webpage
        asin: the asin for the response
        log_func: a function for logging callbacks
        pattern: the compiled pattern to check

    Returns:
        a dict with asin, url, result and reason
    """
    url = build_url_from_asin(asin)
    if isinstance(response, str) or http_status_ok(response.status_code):
        log_func(f"Amazon Seite für {asin} konnte nicht geladen werden")
        return {
            "asin": asin,
            "result": False,
            "url": url,
            "reason": (
                response
                if isinstance(response, str)
                else f"Amazon Seite für {asin} konnte nicht geladen werden"
            ),
        }

    if "dass sie kein bot sind" in response.content.decode().lower():
        log_func(
            f"ASIN {asin}: Programm wurde als Bot erkannt. Seite kann nicht überprüft werden.",
        )
        return {
            "asin": asin,
            "result": False,
            "url": url,
            "reason": "Programm wurde als Bot erkannt",
        }

    soup = BeautifulSoup(response.content, features="html.parser")
    elem = soup.find(id="apex_desktop")
    if elem is None:
        log_func("WARNUNG: Preiselement nicht gefunden!")
        return {
            "asin": asin,
            "result": False,
            "url": url,
            "reason": "No price element found",
        }

    check = bool(pattern.search(elem.text))
    log_func(
        f"Überprüfe ASIN {asin}: {'Text Gefunden' if check else 'Text NICHT gefunden'}",
    )
    return {
        "asin": asin,
        "result": check,
        "url": url,
        "reason": "",
    }


def check_pages(
    asins: list[str],
    pattern: re.Pattern,
    log_func: callable = print,
) -> list[dict]:
    """Load amazon ASIN pages concurrently and then analyze them for the pattern concurrently.

    Args:
        asins: the list of ASINs to load
        pattern: the compiled regex pattern to check
        log_func: a function for logging callbacks

    Returns:
        a list of with each asin, with url, result, and reason
    """
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(
            executor.map(lambda url: log_func(f"Lade {url}") or fetch_url(url), asins),
        )

    with ThreadPoolExecutor(max_workers=100) as executor:
        return list(
            executor.map(
                lambda result: check_for_pattern(
                    result[0],
                    result[1],
                    log_func,
                    pattern,
                ),
                results,
            ),
        )
