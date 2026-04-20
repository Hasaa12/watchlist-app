from pathlib import Path
import pandas as pd
from db_manager import get_connection

BASE_DIR = Path(__file__).resolve().parent
TMDB_CANDIDATES = ["tmdb_movies_tv.csv", "tmdb_movies_tv.csv", "tmdb_movies_tv.csv.csv"]
GAME_CANDIDATES = ["games_data.csv"]


def find_file(candidates):
    for name in candidates:
        path = BASE_DIR / name
        if path.exists():
            return path
    raise FileNotFoundError(f"Could not find any of these files: {candidates}")


def normalize_text(value):
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text if text else None


def safe_float(value):
    try:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value):
    try:
        if value is None or pd.isna(value) or str(value).strip() == "":
            return None
        text = str(value).strip()
        if len(text) >= 4 and text[:4].isdigit():
            return int(text[:4]) if "-" in text or "/" in text else int(float(text))
        return int(float(text))
    except (TypeError, ValueError):
        return None


def pick_value(row, *candidates, default=None):
    lowered = {str(col).strip().lower(): col for col in row.index}
    for candidate in candidates:
        key = candidate.strip().lower()
        if key in lowered:
            value = row[lowered[key]]
            if value is not None and not pd.isna(value) and str(value).strip() != "":
                return value
    return default


def insert_item(cursor, item):
    cursor.execute(
        """
        INSERT INTO entertainment_items
        (title, type, genre, release_date, rating, runtime, description, year,
         director, cast_members, source, external_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["title"],
            item["type"],
            item["genre"],
            item["release_date"],
            item["rating"],
            item["runtime"],
            item["description"],
            item["year"],
            item["director"],
            item["cast_members"],
            item["source"],
            item["external_id"],
        ),
    )


def delete_existing_source_rows(cursor, source_name):
    cursor.execute("DELETE FROM entertainment_items WHERE source = ?", (source_name,))


def load_tmdb_csv(cursor):
    file_path = find_file(TMDB_CANDIDATES)
    df = pd.read_csv(file_path)

    delete_existing_source_rows(cursor, "tmdb_csv")
    inserted = 0

    for _, row in df.iterrows():
        title = normalize_text(
            pick_value(row, "title", "name", "movie_title", "tv_title")
        )
        if not title:
            continue

        media_type = normalize_text(
            pick_value(row, "type", "media_type", "content_type")
        )
        if not media_type:
            media_type = "tv" if pick_value(row, "first_air_date", "number_of_seasons") else "movie"

        release_date = normalize_text(
            pick_value(row, "release_date", "first_air_date", "released")
        )

        item = {
            "title": title,
            "type": media_type.lower(),
            "genre": normalize_text(pick_value(row, "genre", "genres")),
            "release_date": release_date,
            "rating": safe_float(pick_value(row, "vote_average", "rating", "score")),
            "runtime": safe_int(pick_value(row, "runtime", "episode_run_time")),
            "description": normalize_text(pick_value(row, "overview", "description", "summary")),
            "year": safe_int(pick_value(row, "year")) or safe_int(release_date),
            "director": normalize_text(pick_value(row, "director", "directors")),
            "cast_members": normalize_text(pick_value(row, "cast", "cast_members", "actors")),
            "source": "tmdb_csv",
            "external_id": normalize_text(pick_value(row, "id", "tmdb_id")),
        }

        insert_item(cursor, item)
        inserted += 1

    return inserted


def load_games_csv(cursor):
    file_path = find_file(GAME_CANDIDATES)
    df = pd.read_csv(file_path)

    delete_existing_source_rows(cursor, "games_csv")
    inserted = 0

    for _, row in df.iterrows():
        title = normalize_text(
            pick_value(row, "title", "name", "game", "game_name")
        )
        if not title:
            continue

        release_date = normalize_text(
            pick_value(row, "release_date", "released", "release year", "year")
        )

        item = {
            "title": title,
            "type": "game",
            "genre": normalize_text(pick_value(row, "genre", "genres")),
            "release_date": release_date,
            "rating": safe_float(pick_value(row, "rating", "score", "user_score", "critic_score")),
            "runtime": None,
            "description": normalize_text(pick_value(row, "summary", "description")),
            "year": safe_int(pick_value(row, "release year", "year")) or safe_int(release_date),
            "director": None,
            "cast_members": None,
            "source": "games_csv",
            "external_id": normalize_text(pick_value(row, "id", "game_id")),
        }

        insert_item(cursor, item)
        inserted += 1

    return inserted


def main():
    connection = None

    try:
        connection, cursor = get_connection()

        tmdb_count = load_tmdb_csv(cursor)
        game_count = load_games_csv(cursor)

        connection.commit()

        print(f"Loaded {tmdb_count} TMDB items.")
        print(f"Loaded {game_count} game items.")
        print(f"Total loaded: {tmdb_count + game_count}")

    except Exception as error:
        if connection:
            connection.rollback()
        print(f"Data loading failed: {error}")

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()