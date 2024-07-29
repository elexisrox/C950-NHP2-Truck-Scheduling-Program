import csv
from HashTable import *


# Contains methods required to extract, parse, and interpret distance data
# Space-time complexity: O(N^2)
class Distance:
    # Initialize class
    def __init__(self, addresses_csv, distances_csv):
        self.table = HashTable()
        self.addresses_csv = addresses_csv
        self.distances_csv = distances_csv
        self.address_list = self.parse_addresses_csv()
        self.parse_distances_csv()

    # Method to parse the address data in CSV format, associating each address with a numeric key.
    # Space-time complexity: O(N)
    def parse_addresses_csv(self):
        address_array = []
        with open(self.addresses_csv, encoding='utf-8-sig') as file:
            csv_extractor = csv.reader(file)
            for row in csv_extractor:
                address_street = row[1]
                address_array.append(address_street)

        return address_array

    # Method to parse the distance data in CSV format and populate a hash table.
    # Each address's key correlates to a numerically equivalent row/column.
    # Space-time complexity: O(N^2)
    def parse_distances_csv(self):
        with open(self.distances_csv, encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            rows = list(reader)

            addresses = self.address_list

            for i in range(0, len(rows)):
                current_address = addresses[i]
                row_distances = []

                for j in range(0, len(rows[i])):
                    # Check the intersection of the row/column that correlates with the 2 addresses given.
                    if rows[i][j] != '':
                        distance = float(rows[i][j])
                    # If the targeted cell is blank, reverse the values. This is due to the formatting of the CSV file.
                    else:
                        distance = float(rows[j][i])
                    row_distances.append(distance)
                # Insert row distances into hash table using address as the key
                self.table.insert(current_address, row_distances)

    # Method to look up the distance between two addresses
    # Space-time complexity: O(N)
    def lookup_distance(self, starting_address, destination_address):
        try:
            destination_address_index = self.address_list.index(destination_address)
            starting_address_row = self.table.search(starting_address)

            # Returns a default distance if address is unrecognized.
            if starting_address_row is None:
                print('ERROR: There are errors within the address data.')
                return float('inf')
            # Returns the distance associated with the two addresses.
            else:
                distance = starting_address_row[destination_address_index]
                return distance

        # Included redundant ValueError in case previous error evasion attempt is unsuccessful.
        # Returns a default distance if address is unrecognized.
        except ValueError:
            print('ValueError: Invalid data')
            return float('inf')

    # Method to retrieve a distance value between two addresses, specifically from the WGUPS_Address_Data and
    # WGUPS_Distance_Data CSV files.
    # Space-time complexity: O(N)
    @staticmethod
    def retrieve_distance_wgups(address1, address2):
        distance_lookup = Distance('./WGUPS_Address_Data.csv', './WGUPS_Distance_Data.csv')
        return distance_lookup.lookup_distance(address1, address2)

    # Method to retrieve the address that is closest to another address, aka its nearest neighbor.
    # Space-time complexity: O(N)
    @staticmethod
    def nearest_neighbor(address, remaining_addresses):
        # Initialize minimum distance with a default large float.
        min_distance = float('inf')
        # Set the nearest address to the HUB.
        nearest_address = '4001 South 700 E'

        # Iterate through the given addresses.
        try:
            for possible_nearest_address in remaining_addresses:
                distance = Distance.retrieve_distance_wgups(address, possible_nearest_address)
                # If the distance between the two points is less than the current min_distance value, that address
                # becomes the nearest_address.
                if 0 < distance < min_distance:
                    min_distance = distance
                    nearest_address = possible_nearest_address
        except ValueError:
            print('ERROR: A ValueError occurred when determining the nearest neighbor.')

        return nearest_address
