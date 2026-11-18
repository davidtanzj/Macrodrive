import os
import re
import sqlite3
import threading
import time

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_DATABASE = os.getenv("SQLITE_DATABASE", "Macrodrive.db")

# Pre-import the psycopg2 submodules on the main thread at module load, rather
# than lazily inside functions. The lazy imports race on Python's per-module
# import lock when the background database-init thread and the first request
# handler both call connect_database() concurrently, which hangs the request
# long enough to trip gunicorn's 30s worker timeout.
if DATABASE_URL:
    from psycopg2.extras import DictCursor  # noqa: F401
    from psycopg2.pool import ThreadedConnectionPool  # noqa: F401

_POOL = None
_POOL_LOCK = threading.Lock()

POSTGRES_MIN_CONNECTIONS = 1
POSTGRES_MAX_CONNECTIONS = 5
POSTGRES_CONNECT_TIMEOUT = 15
POSTGRES_RETRIES = 3
POSTGRES_RETRY_DELAY = 2


def using_postgres():
    return bool(DATABASE_URL)


def _get_pool():
    global _POOL

    if _POOL is not None:
        return _POOL

    with _POOL_LOCK:
        if _POOL is not None:
            return _POOL

        from psycopg2.pool import ThreadedConnectionPool

        last_error = None

        for attempt in range(1, POSTGRES_RETRIES + 1):
            try:
                _POOL = ThreadedConnectionPool(
                    POSTGRES_MIN_CONNECTIONS,
                    POSTGRES_MAX_CONNECTIONS,
                    dsn=DATABASE_URL,
                    connect_timeout=POSTGRES_CONNECT_TIMEOUT,
                    application_name="macrodrive",
                )
                return _POOL
            except Exception as error:
                last_error = error

                if attempt < POSTGRES_RETRIES:
                    time.sleep(
                        POSTGRES_RETRY_DELAY * attempt
                    )

        raise last_error


def _checkout_postgres_connection():
    pool = _get_pool()
    last_error = None

    for attempt in range(1, POSTGRES_RETRIES + 1):
        connection = None

        try:
            connection = pool.getconn()

            if connection.closed:
                pool.putconn(
                    connection,
                    close=True,
                )
                connection = None
                continue

            connection.autocommit = False

            # Validate pooled connections before handing them to callers.
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.execute(
                    "SET statement_timeout = '30s'"
                )
                cursor.execute(
                    "SET lock_timeout = '10s'"
                )

            return connection

        except Exception as error:
            last_error = error

            if connection is not None:
                try:
                    pool.putconn(
                        connection,
                        close=True,
                    )
                except Exception:
                    pass

            if attempt < POSTGRES_RETRIES:
                time.sleep(
                    POSTGRES_RETRY_DELAY * attempt
                )

    raise last_error


class Connection:
    def __init__(self):
        self.postgres = using_postgres()
        self._closed = False

        if self.postgres:
            from psycopg2.extras import DictCursor

            self._dict_cursor = DictCursor
            self._pool = _get_pool()
            self._connection = (
                _checkout_postgres_connection()
            )
        else:
            self._dict_cursor = None
            self._pool = None
            self._connection = sqlite3.connect(
                SQLITE_DATABASE
            )

    @property
    def row_factory(self):
        if self.postgres:
            return None
        return self._connection.row_factory

    @row_factory.setter
    def row_factory(self, value):
        if not self.postgres:
            self._connection.row_factory = value

    def cursor(self):
        if self.postgres:
            raw = self._connection.cursor(
                cursor_factory=self._dict_cursor
            )
        else:
            raw = self._connection.cursor()

        return Cursor(
            raw,
            self.postgres,
        )

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        if self._closed:
            return

        self._closed = True

        if self.postgres:
            try:
                # A caller may close after an exception without explicitly
                # rolling back. Ensure the pooled connection is clean.
                self._connection.rollback()
            except Exception:
                pass

            try:
                if self._connection.closed:
                    self._pool.putconn(
                        self._connection,
                        close=True,
                    )
                else:
                    self._pool.putconn(
                        self._connection
                    )
            except Exception:
                try:
                    self._connection.close()
                except Exception:
                    pass
        else:
            self._connection.close()


class Cursor:
    def __init__(self, cursor, postgres):
        self._cursor = cursor
        self.postgres = postgres

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def _convert(self, sql):
        if not self.postgres:
            return sql

        sql = sql.replace("?", "%s")

        sql = re.sub(
            r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
            "SERIAL PRIMARY KEY",
            sql,
            flags=re.IGNORECASE,
        )

        if re.search(
            r"\bINSERT\s+OR\s+IGNORE\s+INTO\b",
            sql,
            flags=re.IGNORECASE,
        ):
            sql = re.sub(
                r"\bINSERT\s+OR\s+IGNORE\s+INTO\b",
                "INSERT INTO",
                sql,
                count=1,
                flags=re.IGNORECASE,
            )

            sql = sql.rstrip().rstrip(";")
            sql += " ON CONFLICT DO NOTHING"

        return sql

    def execute(self, sql, params=None):
        if self.postgres:
            pragma = re.match(
                r"\s*PRAGMA\s+table_info\(([^)]+)\)",
                sql,
                flags=re.IGNORECASE,
            )

            if pragma:
                table_name = pragma.group(1).strip()

                self._cursor.execute(
                    """
                    SELECT
                        ordinal_position - 1,
                        column_name,
                        data_type,
                        CASE
                            WHEN is_nullable = 'NO'
                            THEN 1
                            ELSE 0
                        END,
                        column_default,
                        0
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (table_name,),
                )

                return self

        converted = self._convert(sql)

        if params is None:
            self._cursor.execute(
                converted
            )
        else:
            self._cursor.execute(
                converted,
                params,
            )

        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)


def connect_database():
    return Connection()
