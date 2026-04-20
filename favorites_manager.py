import sqlite3
from db_manager import get_connection


class FavoritesManager:

    def add_favorite(self, user_id, item_id):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                "INSERT INTO favorites (user_id, item_id) VALUES (?, ?)",
                (user_id, item_id)
            )
            connection.commit()
            print("Added to favorites!")
            return True
        except sqlite3.IntegrityError:
            print("That item is already in your favorites.")
            return False
        except sqlite3.Error as e:
            print(f"Error adding favorite: {e}")
            return False
        finally:
            if connection:
                connection.close()

    def remove_favorite(self, user_id, item_id):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                "DELETE FROM favorites WHERE user_id = ? AND item_id = ?",
                (user_id, item_id)
            )
            if cursor.rowcount == 0:
                print("Item not found in favorites.")
                return False
            connection.commit()
            print("Removed from favorites.")
            return True
        except sqlite3.Error as e:
            print(f"Error removing favorite: {e}")
            return False
        finally:
            if connection:
                connection.close()

    def get_user_favorites(self, user_id):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                """
                SELECT ei.item_id, ei.title, ei.type, ei.genre, ei.year, f.added_at
                FROM favorites f
                JOIN entertainment_items ei ON f.item_id = ei.item_id
                WHERE f.user_id = ?
                ORDER BY f.added_at DESC
                """,
                (user_id,)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting favorites: {e}")
            return []
        finally:
            if connection:
                connection.close()
