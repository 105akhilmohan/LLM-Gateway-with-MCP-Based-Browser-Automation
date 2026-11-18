
from urllib.parse import urlparse

from browser.browser_manager import browser_manager


def validate_url(url):

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.netloc:
        raise ValueError("Invalid URL.")

    return url


def open_chrome(url=None):

    if not url:
        url = "https://www.google.com"

    url = validate_url(url)

    return browser_manager.open_chrome(url)


def close_chrome():

    return browser_manager.close_chrome()


def open_website(url):

    url = validate_url(url)

    return browser_manager.open_chrome(url)
