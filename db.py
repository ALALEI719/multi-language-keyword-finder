import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "data.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                credits INTEGER DEFAULT 10,
                api_key TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                keyword TEXT,
                country TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                credits_used INTEGER DEFAULT 0
            )
            """
        )
        conn.commit()


def create_user(email: str, password_hash: str, credits: int = 5) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (email, password_hash, credits) VALUES (?, ?, ?)",
            (email.strip().lower(), password_hash, credits),
        )
        conn.commit()
        return int(cur.lastrowid)


def get_user_by_email(email: str):
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email.strip().lower(),),
        )
        return cur.fetchone()


def get_user_by_id(user_id: int):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cur.fetchone()


def update_user_api_key(user_id: int, api_key: str):
    with get_conn() as conn:
        conn.execute("UPDATE users SET api_key = ? WHERE id = ?", (api_key.strip(), user_id))
        conn.commit()


def adjust_credits(user_id: int, delta: int):
    with get_conn() as conn:
        conn.execute("UPDATE users SET credits = credits + ? WHERE id = ?", (delta, user_id))
        conn.commit()


def deduct_credit_if_possible(user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("SELECT credits FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return False
        if int(row["credits"]) <= 0:
            return False
        conn.execute("UPDATE users SET credits = credits - 1 WHERE id = ?", (user_id,))
        conn.commit()
        return True


def log_query(user_id: int | None, session_id: str, keyword: str, country: str, credits_used: int = 0):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO query_log (user_id, session_id, keyword, country, credits_used)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, session_id, keyword, country, credits_used),
        )
        conn.commit()


def list_users():
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, email, credits, created_at, api_key FROM users ORDER BY created_at DESC"
        )
        return cur.fetchall()
