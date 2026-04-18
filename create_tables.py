
import sqlite3
from db_manager import get_connection


def create_users_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def create_entertainment_items_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS entertainment_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            genre TEXT,
            release_date TEXT,
            rating REAL,
            runtime INTEGER,
            description TEXT,
            year INTEGER,
            director TEXT,
            cast_members TEXT,
            source TEXT,
            external_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def create_user_lists_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_lists (
            list_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'plan to watch',
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            UNIQUE(user_id, item_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES entertainment_items(item_id) ON DELETE CASCADE
        );
        """
    )


def create_ratings_reviews_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ratings_reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            user_rating REAL CHECK(user_rating >= 1 AND user_rating <= 10),
            review_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES entertainment_items(item_id) ON DELETE CASCADE
        );
        """
    )


def create_favorites_table(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES entertainment_items(item_id) ON DELETE CASCADE
        );
        """
    )


def create_all_tables():

    connection = None
    try:
        connection, cursor = get_connection()

        create_users_table(cursor)
        create_entertainment_items_table(cursor)
        create_user_lists_table(cursor)
        create_ratings_reviews_table(cursor)
        create_favorites_table(cursor)

        connection.commit()
        print("All tables were created successfully.")

    except sqlite3.Error as error:
        print(f"Error creating tables: {error}")

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    create_all_tables()
