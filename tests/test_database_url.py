import os
import unittest
from unittest.mock import patch


class DatabaseURLTests(unittest.TestCase):
    def _database(self):
        # Import after setting POSTGRES_URL: the module constructs the Engine on import.
        with patch.dict(
            os.environ,
            {"POSTGRES_URL": "postgresql://test:password@localhost:5432/bookflix_test"},
        ):
            from bookflix import database
        return database

    def test_complete_uri(self):
        database = self._database()
        with patch.dict(
            os.environ,
            {
                "POSTGRES_URL": (
                    "postgresql://bookflix:p%40ss%2Fword@db.internal:5432/"
                    "bookflix?sslmode=require"
                )
            },
        ):
            url = database._database_url()

        self.assertEqual(url.drivername, "postgresql+psycopg")
        self.assertEqual(url.username, "bookflix")
        self.assertEqual(url.password, "p@ss/word")
        self.assertEqual(url.host, "db.internal")
        self.assertEqual(url.database, "bookflix")
        self.assertEqual(url.query["sslmode"], "require")

    def test_missing_url(self):
        database = self._database()
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "POSTGRES_URL"):
                database._database_url()

    def test_reject_sqlite(self):
        database = self._database()
        with patch.dict(os.environ, {"POSTGRES_URL": "sqlite:///library.db"}):
            with self.assertRaisesRegex(RuntimeError, "POSTGRES_URL"):
                database._database_url()


if __name__ == "__main__":
    unittest.main()
