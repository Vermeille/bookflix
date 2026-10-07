# Bookflix

Bookflix is a small FastAPI application for managing a personal/shared book library.

## Database

Bookflix uses PostgreSQL. Configure the connection with three environment variables:

- `POSTGRES_URL`: server and database, for example `postgresql://db.example.internal:5432/bookflix`
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASSWORD`: PostgreSQL password

Credentials are kept separate from the URL. The URL may include normal PostgreSQL connection
options such as `?sslmode=require`.

Copy `.env.example` to `.env` for local Docker Compose use.

## Migrating an existing SQLite library

The application no longer reads `library.db` directly. To move an existing Bookflix database
into an empty PostgreSQL database, configure the `POSTGRES_*` variables and run:

```bash
python -m scripts.migrate_sqlite_to_postgres /path/to/library.db
```

The migration copies categories, students and books while preserving IDs and relationships,
then resets PostgreSQL sequences. It refuses to run if any target application table already
contains rows.

Keep a backup of the SQLite file until the PostgreSQL deployment has been verified.
