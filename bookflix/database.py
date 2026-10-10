from __future__ import annotations

import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _database_url():
    url = make_url(_required("DATABASE_URL"))

    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+psycopg")
    elif url.drivername != "postgresql+psycopg":
        raise RuntimeError(
            "DATABASE_URL must use the postgres://, postgresql:// or postgresql+psycopg:// scheme"
        )

    return url


engine = create_engine(_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upgrade_schema():
    """Apply the small schema changes needed by newer app versions."""
    with engine.begin() as connection:
        columns = {
            column["name"] for column in inspect(connection).get_columns("books")
        }
        if "category_id" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE books ADD COLUMN category_id "
                    "INTEGER REFERENCES categories(id)"
                )
            )

        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_categories_name_lower "
                "ON categories (LOWER(name))"
            )
        )
