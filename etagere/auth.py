from typing import Annotated
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from etagere import models, database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.Student).filter(models.Student.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user


def get_current_user(token: str, db: Session):
    # Placeholder for token verification
    user = db.query(models.Student).filter(models.Student.username == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication"
        )
    return user


def cookie_verify(
    db: Session = Depends(database.get_db),
    Authorization: Annotated[str | None, Cookie()] = None,
):
    if not Authorization:
        return None

    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization format invalid")

    tok = Authorization.split(" ")[1]
    user = get_current_user(tok, db)
    return user
