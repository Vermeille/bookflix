import time
from sqlalchemy.orm import Session
from bookflix import models
from bookflix.auth import get_password_hash
from bookflix.book_utils import get_book_info_by_isbn, canonical_isbn

###########
# book
###########


def add_book(db: Session, isbn: str, title: str, author: str, cover_url: str):
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
