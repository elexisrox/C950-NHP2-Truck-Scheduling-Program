from PackageCSVExtractor import *


# Provides data for PackageCSVExtractor class.
# Space-time complexity: O(N)
class Schedule:
    # Initializer
    def __init__(self, address_key, st_address):
        self.st_address = address_key
        self.address_key = st_address

        self.address_data = None
        self.distance_data = None

    # Loads the schedule data based on WGU provided data.
    # Space-time complexity: O(N)
    def load_schedule_data(self):
        with open('WGUPS_Address_Data.csv', encoding='utf-8-sig') as address_csv_file:
            read_addr_csv = csv.reader(address_csv_file, delimiter=',')
            self.address_data = list(read_addr_csv)

        with open('WGUPS_Distance_Data.csv', encoding='utf-8-sig') as distance_csv_file:
            read_distance_csv = csv.reader(distance_csv_file, delimiter=',')
            self.distance_data = list(read_distance_csv)






