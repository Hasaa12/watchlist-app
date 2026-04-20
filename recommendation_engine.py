import pandas as pd
import numpy as np
from pathlib import Path
from tabulate import tabulate
from db_manager import get_connection

BASE_DIR = Path(__file__).resolve().parent


def load_csv_data():
    tmdb_path = BASE_DIR / "tmdb_movies_tv.csv"
    games_path = BASE_DIR / "games_data.csv"

    tmdb = pd.read_csv(tmdb_path)
    tmdb["type"] = "movie"
    tmdb = tmdb.rename(columns={"Title": "title", "Genre": "genre", "Year": "year"})
    tmdb["rating"] = None
    tmdb = tmdb[["title", "type", "genre", "rating", "year"]].copy()

    games = pd.read_csv(games_path)
    games["type"] = "game"
    games = games.rename(columns={"Title": "title", "Genres": "genre", "Rating": "rating"})
    games["year"] = None
    games = games[["title", "type", "genre", "rating", "year"]].copy()

    df = pd.concat([tmdb, games], ignore_index=True)
    return df


def get_user_completed_items(user_id):
    connection = None
    try:
        connection, cursor = get_connection()
        cursor.execute(
            """
            SELECT ei.title, ei.genre, rr.user_rating
            FROM user_lists ul
            JOIN entertainment_items ei ON ul.item_id = ei.item_id
            LEFT JOIN ratings_reviews rr ON rr.item_id = ei.item_id AND rr.user_id = ul.user_id
            WHERE ul.user_id = ? AND ul.status = 'completed'
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"error getting completed items: {e}")
        return []
    finally:
        if connection:
            connection.close()


def get_user_watchlist_titles(user_id):
    connection = None
    try:
        connection, cursor = get_connection()
        cursor.execute(
            """
            SELECT ei.title
            FROM user_lists ul
            JOIN entertainment_items ei ON ul.item_id = ei.item_id
            WHERE ul.user_id = ?
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        return [row["title"].lower() for row in rows]
    except Exception as e:
        print(f"error getting watchlist titles: {e}")
        return []
    finally:
        if connection:
            connection.close()


def extract_top_genres(completed_items):
    genre_scores = {}

    for item in completed_items:
        if not item["genre"]:
            continue
        genres_raw = str(item["genre"]).replace("[", "").replace("]", "").replace("'", "")
        genres = [g.strip() for g in genres_raw.split(",") if g.strip()]
        rating = item.get("user_rating") or 3.0

        for genre in genres:
            if genre not in genre_scores:
                genre_scores[genre] = []
            genre_scores[genre].append(float(rating))

    avg_scores = {g: np.mean(scores) for g, scores in genre_scores.items()}
    sorted_genres = sorted(avg_scores, key=avg_scores.get, reverse=True)
    return sorted_genres[:3]


def get_recommendations(user_id=None):
    df = load_csv_data()

    if user_id:
        completed = get_user_completed_items(user_id)
        watchlist_titles = get_user_watchlist_titles(user_id)
    else:
        completed = []
        watchlist_titles = []

    if completed:
        top_genres = extract_top_genres(completed)
        print(f"\nYour top genres: {', '.join(top_genres)}")

        df2 = df.dropna(subset=["genre"]).copy()
        df2["genre_clean"] = df2["genre"].astype(str).str.replace(r"[\[\]']", "", regex=True)

        def matches_genre(genre_str):
            for g in top_genres:
                if g.lower() in genre_str.lower():
                    return True
            return False

        filtered = df2[df2["genre_clean"].apply(matches_genre)].copy()
        filtered = filtered[~filtered["title"].str.lower().isin(watchlist_titles)]
    else:
        print("\nno completed items found, showing top rated items overall")
        filtered = df.dropna(subset=["rating"]).copy()

    filtered["rating"] = pd.to_numeric(filtered["rating"], errors="coerce")
    filtered = filtered.dropna(subset=["rating"])
    filtered = filtered.sort_values("rating", ascending=False)
    filtered = filtered.drop_duplicates(subset=["title"])
    top10 = filtered.head(10)[["title", "type", "genre", "rating"]].copy()
    top10 = top10.rename(columns={"title": "Title", "type": "Type", "genre": "Genre", "rating": "Rating"})
    top10["Genre"] = top10["Genre"].astype(str).str.replace(r"[\[\]']", "", regex=True).str[:30]
    top10["#"] = range(1, len(top10) + 1)
    top10 = top10[["#", "Title", "Type", "Genre", "Rating"]]

    print("\n--- Top 10 Recommendations ---")
    print(tabulate(top10, headers="keys", tablefmt="pretty", showindex=False))
    return top10


if __name__ == "__main__":
    get_recommendations()
