import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    tmdb["rating"] = None  # TMDB rating col is age rating (PG-13 etc), not numeric
    tmdb = tmdb[["title", "type", "genre", "rating", "year"]].copy()

    games = pd.read_csv(games_path)
    games["type"] = "game"
    games = games.rename(columns={"Title": "title", "Genres": "genre", "Rating": "rating"})
    games["year"] = None
    games = games[["title", "type", "genre", "rating", "year"]].copy()

    df = pd.concat([tmdb, games], ignore_index=True)
    return df


def load_db_data(user_id):
    connection = None
    try:
        connection, cursor = get_connection()
        cursor.execute(
            """
            SELECT ei.title, ei.type, ei.genre, ei.rating, ei.year, ul.status
            FROM user_lists ul
            JOIN entertainment_items ei ON ul.item_id = ei.item_id
            WHERE ul.user_id = ?
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        data = [dict(row) for row in rows]
        return pd.DataFrame(data)
    except Exception as e:
        print(f"error loading from db: {e}")
        return None
    finally:
        if connection:
            connection.close()


def total_by_type(df):
    counts = df["type"].value_counts().reset_index()
    counts.columns = ["Type", "Count"]
    print("\n--- Items by Type ---")
    print(tabulate(counts, headers="keys", tablefmt="pretty", showindex=False))


def completion_rate(df):
    if "status" not in df.columns:
        print("no status column available")
        return
    total = len(df)
    completed = len(df[df["status"] == "completed"])
    rate = round((completed / total) * 100, 1) if total > 0 else 0
    print(f"\n--- Completion Rate ---")
    print(f"Completed: {completed}/{total} ({rate}%)")


def avg_rating_by_genre(df):
    df2 = df.dropna(subset=["genre", "rating"]).copy()
    df2["genre"] = df2["genre"].astype(str).str.replace(r"[\[\]']", "", regex=True).str.split(",")
    df2 = df2.explode("genre")
    df2["genre"] = df2["genre"].str.strip()
    df2 = df2[df2["genre"] != ""]

    ratings = df2["rating"].astype(float)
    avg = np.mean(ratings.values)
    print(f"\nOverall avg rating: {round(avg, 2)}")

    genre_avg = df2.groupby("genre")["rating"].mean().reset_index()
    genre_avg.columns = ["Genre", "Avg Rating"]
    genre_avg["Avg Rating"] = genre_avg["Avg Rating"].round(2)
    genre_avg = genre_avg.sort_values("Avg Rating", ascending=False).head(10)

    print("\n--- Top 10 Genres by Avg Rating ---")
    print(tabulate(genre_avg, headers="keys", tablefmt="pretty", showindex=False))


def genre_distribution(df):
    df2 = df.dropna(subset=["genre"]).copy()
    df2["genre"] = df2["genre"].astype(str).str.replace(r"[\[\]']", "", regex=True).str.split(",")
    df2 = df2.explode("genre")
    df2["genre"] = df2["genre"].str.strip()
    df2 = df2[df2["genre"] != ""]

    dist = df2["genre"].value_counts().reset_index().head(10)
    dist.columns = ["Genre", "Count"]

    print("\n--- Genre Distribution (Top 10) ---")
    print(tabulate(dist, headers="keys", tablefmt="pretty", showindex=False))


def plot_genre_bar_chart(df):
    df2 = df.dropna(subset=["genre"]).copy()
    df2["genre"] = df2["genre"].astype(str).str.replace(r"[\[\]']", "", regex=True).str.split(",")
    df2 = df2.explode("genre")
    df2["genre"] = df2["genre"].str.strip()
    df2 = df2[df2["genre"] != ""]

    top_genres = df2["genre"].value_counts().head(8)

    plt.figure(figsize=(10, 5))
    plt.bar(top_genres.index, top_genres.values, color="steelblue")
    plt.title("Top 8 Genres")
    plt.xlabel("Genre")
    plt.ylabel("Count")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("genre_bar.png")
    plt.show()
    print("saved genre_bar.png")


def plot_completion_pie(df):
    if "status" not in df.columns:
        print("no status data available")
        return
    status_counts = df["status"].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(status_counts.values, labels=status_counts.index, autopct="%1.1f%%", startangle=140)
    plt.title("Watchlist Status Breakdown")
    plt.tight_layout()
    plt.savefig("completion_pie.png")
    plt.show()
    print("saved completion_pie.png")


def plot_ratings_histogram(df):
    ratings = df["rating"].dropna().astype(float)
    p25 = np.percentile(ratings, 25)
    p75 = np.percentile(ratings, 75)

    plt.figure(figsize=(8, 5))
    plt.hist(ratings, bins=20, color="coral", edgecolor="black")
    plt.axvline(np.mean(ratings), color="blue", linestyle="--", label=f"mean: {round(np.mean(ratings), 2)}")
    plt.axvline(p25, color="green", linestyle=":", label=f"25th pct: {round(p25, 2)}")
    plt.axvline(p75, color="purple", linestyle=":", label=f"75th pct: {round(p75, 2)}")
    plt.title("Ratings Distribution")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig("ratings_hist.png")
    plt.show()
    print("saved ratings_hist.png")


def run_all_stats(user_id=None):
    if user_id:
        df = load_db_data(user_id)
        if df is None:
            print("no watchlist data found, loading from csv instead")
            df = load_csv_data()
    else:
        df = load_csv_data()

    total_by_type(df)
    avg_rating_by_genre(df)
    genre_distribution(df)

    if user_id and "status" in df.columns:
        completion_rate(df)

    plot_genre_bar_chart(df)
    plot_ratings_histogram(df)

    if user_id and "status" in df.columns:
        plot_completion_pie(df)


if __name__ == "__main__":
    run_all_stats()
