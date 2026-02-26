import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime
import os


class Database:
    def __init__(self, db_path: str = "price_tracker.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Create a database connection."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialize database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tracked items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                title TEXT,
                current_price REAL,
                initial_price REAL,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        # Price history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                price REAL NOT NULL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES tracked_items (id)
            )
        """)

        conn.commit()
        conn.close()

    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add a new user or update existing."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))

        conn.commit()
        conn.close()

    def add_tracked_item(self, user_id: int, url: str, title: str = None, price: float = None) -> int:
        """Add a new tracked item."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tracked_items (user_id, url, title, current_price, initial_price, last_checked)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, url, title, price, price, datetime.now()))

        item_id = cursor.lastrowid

        # Add to price history
        if price is not None:
            cursor.execute("""
                INSERT INTO price_history (item_id, price)
                VALUES (?, ?)
            """, (item_id, price))

        conn.commit()
        conn.close()

        return item_id

    def get_user_items(self, user_id: int, active_only: bool = True) -> List[Tuple]:
        """Get all tracked items for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT id, url, title, current_price, initial_price, last_checked, created_at
            FROM tracked_items
            WHERE user_id = ?
        """

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY created_at DESC"

        cursor.execute(query, (user_id,))
        items = cursor.fetchall()

        conn.close()
        return items

    def get_all_active_items(self) -> List[Tuple]:
        """Get all active tracked items across all users."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_id, url, title, current_price, last_checked
            FROM tracked_items
            WHERE is_active = 1
            ORDER BY last_checked ASC
        """)

        items = cursor.fetchall()
        conn.close()

        return items

    def update_item_price(self, item_id: int, new_price: float) -> bool:
        """Update item price and add to history."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get current price
        cursor.execute("SELECT current_price FROM tracked_items WHERE id = ?", (item_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return False

        old_price = result[0]
        price_changed = old_price is None or abs(old_price - new_price) > 0.01

        # Update current price and last checked
        cursor.execute("""
            UPDATE tracked_items
            SET current_price = ?, last_checked = ?
            WHERE id = ?
        """, (new_price, datetime.now(), item_id))

        # Add to price history if price changed
        if price_changed:
            cursor.execute("""
                INSERT INTO price_history (item_id, price)
                VALUES (?, ?)
            """, (item_id, new_price))

        conn.commit()
        conn.close()

        return price_changed

    def delete_item(self, item_id: int, user_id: int) -> bool:
        """Delete (deactivate) a tracked item."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE tracked_items
            SET is_active = 0
            WHERE id = ? AND user_id = ?
        """, (item_id, user_id))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def get_item_by_id(self, item_id: int) -> Optional[Tuple]:
        """Get a specific item by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_id, url, title, current_price, initial_price, last_checked
            FROM tracked_items
            WHERE id = ?
        """, (item_id,))

        item = cursor.fetchone()
        conn.close()

        return item

    def get_price_history(self, item_id: int, limit: int = 10) -> List[Tuple]:
        """Get price history for an item."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT price, checked_at
            FROM price_history
            WHERE item_id = ?
            ORDER BY checked_at DESC
            LIMIT ?
        """, (item_id, limit))

        history = cursor.fetchall()
        conn.close()

        return history
