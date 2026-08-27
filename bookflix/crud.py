import time
from sqlalchemy import func
from sqlalchemy.orm import Session
from bookflix import models
from bookflix.auth import get_password_hash
from bookflix.book_utils import get_book_info_by_isbn, canonical_isbn

###########
# book
###########


def all_categories(db: Session):
    return db.query(models.Category).order_by(models.Category.name).all()


def add_category(db: Session, name: str):
    name = name.strip()
    if not name:
        raise ValueError("Le nom de la catégorie est requis.")
    if (
        db.query(models.Category)
        .filter(func.lower(models.Category.name) == name.lower())
        .first()
    ):
        raise ValueError("Cette catégorie existe déjà.")

    category = models.Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int) -> bool:
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        return False

    for book in list(category.books):
        book.category = None
    db.delete(category)
    db.commit()
    return True


def set_book_category(db: Session, isbn: str, category_id: str | None) -> bool:
    isbn = canonical_isbn(isbn)
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        return False

    if category_id in [None, ""]:
        book.category = None
    else:
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            raise ValueError("Catégorie invalide.")
        category = (
            db.query(models.Category)
            .filter(models.Category.id == category_id)
            .first()
        )
        if not category:
            raise LookupError("Catégorie introuvable.")
        book.category = category
    db.commit()
    return True


def add_book(db: Session, isbn: str, title: str, author: str, cover_url: str):
    isbn = canonical_isbn(isbn)

    book = models.Book(isbn=isbn, title=title, author=author, cover_url=cover_url)
    db.add(book)
    db.commit()
    return book


def get_book_by_isbn(db: Session, isbn: str):
    isbn = canonical_isbn(isbn)

    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        print("book not cached", isbn)
        book_info = get_book_info_by_isbn(isbn)
        if not book_info:
            return None
        book = add_book(
            db,
            isbn=isbn,
            title=book_info["Title"],
            author=", ".join(book_info["Authors"]),
            cover_url=book_info.get("thumbnail"),
        )
    return book


def borrow_book(db: Session, student: models.Student, book: models.Book):
    book.borrowed_by = student
    book.borrowed_time = int(time.time())
    db.commit()


def all_books(db: Session):
    return db.query(models.Book).all()


def my_books(db: Session, student: models.Student):
    return db.query(models.Book).filter(models.Book.borrowed_by == student).all()


def return_book(db: Session, book: models.Book):
    book.borrowed_by = None
    db.commit()


def delete_book_by_isbn(db: Session, isbn: str) -> bool:
    """Delete a book by its ISBN. Returns True if deleted, False if not found."""
    isbn = canonical_isbn(isbn)
    book = db.query(models.Book).filter(models.Book.isbn == isbn).first()
    if not book:
        return False
    db.delete(book)
    db.commit()
    return True


################
# USER CRUD
################


def get_student_by_username(db: Session, username: str):
    return db.query(models.Student).filter(models.Student.username == username).first()


def add_user(db: Session, username: str, password: str):
    user = get_student_by_username(db, username)
    if user:
        return user

    user = models.Student(username=username, password=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def all_users(db: Session):
    return db.query(models.Student).all()


def delete_user_by_username(db: Session, username: str) -> bool:
    """Delete a user by username.
    - Returns True if deleted, False if not found or protected.
    - Clears any borrowed books to maintain referential integrity.
    - Never deletes the special 'admin' user.
    """
    user = get_student_by_username(db, username)
    if not user:
        return False
    if user.username == "admin":
        return False

    # Unassign borrowed books to avoid FK constraint issues
    for book in list(user.borrowed_books):
        book.borrowed_by = None

    db.delete(user)
    db.commit()
    return True
