from datetime import time, date
from Package import *


# Contains all data relevant to the trucks.
# Space-time complexity: O(1)
class Truck:
    def __init__(self, truck_number):
        self.truck_number = truck_number

        self.package_list = []
        self.route_addresses = []
        self.route = []
        self.starting_location = '4001 South 700 E'
        self.current_location = '4001 South 700 E'
        self.loaded_addresses_by_truck = {}
        self.total_distance = 0
        self.capacity = 16
        self.speed = 18
        # Set the standard departure time for the first two trucks (8:00 AM).
        self.start_time = datetime(year=1, month=1, day=1, hour=8, minute=0, second=0)
        # Track the current time of the truck along its route.
        self.current_time = self.start_time
        # This is the time the truck returns to the HUB after finishing its route.
        self.return_time = None
        # Used to store the correlating location and time at each stop as the truck travels its route.
        self.truck_location_log = {}

    # Method to determine if the truck is full by comparing the length of its package list to its capacity.
    # Space-time complexity: O(1)
    def truck_is_full(self):
        return bool(len(self.package_list) >= self.capacity)

    # Getters for truck info
    # Space-time complexity: O(1) unless otherwise stated
    def get_truck_number(self):
        return self.truck_number

    def route_addresses(self):
        return self.route_addresses

    def route(self):
        return self.route

    def get_starting_location(self):
        return self.starting_location

    def get_current_location(self):
        return self.current_location

    def get_total_distance(self):
        return self.total_distance

    def get_capacity(self):
        return self.capacity

    def get_speed(self):
        return self.speed

    def get_package_list(self):
        return self.package_list

    # Space-time complexity: O(N), but loaded addresses cannot contain more than 16 entries, so it could be considered
    # O(1) as well.
    def get_loaded_addresses_by_truck(self):
        # Create an empty dictionary to store loaded addresses with their associated truck number.
        loaded_pkg_list_addresses = {}

        package_list = self.get_package_list()
        # Iterate through the truck's package list
        for package in package_list:
            # Retrieve the truck number
            truck_number = str(package.get_current_truck())
            pkg_address = package.get_dest_st_address()
            # Store the address and the truck number
            loaded_pkg_list_addresses[pkg_address] = truck_number

        return loaded_pkg_list_addresses

    def get_start_time(self):
        return self.start_time

    def get_current_time(self):
        return self.current_time

    def get_return_time(self):
        return self.return_time

    # Setters for truck information
    # Space-time complexity: O(1) for all setters
    def set_truck_number(self, number):
        self.truck_number = number

    def set_route_addresses(self, route_addresses):
        self.route_addresses = route_addresses

    def set_route(self, route):
        self.route = route

    def set_current_location(self, location):
        self.current_location = location

    def set_total_distance(self, distance):
        self.total_distance = distance

    def set_capacity(self, capacity):
        self.capacity = capacity

    def set_speed(self, speed):
        self.speed = speed

    # Set the start time and make sure it is a datetime object.
    def set_start_time(self, start_time):
        if isinstance(start_time, time):
            # Convert the time to a datetime with a default date.
            self.start_time = datetime.combine(date.min, start_time)
        elif isinstance(start_time, datetime):
            # If datetime is given, set the start_time directly.
            self.start_time = start_time
        else:
            raise ValueError("Invalid input. Please provide a time or datetime object.")

    def set_current_time(self, current_time):
        self.current_time = current_time

    def set_return_time(self, return_time):
        self.return_time = return_time

    # Checks if a package is currently on a specified truck.
    # Space-time complexity: O(1) because the number of packages on a truck is constant.
    def is_package_on_truck(self, package_id):
        for package in self.package_list:
            if package.get_package_id() == package_id:
                return True
        return False

    # Adds a package to a specified truck. Called by add_package_to_truck in Dispatch class.
    # Space-time complexity: O(1)
    def add_package(self, package):
        # Check if the truck is full first.
        if self.truck_is_full():
            return False
        # If the truck is not full, load the package.
        self.package_list.append(package)
        package.set_current_truck(self.truck_number)
        return True

    # Removes a package from a specified truck. Called by remove_package_from_truck in Dispatch class.
    # Space-time complexity: O(1)
    def remove_package(self, package):
        self.package_list.remove(package)
        package.set_current_truck(None)

    # Returns last package in the truck route.
    # Space-time complexity: O(1)
    def get_last_package_in_route(self):
        # Retrieve the last package in the route and return it.
        if len(self.route_addresses):
            package_stop = self.route_addresses[-1]
            package_id = package_stop[0]
            return package_id
        # Error catch if route is not built yet.
        else:
            print('ERROR: Could not find last package in route.')
            return None

    # Prints package list on a truck, initially created for testing purposes.
    # Space-time complexity: O(1) because the max number of packages on each truck is consistent.
    def print_package_list(self, should_sort=True):
        package_id_list = []
        print(f'{len(self.package_list)} ' + 'packages in Truck ' + f'{self.truck_number}')
        for package in self.package_list:
            package_id = package.get_package_id()
            package_id_list.append(package_id)
        if should_sort:
            package_id_list.sort(key=int)
        print('Packages: ' + ', '.join(map(str, package_id_list)))
