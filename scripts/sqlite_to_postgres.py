#!/usr/bin/env python3
"""Bulk-copy selected SQLite tables into an already-migrated PostgreSQL database."""
from __future__ import annotations

import argparse
import os
import sqlite3
from pathlib import Path

import psycopg
from psycopg import sql

TABLE_ORDER = [
    "auth_user",
    "django_session",
    "meetups_meetupuser",
    "meetups_meetup",
    "meetups_registration",
    "meetups_waitlist",
    "meetups_notification",
    "meetups_task",
    "meetups_tasksubmission",
    "meetups_review",
    "meetups_meetuppaymentlink",
]


def sqlite_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')]


def postgres_columns(conn: psycopg.Connection, table: str) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table,),
        )
        return [row[0] for row in cur.fetchall()]


def copy_table(src: sqlite3.Connection, dst: psycopg.Connection, table: str) -> int:
    source_cols = sqlite_columns(src, table)
    target_cols = postgres_columns(dst, table)
    columns = [col for col in source_cols if col in target_cols]
    if not columns:
        return 0

    quoted_columns = ", ".join(f'"{col}"' for col in columns)
    query = f'SELECT {quoted_columns} FROM "{table}"'
    rows = src.execute(query)

    with dst.cursor() as cur:
        with cur.copy(
            sql.SQL("COPY {} ({}) FROM STDIN").format(
                sql.Identifier(table),
                sql.SQL(", ").join(sql.Identifier(col) for col in columns),
            )
        ) as copy:
            count = 0
            for row in rows:
                copy.write_row(row)
                count += 1
    return count


def reset_sequence(conn: psycopg.Connection, table: str) -> None:
    if "id" not in postgres_columns(conn, table):
        return
    with conn.cursor() as cur:
        cur.execute("SELECT pg_get_serial_sequence(%s, 'id')", (table,))
        sequence = cur.fetchone()[0]
        if not sequence:
            return
        cur.execute(
            sql.SQL("SELECT setval({}, COALESCE((SELECT MAX(id) FROM {}), 1), true)").format(
                sql.Literal(sequence),
                sql.Identifier(table),
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite-path", required=True)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL"))
    args = parser.parse_args()

    sqlite_path = Path(args.sqlite_path)
    if not sqlite_path.exists():
        raise SystemExit(f"SQLite file not found: {sqlite_path}")
    if not args.database_url:
        raise SystemExit("DATABASE_URL is required")

    with sqlite3.connect(sqlite_path) as src, psycopg.connect(args.database_url) as dst:
        with dst.cursor() as cur:
            cur.execute(
                sql.SQL("TRUNCATE {} RESTART IDENTITY CASCADE").format(
                    sql.SQL(", ").join(sql.Identifier(table) for table in TABLE_ORDER)
                )
            )
        copied = {}
        for table in TABLE_ORDER:
            copied[table] = copy_table(src, dst, table)
        for table in TABLE_ORDER:
            reset_sequence(dst, table)
        dst.commit()

    for table, count in copied.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
