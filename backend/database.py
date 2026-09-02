import json
import os
import sqlite3
from datetime import datetime, timezone

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BACKEND_DIR, "shopassist.db")

DEFAULT_TITLE = "New Chat"


def _now():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't already exist. Safe to call on every startup."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                title TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                extra_json TEXT,
                created_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_products (
                id INTEGER PRIMARY KEY,
                product_id INTEGER,
                name TEXT,
                brand TEXT,
                price REAL,
                image_url TEXT,
                product_url TEXT,
                saved_at TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


# ---- Conversations ----------------------------------------------------

def create_conversation(title=DEFAULT_TITLE):
    now = _now()
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO conversations (title, created_at, updated_at) VALUES (?, ?, ?)",
            (title, now, now),
        )
        conn.commit()
        return {"id": cur.lastrowid, "title": title, "created_at": now}
    finally:
        conn.close()


def list_conversations():
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, updated_at FROM conversations ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def conversation_exists(conversation_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM conversations WHERE id = ?", (conversation_id,)
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def get_conversation_messages(conversation_id):
    """Full ordered message history for a conversation, or None if it doesn't exist."""
    conn = get_connection()
    try:
        conv = conn.execute(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()
        if conv is None:
            return None

        rows = conn.execute(
            "SELECT id, role, content, extra_json, created_at FROM messages "
            "WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,),
        ).fetchall()

        messages = []
        for row in rows:
            message = dict(row)
            extra_json = message.pop("extra_json")
            message["extra"] = json.loads(extra_json) if extra_json else None
            messages.append(message)

        result = dict(conv)
        result["messages"] = messages
        return result
    finally:
        conn.close()


def delete_conversation(conversation_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def add_message(conversation_id, role, content, extra=None):
    now = _now()
    extra_json = json.dumps(extra) if extra is not None else None
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO messages (conversation_id, role, content, extra_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (conversation_id, role, content, extra_json, now),
        )
        conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (now, conversation_id))
        conn.commit()
        return {
            "id": cur.lastrowid,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "extra": extra,
            "created_at": now,
        }
    finally:
        conn.close()


def set_title_if_default(conversation_id, title):
    """Set the conversation's title only if it's still the "New Chat" default."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE conversations SET title = ? WHERE id = ? AND title = ?",
            (title, conversation_id, DEFAULT_TITLE),
        )
        conn.commit()
    finally:
        conn.close()


# ---- Saved products -----------------------------------------------------

def create_saved_product(product_id, name, brand, price, image_url, product_url):
    now = _now()
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO saved_products "
            "(product_id, name, brand, price, image_url, product_url, saved_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (product_id, name, brand, price, image_url, product_url, now),
        )
        conn.commit()
        return {
            "id": cur.lastrowid,
            "product_id": product_id,
            "name": name,
            "brand": brand,
            "price": price,
            "image_url": image_url,
            "product_url": product_url,
            "saved_at": now,
        }
    finally:
        conn.close()


def list_saved_products():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM saved_products ORDER BY saved_at DESC").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_saved_product(saved_id):
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM saved_products WHERE id = ?", (saved_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
