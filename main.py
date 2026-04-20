from menu_helpers import print_menu, get_user_choice, confirm_action, mark_complete
from ratings_manager import RatingsManager
from favorites_manager import FavoritesManager
from user import User
from watchlist_manager import WatchlistManager
from stats_service import run_all_stats
from recommendation_engine import get_recommendations, load_csv_data


def main():
    print("\n" + "=" * 50)
    print("WELCOME TO THE ENTERTAINMENT TRACKER".center(50))
    print("=" * 50)

    ratings_manager = RatingsManager()
    watchlist_manager = WatchlistManager()
    favorites_manager = FavoritesManager()

    logged_in = None

    while logged_in is None:
        print("\n--- Please Log In or Register ---")
        print("1) Login")
        print("2) Register")
        print("3) Quit")

        auth_choice = get_user_choice(max_option=3)

        if auth_choice == 1:
            username = input("Enter username: ")
            password = input("Enter password: ")
            logged_in = User.login(username, password)

        elif auth_choice == 2:
            username = input("Enter username: ")
            email = input("Enter email: ")
            password = input("Enter password: ")
            logged_in = User.register(username, email, password)

        else:
            print("Goodbye!")
            return

    print(f"\nWelcome {logged_in.username}!")

    while True:
        menu_options = [
            "Watchlist",
            "Search (Movies & Games)",
            "Ratings & Reviews",
            "Favorites",
            "Stats",
            "Recommendations",
            "Logout"
        ]

        print_menu("MAIN MENU", menu_options)
        choice = get_user_choice(max_option=7)

        try:
            if choice == 1:
                while True:
                    print_menu("WATCHLIST", [
                        "View My Watchlist",
                        "Update Item Status or Notes",
                        "Mark Item as Completed",
                        "Remove Item from Watchlist",
                        "Back to Main Menu"
                    ])
                    wl_choice = get_user_choice(max_option=5)

                    if wl_choice == 1:
                        items = watchlist_manager.get_all_items(logged_in.user_id)
                        if not items:
                            print("Your watchlist is empty!")
                        else:
                            for item in items:
                                print(item.display())

                    elif wl_choice == 2:
                        item_id = input("\nEnter the ID of the item to update: ")
                        print("Valid statuses: plan to watch, watching, completed, dropped")
                        status = input("Enter new status (or press Enter to skip): ").strip()
                        notes = input("Enter new notes (or press Enter to skip): ").strip()
                        watchlist_manager.edit_item(
                            user_id=logged_in.user_id,
                            item_id=item_id,
                            status=status if status else None,
                            notes=notes if notes else None
                        )

                    elif wl_choice == 3:
                        item_id = input("\nEnter the ID of the item you finished: ")
                        success = watchlist_manager.mark_complete(logged_in.user_id, item_id)
                        if success:
                            mark_complete(item_title=item_id, ratings_manager=ratings_manager,
                                          user_id=logged_in.user_id)

                    elif wl_choice == 4:
                        item_id = input("\nEnter the ID of the item to remove: ")
                        if confirm_action("Are you sure you want to remove this?"):
                            watchlist_manager.delete_item(logged_in.user_id, item_id)

                    elif wl_choice == 5:
                        break

            elif choice == 2:
                query = input("\nSearch for a movie or game: ").strip().lower()
                print(f"\nSearching for '{query}'...")

                df = load_csv_data()
                results = df[df['title'].fillna('').str.lower().str.contains(query)]

                if results.empty:
                    print("No matching items found.")
                else:
                    top_results = results.head(10)
                    for index, row in top_results.iterrows():
                        print(f"[{row['type'].upper()}] {row['title']} | Genre: {row['genre']} | Year: {row['year']}")

            elif choice == 3:
                while True:
                    print_menu("RATINGS & REVIEWS", [
                        "View My Reviews",
                        "View Reviews for a Title",
                        "Add a New Review",
                        "Edit an Existing Review",
                        "Back to Main Menu"
                    ])
                    rating_choice = get_user_choice(max_option=5)

                    if rating_choice == 1:
                        my_reviews = ratings_manager.get_user_reviews(logged_in.user_id)
                        if not my_reviews:
                            print("You haven't written any reviews yet.")
                        else:
                            for review in my_reviews:
                                print(f"Review ID: {review[0]} | Title: {review[2]} | Rating: {review[3]}/10")
                                print(f"  '{review[4]}'")

                    elif rating_choice == 2:
                        item_id = int(input("Enter the Item ID: "))
                        title_reviews = ratings_manager.get_reviews_for_item(item_id)
                        if not title_reviews:
                            print("No reviews found.")
                        else:
                            for review in title_reviews:
                                print(f"User ID: {review[1]} rated it {review[3]}/10")
                                print(f"  '{review[4]}'")

                    elif rating_choice == 3:
                        title = input("Enter the title: ").strip()
                        while True:
                            try:
                                rating = int(input("Enter rating (1-10): "))
                                if 1 <= rating <= 10:
                                    break
                                else:
                                    print("Rating must be between 1 and 10.")
                            except ValueError:
                                print("Please enter a valid number.")
                        text = input("Write your review: ").strip()
                        ratings_manager.add_review(logged_in.user_id, title, rating, text)

                    elif rating_choice == 4:
                        try:
                            review_id = int(input("Enter the Review ID to edit: "))
                        except ValueError:
                            print("Review ID must be a number.")
                            continue
                        while True:
                            try:
                                new_rating = int(input("Enter new rating (1-10): "))
                                if 1 <= new_rating <= 10:
                                    break
                                else:
                                    print("Rating must be between 1 and 10.")
                            except ValueError:
                                print("Please enter a valid number.")
                        new_text = input("Enter new review text: ").strip()
                        ratings_manager.edit_review(review_id, new_rating, new_text)

                    elif rating_choice == 5:
                        break

            elif choice == 4:
                while True:
                    print_menu("FAVORITES", [
                        "View My Favorites",
                        "Add an Item to Favorites",
                        "Remove an Item from Favorites",
                        "Back to Main Menu"
                    ])
                    fav_choice = get_user_choice(max_option=4)

                    if fav_choice == 1:
                        favs = favorites_manager.get_user_favorites(logged_in.user_id)
                        if not favs:
                            print("You have no favorites yet.")
                        else:
                            for fav in favs:
                                print(f"[ID: {fav['item_id']}] {fav['title']} ({fav['type']}) | Genre: {fav['genre']}")

                    elif fav_choice == 2:
                        item_id = input("Enter the Item ID to favorite: ").strip()
                        try:
                            favorites_manager.add_favorite(logged_in.user_id, int(item_id))
                        except ValueError:
                            print("Please enter a valid item ID number.")

                    elif fav_choice == 3:
                        item_id = input("Enter the Item ID to remove: ").strip()
                        try:
                            if confirm_action("Remove from favorites?"):
                                favorites_manager.remove_favorite(logged_in.user_id, int(item_id))
                        except ValueError:
                            print("Please enter a valid item ID number.")

                    elif fav_choice == 4:
                        break

            elif choice == 5:
                print("\n" + "=" * 40)
                print(" YOUR ENTERTAINMENT STATS ".center(40, "="))
                print("=" * 40)
                run_all_stats(logged_in.user_id)
                print("\nCheck your project folder for saved chart images.")
                input("\nPress Enter to return to the Main Menu...")

            elif choice == 6:
                print("\n" + "=" * 40)
                print(" RECOMMENDED FOR YOU ".center(40, "="))
                print("=" * 40)
                get_recommendations(logged_in.user_id)
                input("\nPress Enter to return to the Main Menu...")

            elif choice == 7:
                print("\nLogging out. Goodbye!")
                break

        except Exception as e:
            print(f"\nSomething went wrong: {e}")
            print("Returning to Main Menu...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nForce quitting...")
