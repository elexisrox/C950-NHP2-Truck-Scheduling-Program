import csv
from HashTable import HashTable
from Package import Package


# Extracts the CSV Data for all packages.
# Space-time complexity: O(N)
class PackageCSVExtractor:
    # Initializer
    def __init__(self, file_path):
        self.file_path = file_path
        self.pkg_hash_table = HashTable()

    # Method to extract the CSV data.
    # Space-time complexity: O(N)
    def extract_pkg_csv(self):
        # Set opening file conditions.
        with open(self.file_path, encoding='utf-8-sig') as file:
            csv_extractor = csv.reader(file)
            # Process each row accordingly.
            for row in csv_extractor:
                package = self.pkg_process_row(row)
                # Set the key and value.
                hash_key = package.get_package_id()
                hash_value = package
                # Insert the entry into the hash table.
                self.pkg_hash_table.insert(hash_key, hash_value)
        # Return the hash table.
        return self.pkg_hash_table

    # Method to retrieve the hash table.
    # Space-time complexity: O(1)
    def get_pkg_hash_table(self):
        return self.pkg_hash_table.get_hash_table()

    # Method to determine how a row in the CSV should be interpreted by the program.
    # NOTE: 'dest' stands for 'destination.'
    # Space-time complexity: O(1)
    def pkg_process_row(self, row):
        # Each column represents a different piece of information.
        pkg_id = row[0]
        dest_st_address = row[1]
        dest_city = row[2]
        dest_state = row[3]
        dest_zip = row[4]
        deadline = row[5]
        pkg_weight = row[6]
        notes = row[7]

        # Store the data as a package.
        package_data = Package(pkg_id, dest_st_address, dest_city, dest_state, dest_zip, deadline, pkg_weight, notes)
        # Analyze the notes column for each package.
        package_data = self.parse_notes(notes, package_data)

        return package_data

    # Parses the strings provided in the "notes" section for Package Data.
    # For the purposes of this assignment and because of the provided data, it is assumed that the package conditions
    # specified by the "notes" can only list one condition per package.
    # Space-time complexity: O(N)
    @staticmethod
    def parse_notes(notes, package):
        # Interpretation of notes for delayed packages.
        # Space-time complexity: O(1)
        if 'Delayed on' in notes:
            # It can be assumed that the time of the flight to the depot is known to be 9:05:00.
            delayed_time = "09:05:00"
            package.set_delayed_until(delayed_time)

        # Interpretation of notes for packages restricted to specific trucks.
        # Space-time complexity: O(1)
        if 'Can only be on' in notes:
            # Convert string to all lowercase to avoid errors. Split the string after truck to isolate the truck number.
            split_text = notes.lower().split('truck', 1)

            truck_number = split_text[1].strip()

            # Set the package's truck requirement.
            package.set_required_truck(truck_number)

        # Interpretation of notes for addresses that need to be updated.
        # Hard-coded due to format of CSV data provided by WGU.
        # Space-time complexity: O(1)
        if 'Wrong address' in notes:
            # TODO may need to reformat time
            package.set_delayed_until('10:20:00')
            package.set_dest_st_address(f'Incorrect address. Will be updated at {package.delayed_until}')
            package.set_destination_city('City: N/A')
            package.set_destination_state('State: N/A')
            package.set_destination_zipcode('Zip: N/A')
            package.set_package_flagged(True)

        # Interpretation of notes for packages that must be delivered together.
        # Space-time complexity: O(N)
        if 'Must be delivered' in notes:
            split_text = notes.lower().split('with', 1)
            package_numbers = split_text[1].strip().split(',')

            # Store which packages should be delivered together using the package's deliver_with property.
            # Space-time complexity: O(N)
            req_packages = []
            for package_number in package_numbers:
                package_number = package_number.strip()
                req_packages.append(package_number)

            package.set_deliver_with(req_packages)

        return package
