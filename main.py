from menu_helpers import print_menu, get_user_choice, confirm_action, mark_complete
from ratings_manager import RatingsManager
from user import User
from watchlist_manager import WatchlistManager
from stats_service import run_all_stats
from recommendation_engine import get_recommendations, load_csv_data
#from favorites_manager import FavoritesManager

def main():
    print("\n" + "=" * 50)
    print("🎬🎮 WELCOME TO THE ENTERTAINMENT TRACKER 🎮🎬".center(50))
    print("=" * 50)

    #--- INITIALIZATION ---
    #Boot up all the managers
    ratings_manager = RatingsManager()
    watchlist_manager = WatchlistManager()

    #LOGIN
    logged_in = None

    while logged_in is None:
        print("\n--- Please Log In or Register ---")
        print("1) Login")
        print("2) Register")
        print("3) Quit")

        auth_choice = get_user_choice(max_option = 3)

        if auth_choice == 1:
            username = input("Enter username: ")
            password = input("Enter password: ")

            #print("Mock Login Successful!")
            #Call login
            logged_in = User.login(username, password)

        elif auth_choice == 2:
            username = input("Enter username: ")
            email = input("Enter email: ")
            password = input("Enter password: ")
            #Call resister
            logged_in = User.register(username, email, password)
        else:
            print("Goodbye!")
            return  #Exits the entire app

    #THE MAIN MENU LOOP
    #The user stays in this loop until they choose to log out
    print(f"\n Welcome {logged_in.username}!")
    while True:
        menu_options = [
            "📺Watchlist",
            "🔍Search (Movies & Games)",
            "⭐Ratings & Reviews",
            "❤️Favorites",
            "📊Stats",
            "🍿Recommendations",
            "Logout"
        ]

        print_menu("MAIN MENU", menu_options)
        choice = get_user_choice(max_option=7)

        try:
            if choice == 1:
                print("\n--- WATCHLIST ---")
                while True:
                    print_menu("WATCHLIST", [
                        "View My Watchlist",
                        "Update Item Status or Notes",
                        "Mark Item as Completed",
                        "Remove Item from Watchlist",
                        "Back to Main Menu"
                    ])
                    wl_choice = get_user_choice(max_option = 5)

                    if wl_choice == 1:
                        print("\n--- Your Watchlist ---")
                        #Fetch the user item using the ID from the login step
                        items = watchlist_manager.get_all_items(logged_in.user_id)

                        if not items:
                            print("Your watchlist is currently empty!")
                        else:
                            for item in items:
                                print(item.display()) #Call display function

                    elif wl_choice == 2:
                        item_id = input("\nEnter the ID of the item to update: ")
                        print("Valid statuses: plan to watch, watching, completed, dropped")
                        status = input("Enter new status (or press Enter to skip): ").strip()
                        notes = input("Enter new notes (or press Enter to skip): ").strip()

                        #Only pass the values if the user actually typed something
                        watchlist_manager.edit_item(
                            user_id = logged_in.user_id,
                            item_id = item_id,
                            status = status if status else None,
                            notes = notes if notes else None
                        )

                    elif wl_choice == 3:
                        item_id = input("\nEnter the ID of the item you finished: ")
                        #Update database
                        success = watchlist_manager.mark_complete(logged_in.user_id, item_id)

                        if success:
                            #Trigger helper to ask for review
                            mark_complete(item_title = item_id, ratings_manager = ratings_manager,
                                          user_id = logged_in.user_id)

                    elif wl_choice == 4:
                        item_id = input("\nEnter the ID of the item to remove: ")
                        #Ask for confirmation before deleting
                        if confirm_action("Are you sure you want to remove this?"):
                            watchlist_manager.delete_item(logged_in.user_id, item_id)

                    elif wl_choice == 5:
                        print("\nReturning to Main Menu...")
                        break  #Breaks out of the sub-menu loop

            elif choice == 2:
                print("\n---SEARCH MOVIES & GAMES ---")
                query = input("Enter a game or movie: ").strip().lower()

                print(f"\nSearching catalog for '{query}'...")

                # Load dataframe
                df = load_csv_data()

                # Filter and fill NaNs with empty strings so the search doesn't crash
                results = df[df['title'].fillna('').str.lower().str.contains(query)]

                if results.empty:
                    print("No matching items found.")
                else:
                    # Print the top 10 results
                    top_results = results.head(10)
                    for index, row in top_results.iterrows():
                        print(
                            f"[{row['type'].upper()}] {row['title']} | Genre: {row['genre']} | Year: {row['year']}")

            elif choice == 3:
                print("\n--- RATINGS & REVIEWS ---")
                while True:
                    print_menu("RATINGS & REVIEWS", [
                        "View My Reviews",
                        "View Reviews for a Title",
                        "Add a New Review",
                        "Edit an Existing Review",
                        "Back to Main Menu"
                    ])
                    rating_choice = get_user_choice(max_option = 5)

                    if rating_choice == 1:
                        print("\n--- My Reviews ---")
                        # Uses the logged-in user's ID
                        my_reviews = ratings_manager.get_user_reviews(logged_in.user_id)

                        if not my_reviews:
                            print("You haven't written any reviews yet.")
                        else:
                            for review in my_reviews:
                                # Assuming DB columns are: id, user_id, title, rating, text
                                print(f"Review ID: {review[0]} | Title: {review[2]} | Rating: {review[3]}/10")
                                print(f"  └─ '{review[4]}'")

                    elif rating_choice == 2:
                        print("\n--- Search Reviews ---")
                        item_id = int(input("Enter the Item ID: "))
                        title_reviews = ratings_manager.get_reviews_for_item(item_id)

                        if not title_reviews:
                            print(f"No reviews found for '{item_id}'.")
                        else:
                            for review in title_reviews:
                                print(f"User ID: {review[1]} rated it {review[3]}/10")
                                print(f"  └─ '{review[4]}'")

                    elif rating_choice == 3:
                        print("\n--- Add a Review ---")
                        title = input("Enter the title: ").strip()

                        #Validate the rating input so it doesn't crash
                        while True:
                            try:
                                rating = int(input("Enter rating (1-10): "))
                                if 1 <= rating <= 10:
                                    break
                                else:
                                    print(" Rating must be between 1 and 10.")
                            except ValueError:
                                print(" Please enter a valid number.")

                        text = input("Write your review: ").strip()
                            ###
                        ratings_manager.add_review(logged_in.user_id, title, rating, text)

                    elif rating_choice == 4:
                        print("\n--- Edit a Review ---")
                        try:
                            review_id = int(input("Enter the Review ID you want to edit: "))
                        except ValueError:
                            print("️Review ID must be a number. Returning to menu...")
                            continue  # Skips the rest and restarts the sub-menu loop

                        # Validate the new rating
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
                        print("\nReturning to Main Menu...")
                        break

            elif choice == 4:
                print("\n--- ❤️FAVORITES ---")
                while True:
                    print_menu("FAVORITES", [
                        "View My Favorites",
                        "Add an Item to Favorites",
                        "Remove an Item from Favorites",
                        "Back to Main Menu"
                    ])
                    fav_choice = get_user_choice(max_option=4)

                    if fav_choice == 1:
                        print("\n--- My Favorites ---")
                        # TODO: Call code
                        # e.g., favorites_manager.get_user_favorites(logged_in_user.user_id)
                        print("[Integration Pending: Team's favorites list goes here]")

                    elif fav_choice == 2:
                        print("\n--- Add to Favorites ---")
                        item_id = input("Enter the ID of the item to favorite: ")
                        # TODO: Call code
                        # e.g., favorites_manager.add_favorite(logged_in_user.user_id, item_id)
                        print(f"[Integration Pending: Add ID {item_id} to favorites]")

                    elif fav_choice == 3:
                        print("\n--- Remove from Favorites ---")
                        item_id = input("Enter the ID of the item to remove: ")
                        # TODO: Call code
                        print(f"[Integration Pending: Remove ID {item_id} from favorites]")

                    elif fav_choice == 4:
                        print("\nReturning to Main Menu...")
                        break

            elif choice == 5:
                print("\n--- STATS ---")
                print("\n" + "=" * 40)
                print(" YOUR ENTERTAINMENT STATS ".center(40, "="))
                print("=" * 40)

                #Call stats function
                run_all_stats(logged_in.user_id)
                # e.g., stats_manager.display_user_stats(logged_in_user.user_id)
                print("\nCheck your project folder for new stat chart")
                input("\nPress Enter to return to the Main Menu...")

                #Pause the screen so the user can actually read their stats before the menu redraws
                input("\nPress Enter to return to the Main Menu...")

            elif choice == 6:
                print("\n" + "=" * 40)
                print(" RECOMMENDED FOR YOU ".center(40, "="))
                print("=" * 40)

                #Call recommendation function
                get_recommendations(logged_in.user_id)

                #Pause the screen
                input("\nPress Enter to return to the Main Menu...")

            elif choice == 7:
                print("\nLogging out")
                break

        except Exception as e:
            #Wrap all user input in try/except
            print(f"\nError: {e}")
            print("Returning to Main Menu...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        #Catches if the user hits Ctrl+C to forcefully quit
        print("\n\nForce quitting...")