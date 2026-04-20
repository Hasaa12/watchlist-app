import sqlite3
from db_manager import get_connection

class RatingsManager:
    # Inserts a rating (1-10) and text review into db
    def add_review(self, user_id, item_id, rating, review_text):
        connection = None
        try:
            connection, cursor = get_connection()
            sql = """
                INSERT INTO ratings_reviews (user_id, item_id, user_rating, review_text) 
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, (user_id, item_id, rating, review_text))
            connection.commit()
            print("Success: Review added!")

        except sqlite3.Error as e:
            print(f"Database Error while adding review: {e}")
        finally:
            if connection:
                connection.close()

    # Updates an existing review
    def edit_review(self, review_id, new_rating, new_review_text):
        connection = None
        try:
            connection, cursor = get_connection()
            sql = """
                UPDATE ratings_reviews 
                SET user_rating = ?, review_text = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE review_id = ?
            """
            cursor.execute(sql, (new_rating, new_review_text, review_id))
            connection.commit()
            print("Success: Review updated!")

        except sqlite3.Error as e:
            print(f"Database Error while editing review: {e}")
        finally:
            if connection:
                connection.close()

    # Returns all reviews for a specific item
    def get_reviews_for_item(self, item_id):
        connection = None
        try:
            connection, cursor = get_connection()
            sql = "SELECT * FROM ratings_reviews WHERE item_id = ?"
            cursor.execute(sql, (item_id,))
            return cursor.fetchall()

        except sqlite3.Error as e:
            print(f"Database Error while fetching item reviews: {e}")
            return []
        finally:
            if connection:
                connection.close()

    # Returns all reviews by the logged-in user
    def get_user_reviews(self, user_id):
        connection = None
        try:
            connection, cursor = get_connection()
            sql = "SELECT * FROM ratings_reviews WHERE user_id = ?"
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()

        except sqlite3.Error as e:
            print(f"Database Error while fetching user reviews: {e}")
            return []
        finally:
            if connection:
                connection.close()