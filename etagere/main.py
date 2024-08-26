from os import stat
from datetime import datetime
from typing import Annotated
from fastapi import (
    FastAPI,
    Depends,
    Request,
    UploadFile,
    File,
    HTTPException,
    status,
    Form,
    Cookie,
)
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from etagere import models, crud, database, auth, camera, book_utils
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
templates.env.filters["showtime"] = datetime.fromtimestamp
models.Base.metadata.create_all(bind=database.engine)


##### CREATE USERS #####
@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db),
):
    user = crud.add_user(db, username, password)
    if user is None:
        raise HTTPException(status_code=400, detail="Could not register")
    return login_post(username, password, db)


###################
### login
###################


@app.get("/login")
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_post(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(database.get_db),
):
    user = auth.authenticate_user(db, username, password)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Could not register user (something is fucked in the code)",
        )
    response = RedirectResponse("/books/my", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie("Authorization", f"Bearer {user.username}")
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("Authorization")
    return response


@app.get("/users")
def users(db: Session = Depends(database.get_db)):
    return crud.all_users(db)


######
# books
######


@app.get("/books")
def books(
    db: Session = Depends(database.get_db),
    user: models.Student | None = Depends(auth.cookie_verify),
):
    books = crud.all_books(db)
    students = list(book.borrowed_by for book in books)
    students.sort(key=lambda x: x.username if x else "zzzzzzzzzzzzzzzz")
    books_by_student = {
        student: [book for book in books if book.borrowed_by == student]
        for student in students
    }
    return templates.TemplateResponse(
        "book.wid", {"request": {}, "books_by_student": books_by_student, "user": user}
    )


@app.get("/books/borrow")
def borrow_book_query(isbn: str):
    return RedirectResponse(f"/books/borrow/{isbn}")


@app.get("/books/borrow/{isbn}")
def borrow_book(
    isbn: str,
    db: Session = Depends(database.get_db),
    user: models.Student = Depends(auth.cookie_verify),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    book = crud.get_book_by_isbn(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    crud.borrow_book(db, user, book)
    return RedirectResponse("/books/my")


@app.get("/books/return")
def borrow_book_query(isbn: str):
    return RedirectResponse(f"/books/return/{isbn}")


@app.post("/books/photo")
def borrow_book_by_photo(
    photo: UploadFile = File(...),
    user: models.Student = Depends(auth.cookie_verify),
    db: Session = Depends(database.get_db),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    image_path = f"uploads/{photo.filename}"
    with open(image_path, "wb") as f:
        f.write(photo.file.read())
    isbn = camera.scan_barcode(image_path)
    if not isbn:
        raise HTTPException(status_code=400, detail="Could not read the barcode")
    book = crud.get_book_by_isbn(db, isbn)

    if book.borrowed_by == user:
        return RedirectResponse(
            f"/books/return/{isbn}", status_code=status.HTTP_303_SEE_OTHER
        )
    else:
        return RedirectResponse(
            f"/books/borrow/{isbn}", status_code=status.HTTP_303_SEE_OTHER
        )


@app.get("/books/return/{isbn}")
def return_book(
    isbn: str,
    db: Session = Depends(database.get_db),
    user: models.Student = Depends(auth.cookie_verify),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    book = crud.get_book_by_isbn(db, isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    crud.return_book(db, book)
    return RedirectResponse("/books/my")


@app.get("/books/my")
def my_books(
    db: Session = Depends(database.get_db),
    user: models.Student = Depends(auth.cookie_verify),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    books = crud.my_books(db, user)
    return templates.TemplateResponse(
        "book.wid", {"request": {}, "books_by_student": {user: books}, "user": user}
    )


################


@app.get("/users")
def users(db: Session = Depends(database.get_db)):
    users = crud.all_users(db)
    return templates.TemplateResponse(
        "users.html", {"request": {}, "users": crud.all_users(db)}
    )


@app.get("/")
def read_root(
    request: Request, current_user: models.Student = Depends(auth.cookie_verify)
):
    if current_user is None:
        return templates.TemplateResponse(
            "login.html", {"request": request, "user": current_user}
        )
    else:
        return RedirectResponse("/books/my")
