from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:////app/library.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def upgrade_schema():
    """Apply the small SQLite schema changes needed by newer app versions."""
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR COLLATE NOCASE NOT NULL UNIQUE
                )
                """
            )
        )

        columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(books)"))
        }
        if "category_id" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE books ADD COLUMN category_id "
                    "INTEGER REFERENCES categories(id)"
                )
            )
