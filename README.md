# Bookflix

Bookflix is a small FastAPI application for managing a personal/shared book library.

## Database

Bookflix uses PostgreSQL. Configure a single environment variable:

- `DATABASE_URL`: complete PostgreSQL connection URI, including the username and password, for example `postgresql://bookflix:password@db.example.internal:5432/bookflix`

The old `POSTGRES_URL`, `POSTGRES_USER` and `POSTGRES_PASSWORD` variables are no longer used.
Percent-encode reserved characters in credentials (e.g. `@` as `%40`, `/` as `%2F`).
Connection options such as `?sslmode=require` are supported. Keep real credentials
out of source control.

Copy `.env.example` to `.env` for local Docker Compose use.

## Migrating an existing SQLite library

The application no longer reads `library.db` directly. To move an existing Bookflix database
into an empty PostgreSQL database, set `DATABASE_URL` to the destination database (including
credentials) and run:

```bash
export DATABASE_URL='postgresql://bookflix:password@db.example.internal:5432/bookflix'
python -m scripts.migrate_sqlite_to_postgres /path/to/library.db
```

The migration copies categories, students and books while preserving IDs and relationships,
then resets PostgreSQL sequences. It refuses to run if any target application table already
contains rows.

Keep a backup of the SQLite file until the PostgreSQL deployment has been verified.
