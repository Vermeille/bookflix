from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from sqlalchemy import text

from bookflix import database, models


TABLES = ("categories", "students", "books")


def _table_exists(source: sqlite3.Connection, table: str) -> bool:
    return (
        source.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()
        is not None
    )


def _read_rows(source: sqlite3.Connection, table: str) -> list[dict[str, object]]:
    if not _table_exists(source, table):
        return []
    return [dict(row) for row in source.execute(f"SELECT * FROM {table}")]


def _assert_target_empty() -> None:
    with database.engine.connect() as target:
        non_empty = {
            table: target.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            for table in TABLES
        }

    populated = {table: count for table, count in non_empty.items() if count}
    if populated:
        details = ", ".join(f"{table}={count}" for table, count in populated.items())
        raise RuntimeError(
            "Refusing to migrate into a non-empty PostgreSQL database: " + details
        )


def _insert_rows(target, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return

    columns = list(rows[0])
    column_sql = ", ".join(columns)
    value_sql = ", ".join(f":{column}" for column in columns)
    target.execute(
        text(f"INSERT INTO {table} ({column_sql}) VALUES ({value_sql})"),
        rows,
    )


def _reset_sequence(target, table: str) -> None:
    target.execute(
        text(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table}', 'id'),
                COALESCE(MAX(id), 1),
                MAX(id) IS NOT NULL
            )
            FROM {table}
            """
        )
    )


def migrate(sqlite_path: Path) -> None:
    if not sqlite_path.is_file():
        raise FileNotFoundError(sqlite_path)

    models.Base.metadata.create_all(bind=database.engine)
    database.upgrade_schema()
    _assert_target_empty()

    source = sqlite3.connect(sqlite_path)
    source.row_factory = sqlite3.Row
    try:
        source_rows = {table: _read_rows(source, table) for table in TABLES}

        with database.engine.begin() as target:
            for table in TABLES:
                _insert_rows(target, table, source_rows[table])
            for table in TABLES:
                _reset_sequence(target, table)
    finally:
        source.close()

    counts = ", ".join(f"{table}={len(source_rows[table])}" for table in TABLES)
    print(f"Migration complete: {counts}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate an existing Bookflix SQLite database to PostgreSQL."
    )
    parser.add_argument(
        "sqlite_path",
        nargs="?",
        default="library.db",
        type=Path,
        help="Path to the existing SQLite database (default: library.db)",
    )
    args = parser.parse_args()
    migrate(args.sqlite_path)


if __name__ == "__main__":
    main()
