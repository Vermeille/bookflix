from isbnlib import canonical, meta, cover


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
    return {**meta(isbn), **cover(isbn)}
