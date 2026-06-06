"""Optional Postgres sync for mock API server during integration/DB tests."""
import os
from typing import Any, Dict, Optional

import psycopg2


def db_enabled() -> bool:
    """Sync to Postgres only when explicitly enabled and credentials are present."""
    return (
        os.getenv("MOCK_DB_SYNC", "").lower() == "true"
        and bool(os.getenv("DB_PASSWORD"))
    )


def _get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "test_db"),
        user=os.getenv("DB_USER", "test_user"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def insert_user(payload: Dict[str, Any]) -> Optional[int]:
    if not db_enabled():
        return None
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, first_name, last_name)
                    VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (
                        payload.get("email"),
                        payload.get("first_name"),
                        payload.get("last_name"),
                    ),
                )
                user_id = cur.fetchone()[0]
            conn.commit()
            return int(user_id)
        finally:
            conn.close()
    except psycopg2.Error:
        return None


def delete_user(user_id: int) -> None:
    if not db_enabled():
        return
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
        finally:
            conn.close()
    except psycopg2.Error:
        return


def insert_product(payload: Dict[str, Any]) -> Optional[int]:
    if not db_enabled():
        return None
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO products (name, description, price, sku, category, stock)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        payload.get("name"),
                        payload.get("description"),
                        payload.get("price"),
                        payload.get("sku"),
                        payload.get("category"),
                        payload.get("stock", 0),
                    ),
                )
                product_id = cur.fetchone()[0]
            conn.commit()
            return int(product_id)
        finally:
            conn.close()
    except psycopg2.Error:
        return None


def delete_product(product_id: int) -> None:
    if not db_enabled():
        return
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
        finally:
            conn.close()
    except psycopg2.Error:
        return


def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    if not db_enabled():
        return None
    try:
        conn = _get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, price, sku, category, stock
                    FROM products WHERE id = %s
                    """,
                    (product_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": str(row[0]),
                    "name": row[1],
                    "description": row[2],
                    "price": float(row[3]) if row[3] is not None else 0,
                    "sku": row[4],
                    "category": row[5],
                    "stock": row[6],
                }
        finally:
            conn.close()
    except psycopg2.Error:
        return None
