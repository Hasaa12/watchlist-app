import sqlite3
from db_manager import get_connection


class RatingsManager:

    def _get_item_id_by_title(self, cursor, title_or_id):
        try:
            return int(title_or_id)
        except (ValueError, TypeError):
            pass

        cursor.execute(
            "SELECT item_id FROM entertainment_items WHERE LOWER(title) = LOWER(?)",
            (str(title_or_id).strip(),)
        )
        row = cursor.fetchone()
        if row:
            return row["item_id"]

        cursor.execute(
            "SELECT item_id FROM entertainment_items WHERE LOWER(title) LIKE LOWER(?)",
            (f"%{str(title_or_id).strip()}%",)
        )
        row = cursor.fetchone()
        if row:
            return row["item_id"]

        return None

    def add_review(self, user_id, title_or_id, rating, review_text):
        connection = None
        try:
            connection, cursor = get_connection()

            item_id = self._get_item_id_by_title(cursor, title_or_id)
            if item_id is None:
                print(f"Could not find '{title_or_id}' in the database.")
                return False

            cursor.execute(
                """
                INSERT INTO ratings_reviews (user_id, item_id, user_rating, review_text)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, item_id, rating, review_text)
            )
            connection.commit()
            print("Review added!")
            return True

        except sqlite3.IntegrityError:
            print("You already reviewed this item. Use edit instead.")
            return False
        except sqlite3.Error as e:
            print(f"Database error while adding review: {e}")
            return False
        finally:
            if connection:
                connection.close()

    def edit_review(self, review_id, new_rating, new_review_text):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                """
                UPDATE ratings_reviews
                SET user_rating = ?, review_text = ?, updated_at = CURRENT_TIMESTAMP
                WHERE review_id = ?
                """,
                (new_rating, new_review_text, review_id)
            )
            if cursor.rowcount == 0:
                print("No review found with that ID.")
                return False
            connection.commit()
            print("Review updated!")
            return True
        except sqlite3.Error as e:
            print(f"Database error while editing review: {e}")
            return False
        finally:
            if connection:
                connection.close()

    def get_reviews_for_item(self, item_id):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                "SELECT * FROM ratings_reviews WHERE item_id = ?",
                (item_id,)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error while fetching item reviews: {e}")
            return []
        finally:
            if connection:
                connection.close()

    def get_user_reviews(self, user_id):
        connection = None
        try:
            connection, cursor = get_connection()
            cursor.execute(
                """
                SELECT rr.review_id, rr.user_id, ei.title, rr.user_rating, rr.review_text
                FROM ratings_reviews rr
                JOIN entertainment_items ei ON rr.item_id = ei.item_id
                WHERE rr.user_id = ?
                """,
                (user_id,)
            )
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error while fetching user reviews: {e}")
            return []
        finally:
            if connection:
                connection.close()
