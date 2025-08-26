# project_files/database/db_connector.py
import os
import mysql.connector
from urllib.parse import urlparse

def connectDB():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")

    p = urlparse(url)
    return mysql.connector.connect(
        user=p.username,
        password=p.password,
        host=p.hostname,
        port=int(p.port) if p.port else 3306,
        database=p.path.lstrip("/"),
        autocommit=False,
        raise_on_warnings=True,
    )

def query(conn, sql, params=None):
    """
    SELECT  -> returns list[dict]
    DML/DDL -> returns int rowcount
    Always buffers and fully drains all result sets to avoid
    'Unread result found' (common with CALL ... that returns rows).
    """
    cur = conn.cursor(dictionary=True, buffered=True)  # <-- buffered
    try:
        cur.execute(sql, params or [])

        rows = []
        saw_rows = False

        # initial result
        if cur.with_rows:
            rows.extend(cur.fetchall())
            saw_rows = True

        # drain any additional result sets (e.g., from stored procedures)
        while cur.nextset():
            if cur.with_rows:
                cur.fetchall()   # drain; we don't need to keep them
                saw_rows = True

        if saw_rows:
            return rows
        else:
            conn.commit()
            return cur.rowcount
    finally:
        cur.close()
