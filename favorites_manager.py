import sqlite3
from db_manager import get_connection


class FavoritesManager:
    def add_favorite(self, user_id, item_id):
        connection = None
        try:
            connection, cursor = get_connection()

            cursor.execute(
                """
                INSERT INTO favorites (user_id, item_id)
                VALUES (?, ?)
                """,
                (user_id, item_id)
            )

            connection.commit()
            print("Item added to favorites.")
            return True

        except sqlite3.IntegrityError:
            print("That item is already in favorites, or the user/item does not exist.")
            return False

        except sqlite3.Error as error:
            print(f"Error adding favorite: {error}")
            return False

        finally:
            if connection:
                connection.close()

    def remove_favorite(self, user_id, item_id):
        connection = None
        try:
            connection, cursor = get_connection()

            cursor.execute(
                """
                DELETE FROM favorites
                WHERE user_id = ? AND item_id = ?
                """,
                (user_id, item_id)
            )

            if cursor.rowcount == 0:
                print("Favorite not found.")
                return False

            connection.commit()
            print("Item removed from favorites.")
            return True

        except sqlite3.Error as error:
            print(f"Error removing favorite: {error}")
            return False

        finally:
            if connection:
                connection.close()

    def is_favorite(self, user_id, item_id):
        connection = None
        try:
            connection, cursor = get_connection()

            cursor.execute(
                """
                SELECT 1
                FROM favorites
                WHERE user_id = ? AND item_id = ?
                """,
                (user_id, item_id)
            )

            row = cursor.fetchone()
            return row is not None

        except sqlite3.Error as error:
            print(f"Error checking favorite: {error}")
            return False

        finally:
            if connection:
                connection.close()

    def get_all_favorites(self, user_id):
        connection = None
        try:
            connection, cursor = get_connection()

            cursor.execute(
                """
                SELECT
                    ei.item_id,
                    ei.title,
                    ei.type,
                    ei.genre,
                    ei.release_date,
                    ei.rating,
                    ei.runtime,
                    ei.description,
                    ei.year,
                    ei.director,
                    ei.cast_members,
                    ei.source,
                    ei.external_id,
                    f.added_at
                FROM favorites f
                JOIN entertainment_items ei
                    ON f.item_id = ei.item_id
                WHERE f.user_id = ?
                ORDER BY f.added_at DESC
                """,
                (user_id,)
            )

            return cursor.fetchall()

        except sqlite3.Error as error:
            print(f"Error getting favorites: {error}")
            return []

        finally:
            if connection:
                connection.close()

    def search_favorites(self, user_id, keyword):
        connection = None
        try:
            connection, cursor = get_connection()

            pattern = "%" + keyword + "%"

            cursor.execute(
                """
                SELECT
                    ei.item_id,
                    ei.title,
                    ei.type,
                    ei.genre,
                    ei.release_date,
                    ei.rating,
                    ei.runtime,
                    ei.description,
                    ei.year,
                    ei.director,
                    ei.cast_members,
                    ei.source,
                    ei.external_id,
                    f.added_at
                FROM favorites f
                JOIN entertainment_items ei
                    ON f.item_id = ei.item_id
                WHERE f.user_id = ?
                  AND (
                      ei.title LIKE ?
                      OR ei.genre LIKE ?
                      OR ei.type LIKE ?
                      OR ei.description LIKE ?
                      OR ei.director LIKE ?
                      OR ei.cast_members LIKE ?
                  )
                ORDER BY f.added_at DESC
                """,
                (user_id, pattern, pattern, pattern, pattern, pattern, pattern)
            )

            return cursor.fetchall()

        except sqlite3.Error as error:
            print(f"Error searching favorites: {error}")
            return []

        finally:
            if connection:
                connection.close()