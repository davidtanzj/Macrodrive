import os
import re
import sqlite3

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SQLITE_DATABASE = os.getenv("SQLITE_DATABASE", "Macrodrive.db")


def using_postgres():
    return bool(DATABASE_URL)


class Connection:
    def __init__(self):
        self.postgres = using_postgres()

        if self.postgres:
            import psycopg2
            from psycopg2.extras import DictCursor

            self._dict_cursor = DictCursor
            self._connection = psycopg2.connect(DATABASE_URL)
        else:
            self._dict_cursor = None
            self._connection = sqlite3.connect(SQLITE_DATABASE)

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

        return Cursor(raw, self.postgres)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
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
                        CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END,
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
            self._cursor.execute(converted)
        else:
            self._cursor.execute(converted, params)

        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __iter__(self):
        return iter(self._cursor)


def connect_database():
    return Connection()
