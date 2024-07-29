from Dispatch import *


# Contains the main code for the User Interface. Calls Dispatch to load the trucks.
# Space-time complexity: O(N^2), due to printing all the package details from the Dispatch class.
class UserMenu:
    # Method below requests user input for time request.
    # Since this request is made for both menu options 1 and 2, this method reduces redundancy.
    # Space-time complexity: O(1)
    @staticmethod
    def ask_time_input():
        package_time = input('Please enter the desired time in HH:MM:SS format: ')
        result = Dispatch.read_time(package_time)
        return result

    # Method to begin the main menu
    # Space-time complexity: O(N^2)
    @staticmethod
    def begin_main_menu(dispatch):
        # Used for formatting purposes within the user menu.
        indent = '\t\t '

        # Retrieve the hash table, so it can be used for user search.
        package_hash_table = dispatch.get_package_hash_table()

        # Begin User Menu
        while True:
            # Print greeting, total miles, and menu options.
            # Space-time complexity: O(N)
            print(f"""
                Hello! Welcome to the WGUPS Package Tracking System.
                Current route was completed in {dispatch.get_total_distance():.2f} miles.
                Please review the following options:          
    
                1. Lookup the status of an individual package
                2. View delivery status of all packages at a given time
                
                Type '1' or '2' to select your desired option: 
                """)

            menu_options = input()
            # If user selects option 1
            if menu_options == '1':
                try:
                    # Prompt the user for Package ID.
                    package_number = input('\nPlease enter the package number you would like to look up: ')
                    # Catch errors related to incorrect input format.
                    if not package_number.isdigit():
                        print(indent + 'Incorrect format. Please enter a number.')
                    # Lookup the package in the hash table.
                    # Space-time complexity: O(N)
                    package = package_hash_table.search(f'{package_number}')
                    # Print an error if the user input number could not be found in the table.
                    if package is None:
                        print(indent + 'Package not found. Please try again.')
                    # If user input is valid and the package is found, lookup the package
                    # based on package id and user input time.
                    else:
                        # Ask user for time input.
                        user_time_input = UserMenu.ask_time_input()
                        # Return the result that will be printed in Main.
                        return package, user_time_input, dispatch

                except ValueError:
                    print('Invalid entry. Please try again.')

            # If user selects option 2
            elif menu_options == '2':
                try:
                    # Prompt the user for time input.
                    user_time_input = UserMenu.ask_time_input()
                    # Call dispatch to print all package details.
                    # Space-time complexity: O(N^2)
                    dispatch.print_all_packages_details(user_time_input)
                    return None

                except ValueError:
                    print('Invalid entry. Please try again.')

            elif menu_options == 'exit':
                exit()
            else:
                print('Invalid entry. Please try again.')
                return None

    # Called by Main to offer the user the option to exit or begin the menu again.
    # Space-time complexity: O(1)
    @staticmethod
    def offer_exit_choice():
        while True:
            # Display a prompt for the user to exit or continue.
            user_input = input("\nPress the Enter key to continue to the main menu, or type 'exit' to exit.\n")

            # If user presses "Enter" key, the main menu will print and start the loop again.
            if user_input == "":
                print("Continuing...")
                return 'continue'

            # If user types "exit", the process will end, and the loop will be completed.
            elif user_input.lower() == "exit":
                print("Exiting...")
                return 'exit'

            # If user provides invalid input, the error message below will print.
            # The loop will return to the point where they must press Enter or type "exit" to continue.
            else:
                print("Invalid input. Please try again.")
