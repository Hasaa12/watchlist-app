#Menu Graphic
def print_menu(title, options):
    print("\n" + "=" * 40)
    print(f" {title} ".center(40, "="))
    print("=" * 40)

    for index, option in enumerate(options, 1):
        print(f"  {index}) {option}")

    print("-" * 40)

#Gets a number and prevents crashes
def get_user_choice(max_option):
    while True:
        try:
            choice = int(input("Enter your choice: "))
            if 1 <= choice <= max_option:
                return choice
            else:
                print(f"Please enter a number between 1 and {max_option}.")
        except ValueError:
            print("Invalid input. Please type a number.")

    #Simple Yes/No confirmation prompt
def confirm_action(prompt_text):
    while True:
        answer = input(f"{prompt_text} (y/n): ").strip().lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print("Please enter 'y' for Yes or 'n' for No.")


def mark_complete(item_title, ratings_manager, user_id):
    """
    The flow for when a user finishes a movie/game.
    It immediately prompts them to leave a review
    """
    print("\n" + "*" * 40)
    print(f"🎉 Congratulations on finishing '{item_title}'!")
    print("*" * 40)

    wants_to_rate = confirm_action("Would you like to rate and review it now?")

    #Validate their rating
    if wants_to_rate:
        while True:
            try:
                rating = int(input("Enter your rating (1-10): "))
                if 1 <= rating <= 10:
                    break
                else:
                    print("Rating must be between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")

        #Get the text review
        review_text = input("Write your review or press Enter to leave blank: ")

        #Save it to the database
        ratings_manager.add_review(user_id, item_title, rating, review_text)
    else:
        print("No problem, you can always add a review later from the Ratings Menu.")