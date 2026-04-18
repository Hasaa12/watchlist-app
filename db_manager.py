

import sqlite3
from pathlib import Path


# Database file will be created in the same folder as this file.
DB_PATH = Path(__file__).resolve().parent / "watchlist.db"


def get_connection():

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row  # Lets us access columns by name.
    cursor = connection.cursor()

    # Turn on foreign key support in SQLite.
    cursor.execute("PRAGMA foreign_keys = ON;")

    return connection, cursor


def test_connection():

    try:
        connection, _ = get_connection()
        print(f"Database connected successfully: {DB_PATH}")
        connection.close()
    except sqlite3.Error as error:
        print(f"Database connection error: {error}")


if __name__ == "__main__":
    test_connection()
