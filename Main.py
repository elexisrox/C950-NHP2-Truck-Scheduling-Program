# Student: Elexis Rox, ID#001478546
# Project NHP2 Task 1 for C950, WGU

from UserMenu import *

# Space-time complexity: O(N^2) for the overall program
class Main:
    # Exit program flag to allow the user to exit
    exit_program = False

    # Create an instance of the Dispatch class.
    # Space-time complexity: O(N^2)
    dispatch = Dispatch()
    # Use the Dispatch class to load the trucks.
    dispatch.load_trucks()

    # This loop begins the main menu.
    # Space-time complexity: O(N)
    while not exit_program:
        # UserMenu initiates loading packages and handles user input.
        # Space-time complexity: O(N^2)
        result = UserMenu.begin_main_menu(dispatch)

        # If option 1 is selected in the UserMenu, return search results.
        # Otherwise, option 2 is handled within UserMenu.
        # Space-time complexity: O(N) where N is the number of packages.
        if result is not None:
            package, user_time_str, dispatch = result
            user_time_input = dispatch.read_time(user_time_str)

            # Search results are retrieved based on the input from the user.
            search_results = dispatch.print_full_package_info(package, user_time_input)

        # After the main menu has been completed, the user will be prompted to either restart the menu or exit.
        # Space-time complexity: 0(1)
        while True:
            # Offer user the choice to exit or begin menu again once they have exhausted their menu choice.
            exit_choice = UserMenu.offer_exit_choice()
            if exit_choice == 'exit':
                exit_program = True
                break
            elif exit_choice == 'continue':
                exit_program = False
                break
