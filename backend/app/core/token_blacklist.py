"""Token blacklisting using SQLite."""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "token_blacklist.db")


def _get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS blacklisted_tokens (
            token_jti TEXT PRIMARY KEY,
            expires_at TEXT NOT NULL
        )
    """)
    db.commit()
    return db


def blacklist_token(token_jti: str, expires_at: datetime):
    db = _get_db()
    try:
        db.execute(
            "INSERT OR REPLACE INTO blacklisted_tokens (token_jti, expires_at) VALUES (?, ?)",
            (token_jti, expires_at.isoformat())
        )
        db.commit()
    finally:
        db.close()


def is_token_blacklisted(token_jti: str) -> bool:
    db = _get_db()
    try:
        cursor = db.execute("SELECT 1 FROM blacklisted_tokens WHERE token_jti = ?", (token_jti,))
        return cursor.fetchone() is not None
    finally:
        db.close()


def cleanup_expired_tokens():
    db = _get_db()
    try:
        now = datetime.utcnow().isoformat()
        db.execute("DELETE FROM blacklisted_tokens WHERE expires_at < ?", (now,))
        db.commit()
    finally:
        db.close()
