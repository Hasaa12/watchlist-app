import sqlite3
from db_manager import get_connection
from entertainment_item import EntertainmentItem


class WatchlistManager:
    VALID_STATUSES = {"plan to watch", "watching", "completed", "dropped"}

    def _normalize_status(self, status):
        if status is None:
            return "plan to watch"

        cleaned = status.strip().lower()
        if cleaned not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Use one of: {', '.join(sorted(self.VALID_STATUSES))}"
            )
        return cleaned

    def add_item(self, user_id, item_id, status="plan to watch", notes=None):
        connection = None
        try:
            status = self._normalize_status(status)
            connection, cursor = get_connection()

            cursor.execute(
                """
                INSERT INTO user_lists (user_id, item_id, status, notes)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, item_id, status, notes),
            )

            connection.commit()
            print("Item added to watchlist.")
            return True

        except sqlite3.IntegrityError:
            print("That item is already on the watchlist, or the user/item does not exist.")
            return False
        except (sqlite3.Error, ValueError) as error:
            print(f"Error adding item: {error}")
            return False
        finally:
            if connection:
                connection.close()

    def edit_item(self, user_id, item_id, status=None, notes=None):
        connection = None
        try:
            updates = []
            values = []

            if status is not None:
                updates.append("status = ?")
                values.append(self._normalize_status(status))

            if notes is not None:
                updates.append("notes = ?")
                values.append(notes)

            if not updates:
                raise ValueError("Nothing to update.")

            values.extend([user_id, item_id])

            connection, cursor = get_connection()
            cursor.execute(
                f"""
                UPDATE user_lists
                SET {", ".join(updates)}
                WHERE user_id = ? AND item_id = ?
                """,
                values,
            )

            if cursor.rowcount == 0:
                print("No matching watchlist item found.")
                return False

            connection.commit()
            print("Watchlist item updated.")
            return True

        except (sqlite3.Error, ValueError) as error:
            print(f"Error updating item: {error}")
            return False
        finally:
            if connection:
                connection.close()

    def delete_item(self, user_id, item_id):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                """
                DELETE FROM user_lists
                WHERE user_id = ? AND item_id = ?
                """,
                (user_id, item_id),
            )

            if cursor.rowcount == 0:
                print("No matching watchlist item found.")
                return False

            connection.commit()
            print("Item removed from watchlist.")
            return True

        except sqlite3.Error as error:
            print(f"Error deleting item: {error}")
            return False
        finally:
            if connection:
                connection.close()

    def get_all_items(self, user_id):
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
                    ei.year,
                    ei.source,
                    ul.status,
                    ul.date_added,
                    ul.notes
                FROM user_lists ul
                JOIN entertainment_items ei ON ul.item_id = ei.item_id
                WHERE ul.user_id = ?
                ORDER BY ul.date_added DESC
                """,
                (user_id,),
            )

            rows = cursor.fetchall()
            return [EntertainmentItem.from_row(row) for row in rows]

        except sqlite3.Error as error:
            print(f"Error getting watchlist items: {error}")
            return []
        finally:
            if connection:
                connection.close()

    def search_items(self, user_id, query="", genre=None, item_type=None, status=None):
        connection = None
        try:
            sql = """
                SELECT
                    ei.item_id,
                    ei.title,
                    ei.type,
                    ei.genre,
                    ei.release_date,
                    ei.rating,
                    ei.year,
                    ei.source,
                    ul.status,
                    ul.date_added,
                    ul.notes
                FROM user_lists ul
                JOIN entertainment_items ei ON ul.item_id = ei.item_id
                WHERE ul.user_id = ?
            """
            params = [user_id]

            if query:
                pattern = f"%{query}%"
                sql += """
                    AND (
                        ei.title LIKE ?
                        OR ei.genre LIKE ?
                        OR ei.type LIKE ?
                        OR ul.status LIKE ?
                    )
                """
                params.extend([pattern, pattern, pattern, pattern])

            if genre:
                sql += " AND ei.genre LIKE ?"
                params.append(f"%{genre}%")

            if item_type:
                sql += " AND ei.type = ?"
                params.append(item_type.strip().lower())

            if status:
                sql += " AND ul.status = ?"
                params.append(self._normalize_status(status))

            sql += " ORDER BY ul.date_added DESC"

            connection, cursor = get_connection()
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [EntertainmentItem.from_row(row) for row in rows]

        except (sqlite3.Error, ValueError) as error:
            print(f"Error searching watchlist items: {error}")
            return []
        finally:
            if connection:
                connection.close()

    def mark_complete(self, user_id, item_id):
        return self.edit_item(user_id, item_id, status="completed")