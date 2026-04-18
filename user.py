

import sqlite3
import bcrypt
from db_manager import get_connection


class User:
    def __init__(self, user_id=None, username="", email="", password_hash=None, created_at=None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    @staticmethod
    def _validate_registration_input(username, email, password):
        if not username or not email or not password:
            raise ValueError("Username, email, and password are required.")

        if len(username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long.")

        if "@" not in email or "." not in email:
            raise ValueError("Please enter a valid email address.")

        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

    @staticmethod
    def register(username, email, password):
        """
        Register a new user.
        Returns a User object if successful, otherwise None.
        """
        connection = None
        try:
            User._validate_registration_input(username, email, password)

            connection, cursor = get_connection()

            # Hash the password before saving it.
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (username.strip(), email.strip().lower(), password_hash)
            )
            connection.commit()

            new_user_id = cursor.lastrowid
            print("Registration successful.")

            return User(
                user_id=new_user_id,
                username=username.strip(),
                email=email.strip().lower(),
                password_hash=password_hash
            )

        except ValueError as error:
            print(f"Input error: {error}")
            return None

        except sqlite3.IntegrityError:
            print("That username or email is already in use.")
            return None

        except sqlite3.Error as error:
            print(f"Database error during registration: {error}")
            return None

        finally:
            if connection:
                connection.close()

    @staticmethod
    def login(username, password):

        connection = None
        try:
            if not username or not password:
                raise ValueError("Username and password are required.")

            connection, cursor = get_connection()
            cursor.execute(
                """
                SELECT user_id, username, email, password_hash, created_at
                FROM users
                WHERE username = ?
                """,
                (username.strip(),)
            )
            row = cursor.fetchone()

            if row is None:
                print("No account was found with that username.")
                return None

            stored_hash = row["password_hash"]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode("utf-8")

            if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
                print("Login successful.")
                return User(
                    user_id=row["user_id"],
                    username=row["username"],
                    email=row["email"],
                    password_hash=stored_hash,
                    created_at=row["created_at"]
                )

            print("Incorrect password.")
            return None

        except ValueError as error:
            print(f"Input error: {error}")
            return None

        except sqlite3.Error as error:
            print(f"Database error during login: {error}")
            return None

        finally:
            if connection:
                connection.close()


def run_basic_auth_test():

    print("\n--- Basic User Auth Test ---")
    print("1. Register")
    print("2. Login")

    choice = input("Choose an option: ").strip()

    if choice == "1":
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        user = User.register(username, email, password)
        if user:
            print(f"Created user: {user.username}")

    elif choice == "2":
        username = input("Enter username: ")
        password = input("Enter password: ")
        user = User.login(username, password)
        if user:
            print(f"Welcome back, {user.username}!")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    run_basic_auth_test()
