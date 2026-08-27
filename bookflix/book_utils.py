import os
import time
from isbnlib import canonical, meta, cover, config
from isbnlib.dev import ISBNLibHTTPError

config.add_apikey("goob", os.environ["GOOGLE_BOOKS_API_KEY"])


def canonical_isbn(isbn):
    """
    Returns the canonical form of the ISBN number.
    """
    return canonical(isbn)


def get_book_info_by_isbn(isbn):
    """
    Fetches book information from an online source using the ISBN number.
    """
    isbn = canonical(isbn)
    m = {}
    for _ in range(3):
        try:
            m = meta(isbn)
            break
        except ISBNLibHTTPError:
            time.sleep(1)
    c = {}
    for _ in range(3):
        try:
            c = cover(isbn)
            break
        except ISBNLibHTTPError:
            time.sleep(1)
    return {**m, **c}
