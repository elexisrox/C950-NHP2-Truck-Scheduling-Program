from datetime import timedelta
from Truck import *
from Distance import *
from Schedule import *
import copy as cp


# Class that loads the trucks, optimizes the routes, and keeps track of package and truck status.
# Contains the bulk of the program for this project.
# Space-time complexity: O(N^2)
class Dispatch:
    def __init__(self):
        # Master hashtable that should never have packages added or removed
        self._original_package_table = None
        # Copy of the master hashtable to keep track of which packages have not been loaded on to a truck
        self.package_tracking_list = []
        # Set the number of number_of_drivers
        self.number_of_drivers = 2
        # Set up the trucks
        self.first_truck = Truck(1)
        self.second_truck = Truck(2)
        self.third_truck = Truck(3)
        # Additional truck that holds flagged packages
        self.hold_truck = Truck(4)
        # List of trucks that perform deliveries
        self.trucks = [self.first_truck, self.second_truck, self.third_truck]
        # List of trucks that leaves at 8am
        self.early_trucks = self.trucks[:self.number_of_drivers]
        # List that contains all deliverable trucks plus the hold truck
        self.trucks_and_hold = [self.first_truck, self.second_truck, self.third_truck, self.hold_truck]
        # List that holds ids of packages that have the delayed condition
        self.delayed_package_ids = []
        # List that holds ids of all flagged packages
        self.flagged_packages = []
        # List of package ids that remain after our initial loop
        self.remaining_package_ids = []
        # Track the total distance of all 3 trucks
        self.total_distance_of_all_trucks = 0
        # List of all addresses for reference
        self.all_addresses = []
        # Dictionary containing packages that have identical delivery addresses
        self.identical_addresses = {}
        # Dictionary of all delivery addresses currently associated with a truck.
        # This will help optimize the route, so packages with matching addresses can be easily
        # added to the same truck later on.
        self.all_loaded_addresses_by_truck = {}

    # Main method to establish the package hash table.
    # Space-time complexity: O(N)
    def load_hash_tables(self):
        package_extractor = PackageCSVExtractor('./WGUPS_Package_Data.csv')
        package_hash_table = package_extractor.extract_pkg_csv()
        self._original_package_table = package_hash_table

    # Method to retrieve the package hash table.
    # Space-time complexity: O(1)
    def get_package_hash_table(self):
        return self._original_package_table

    # Load Trucks Method
    # This is the main method that should be called after this class is initialized.
    # Space-time complexity: O(N^2)
    def load_trucks(self):
        # Initialize the main hash table.
        # Space-time complexity: O(N)
        self.load_hash_tables()

        # Load all packages onto the trucks.
        # Space-time complexity: O(N)
        self.process_packages()

        # Create the truck routes.
        # Space-time complexity: O(N^2)
        route_works = self.create_all_truck_routes()

        # If the route doesn't meet all the package deadlines, move the packages around.
        if not route_works:
            # Space-time complexity: O(N)
            self.optimize_routes()
            # Recreate the truck routes
            # Space-time complexity: O(N^2)
            self.create_all_truck_routes()

        # Once routes are established, set the total distance of all trucks traveled in dispatch
        # Space-time complexity: O(N)
        self.set_total_distance()

    # Process Packages Method
    # Main method to process all packages during the loading process
    # Space-time complexity: O(N) where N is the number of packages
    def process_packages(self):
        # Loop through the hash table of packages and process each restricted package first.
        # This guarantees that packages with restrictions have spots reserved on the correct trucks.
        # The number of buckets in the hash table does not change, so it can be treated as a constant.
        # Time complexity: O(N), Space complexity: O(1)
        # Individual operations within the method are all O(N)
        for bucket in self._original_package_table.get_hash_table():
            for package_id, package in bucket:
                # First process data about the packages that may be relevant later.
                if package.package_flagged is False:
                    package_address = package.get_dest_st_address()
                    # Populate the address list with all addresses for any non-flagged packages.
                    self.all_addresses.append(package_address)
                    # Store identical address info
                    if package_address in self.identical_addresses:
                        # If the address already exists in the dictionary, that means the package has an identical
                        # delivery match.
                        self.identical_addresses[package_address].append(package_id)
                        identical_pkg_ids = self.identical_addresses[package_address]
                        package.set_has_delivery_identical(True)
                        for identical_pkg_id in identical_pkg_ids:
                            identical_pkg = self.get_package_by_id(identical_pkg_id)
                            # Set the identical package delivery_identical flag
                            identical_pkg.set_has_delivery_identical(True)
                            # Add the packages to each other's identical packages
                            identical_pkg.add_delivery_identical(package)
                            package.add_delivery_identical(identical_pkg)
                    else:
                        self.identical_addresses[package_address] = [package_id]
                # Next, process the package if it is restricted.
                if package.is_package_restricted():
                    self.process_restricted_package(package)
                else:
                    # If the package is unrestricted , add it to the "remaining_package_ids" list.
                    # This list is maintained mostly for debugging and testing purposes.
                    self.remaining_package_ids.append(package.get_package_id())
                    continue

        # Set up all loaded addresses in the class dictionary
        # Space-time complexity: O(N)
        self.set_loaded_addresses_by_truck()

        # Loop through the packages again, this time focusing on the remaining unrestricted packages.
        # Time complexity: O(N), Space complexity: O(1)
        for bucket in self._original_package_table.get_hash_table():
            for package_id, package in bucket:
                if package.is_package_restricted() is False:
                    self.process_unrestricted_package(package)

    # Main method to process restricted packages (packages with special delivery instructions).
    # Space-time complexity: O(1)
    # All components are O(1). A further explanation is provided for the loop of sibling packages below.
    def process_restricted_package(self, package):
        # Retrieve relevant information about the package.
        package_id = package.get_package_id()
        truck_number = self.get_truck_from_package_id(package_id)
        required_truck = package.get_required_truck()
        deliver_with_list = package.get_deliver_with()
        delayed_until = package.get_delayed_until()
        package_flagged = package.get_package_flagged()

        # Case for when package is already on a truck
        # This should not occur, but the error catch is preventative.
        if truck_number is not None:
            print(f'ERROR: {package_id} is already on Truck {truck_number}')
            return

        # Case for when package is flagged
        # Priority lvl 1 - Separate flagged packages and load them into the hold compartment (Truck 4).
        if package_flagged:
            self.add_package_to_truck(4, package)
            # Add the package id to the flagged_packages list
            self.flagged_packages.append(package_id)
            # Since the hold compartment is part of the third truck, its capacity should be updated.
            self.third_truck.set_capacity(self.first_truck.get_capacity()-len(self.hold_truck.get_package_list()))
            return

        # Case for when package is delayed
        # Priority lvl 2 - These packages must be on Truck 3 since they are not at the depot yet at 8am.
        if delayed_until is not None:
            self.add_package_to_truck(3, package)
            return

        # Case for if required truck is set on package
        # Priority lvl 2 - If a package needs to be on a truck, it goes there.
        if required_truck is not None:
            self.add_package_to_truck(required_truck, package)
            return

        # Case for if deliver_with_list has packages
        # Priority lvl 2 - If a package needs to be delivered with other packages, put them on the same truck together.
        # Space-time complexity: Technically O(N) depending on the number of packages. However, because there is a max
        # of 16 packages per truck, and it is unlikely that more than 16 would need to be delivered together, the
        # space-time complexity is more likely O(1).
        # The number of trucks is also consistent for the purposes of this project.
        if len(deliver_with_list) > 0:
            # Check to see if any packages on the deliver_with_list are already on a truck.
            for sibling_package_id in deliver_with_list:
                sibling_truck_number = self.get_truck_from_package_id(sibling_package_id)
                # If a sibling is found on another truck, add the current package and exit the method.
                if sibling_truck_number is not None:
                    self.add_package_to_truck(int(sibling_truck_number), package)
                    return
            # If no sibling has been added to a truck yet, add it to the first truck.
            self.add_package_to_truck(1, package)
            return
        else:
            # It is unlikely this scenario would occur, but if there are more than 16 packages that "must" be
            # delivered together, all of them would not be able to be loaded together. In this case, a warning
            # message prints for the user.
            print('WARNING: All trucks are too full to fit package requirements. Some packages could not be loaded.')
            return

    # Main method to process unrestricted packages (packages with no special conditions other than delivery deadlines)
    # Nearest Neighbor Algorithm: This program utilizes a nearest neighbor algorithm first, adding packages by
    # closest distance from one another. Packages that all go to the same city are also prioritized to be delivered
    # together. This method also begins accounting for delivery deadlines by prioritizing the trucks that leave
    # earliest in their loading process. Later on, the program will implement a check to make sure delivery deadlines
    # have been met. If they haven't, the program is optimized according to the packages' special conditions, but
    # ultimately still sorted by closest distance from one another.
    # Space-time complexity: O(N). Most other components within this method are O(1).
    def process_unrestricted_package(self, package):
        # Retrieve the package's address.
        package_address = package.get_dest_st_address()
        # Retrieve the package's delivery deadline.
        package_deadline = package.get_delivery_deadline()
        # Retrieve the package's nearest neighbor.
        # Space-time complexity: O(N)
        nearest_neighbor_address = Distance.nearest_neighbor(package_address, self.all_addresses)
        # New flag to keep track if the package has been added to a specific truck.
        package_truck = package.get_current_truck()
        if package_truck != 0:
            added_to_truck = True
        else:
            added_to_truck = False
        # Flag to keep track of identical packages.
        identical_already_added = False
        identical_packages = package.get_delivery_identical()

        # If the package is going to Holladay, add it to Truck 1.
        # There are very few packages that go there, so it's best to have 1 truck dedicated to them.
        # If Truck 1 is full already, the package will still be added below. Later on, the optimize_routes method may
        # move it to Truck 1 if that happens.
        # Packages from other cities will ideally be grouped together using the nearest neighbor algorithm, but if they
        # are not, they will be corrected in the optimization method later on.
        if 'Holladay' in package.get_destination_city() and not added_to_truck:
            added_to_truck = self.add_package_to_truck(1, package)

        # If the package is not added yet, try to add it to the nearest neighbor package's truck.
        if nearest_neighbor_address in self.all_loaded_addresses_by_truck and not added_to_truck:
            associated_trucks = self.all_loaded_addresses_by_truck.get(nearest_neighbor_address)
            for associated_truck in associated_trucks:
                added_to_truck = self.add_package_to_truck(int(associated_truck), package)
                if added_to_truck:
                    break

        # If the package is not added yet and has a deadline, try adding it to one of the trucks that leaves earlier.
        # This depends on the number of drivers set in the class, so the method is flexible as the size of the
        # company grows.
        if package_deadline and not added_to_truck:
            # Iterate through applicable trucks and try to add the package.
            for associated_truck in self.early_trucks:
                added_to_truck = self.add_package_to_truck(int(associated_truck.get_truck_number()), package)
                # If the package is added to the truck, set the added_to_truck flag to True and break the loop.
                if added_to_truck:
                    break

        # If the package still has not been added, try to add it to any available truck.
        if not added_to_truck:
            for associated_truck in self.trucks:
                if len(associated_truck.get_package_list()) < associated_truck.capacity:
                    added_to_truck = self.add_package_to_truck(associated_truck.get_truck_number(), package)
                    if added_to_truck:
                        break

        # Once the package has been loaded, check if it has any identical address packages that could also be loaded.
        if added_to_truck and package.get_has_delivery_identical() and not identical_already_added:
            package_truck = package.get_current_truck()
            for identical_package in identical_packages:
                identical_pkg_truck = identical_package.get_current_truck()
                if identical_pkg_truck == 0:
                    self.add_package_to_truck(package_truck, identical_package)

        # If the package was not loaded onto any truck, all trucks are probably full. This safeguard is here in case
        # there are ever over 48 packages.
        # Print an error message to alert the User.
        if added_to_truck is False:
            print(f'ERROR: Unable to load package {package.get_package_id()}. All trucks may be full.')

    # Method to initiate create_route for all deliverable trucks. Accounts for different start times for the trucks.
    # Space-time complexity: O(N^2)
    def create_all_truck_routes(self):
        # Create the route for Trucks 1 and 2.
        for truck in self.early_trucks:
            # Space-time complexity: O(N^2)
            self.create_route(truck)

        # Determine the start time for Truck 3 based on which of the earlier trucks returns soonest.
        self.third_truck.set_start_time(self.earliest_return_to_depot_time())

        # Create the route for Truck 3.
        route_works = self.create_route(self.third_truck)
        # Return a boolean value representing if the routes meet delivery deadlines.
        # If a False value is returned, the method to optimize the routes will be triggered.
        return route_works

    # Method utilized to sort a truck's current package list by package delivery distance in relation to one another.
    # Space-time complexity: O(N^2) - Depends upon number of unique addresses and number of packages.
    # There are more packages than unique addresses, so amount of packages is the greatest factor in efficiency.
    def create_route(self, truck):
        # Create the route with the packages in order of distance from one another
        self.put_pkgs_in_order(truck)

        # Store the route data needed including distance, time and location.
        self.store_route_data(truck)

        # Check for late deliveries a maximum of 3 times.
        max_iterations = 3
        iterations = 0

        # Set late_packages to True to trigger initial delivery check.
        late_packages = True

        while late_packages and iterations < max_iterations:
            # As long as there continue to be late deliveries, restore the data and check again until they are
            # all resolved.
            late_packages = self.check_late_deliveries(truck)
            self.store_route_data(truck)
            # Increment the iteration count
            iterations += 1

        # If there are still late packages after 3 iterations, return False to trigger the optimize_routes method.
        if late_packages:
            return False
        else:
            return True

    # Method that organizes the packages by address and distance from one another.
    # Space complexity: O(N^2), determined by the sorting step. Time complexity: O(N)
    @staticmethod
    def put_pkgs_in_order(truck):
        # Initialize lists and dictionaries for tracking purposes.
        # Space-time complexity: O(1)
        # Keeps track of all addresses.
        addresses_array = []
        # Keeps track of addresses yet to be loaded.
        remaining_addresses = []
        # Keeps track of package IDs and their associated addresses, grouping IDs that go to the same address.
        shared_addresses = {}

        # Set up the empty route and import Distance data.
        truck.route_addresses = []
        distance_lookup = Distance('./WGUPS_Address_Data.csv', './WGUPS_Distance_Data.csv')

        # Set the truck's first location to its starting location, the HUB.
        current_address = truck.starting_location

        # Group packages by address.
        # Space-time complexity: O(N)
        for package in truck.package_list:
            address = package.get_dest_st_address()
            # Add to addresses array
            addresses_array.append(address)
            # Add to loaded_addresses dictionary
            pkg_id = package.get_package_id()
            if address in shared_addresses:
                shared_addresses[address].append(pkg_id)
            else:
                shared_addresses[address] = [pkg_id]
            remaining_addresses.append(address)

        # Sort the addresses being delivered to by distance from one another.
        # Space-time complexity: O(N^2)
        while remaining_addresses:
            if len(truck.route_addresses) != 0:
                # Get the previous address in the route.
                current_address = truck.route_addresses[-1][1]
            nearest_address = None
            min_distance = float('inf')

            # Find the nearest address to the current address.
            # Space-time complexity: O(N)
            for address in remaining_addresses:
                distance = distance_lookup.lookup_distance(current_address, address)
                if distance <= min_distance:
                    min_distance = distance
                    nearest_address = address

            # Update the current location along delivery route.
            current_address = nearest_address

            # Add the nearest address and its associated package IDs to the route and remove it from the remaining
            # addresses. Each item in route is an array [package_id, nearest_address].
            package_id = shared_addresses[nearest_address].pop()
            truck.route_addresses.append([package_id, nearest_address])
            remaining_addresses.remove(nearest_address)

    # Method to store the route data including distance, location, and times.
    # This method also adds the distance traveled back to the HUB after the last package is delivered.
    # If any changes are made to a truck's route_addresses, this should be called afterwards.
    # Space-time complexity: O(N)
    def store_route_data(self, truck):
        # Initialize current time variable.
        truck.set_current_time(truck.get_start_time())
        # Initialize distance variable.
        total_distance = float(0)
        # Initialize the truck_location_log and current location.
        truck.truck_location_log = {}
        truck.set_current_location(truck.get_starting_location())
        # Begin storing the truck's location at specific times.
        truck.truck_location_log = {truck.get_start_time().time(): truck.starting_location}

        # Iterate through the route stops.
        # Space-time complexity: O(N)
        for package_stop_index, package_stop in enumerate(truck.route_addresses):
            pkg_id, next_address = package_stop

            # Calculate the distance between this stop and the last stop.
            stop_distance = Distance.retrieve_distance_wgups(truck.current_location, next_address)

            # Calculate time taken to deliver the package from current_address to nearest_address using truck's
            # speed (18 miles per hour).
            # Space-time complexity for each calculation: O(1)
            # Space-time complexity overall: O(N) where N is the number of packages.
            time_taken_hours_float = stop_distance / truck.speed
            time_taken_timedelta = timedelta(hours=time_taken_hours_float)
            # Increment the current_time by the time_taken_timedelta.
            truck.current_time += time_taken_timedelta

            # Increment total distance of the truck.
            total_distance = total_distance + stop_distance

            # Update the current location.
            truck.set_current_location(next_address)

            # Set the package's delivered time.
            package = self.get_package_by_id(pkg_id)
            package.set_delivered_time(truck.current_time)

            # Store the truck's location at the current time in the log.
            truck.truck_location_log[truck.current_time.time()] = next_address

        # Add the distance it takes to travel back to the HUB.
        # First, find the last package in the route. Take the distance from that package to the HUB.
        # Space-time complexity: O(1)
        last_package = self.get_package_by_id(truck.get_last_package_in_route())
        travel_home_distance = Distance.retrieve_distance_wgups(
            last_package.get_dest_st_address(), truck.starting_location)
        # Add the travel_home_distance to the truck's total distance to
        # account for the truck's trip back to the HUB.
        truck.set_total_distance(total_distance + travel_home_distance)
        # Set the return to HUB time.
        travel_home_time_float = travel_home_distance / truck.speed
        travel_home_time_timedelta = timedelta(hours=travel_home_time_float)
        return_time = truck.current_time + travel_home_time_timedelta
        truck.set_return_time(return_time)

        # Create the route by simplifying route_addresses to display the package IDs only.
        truck.set_route(cp.deepcopy(truck.route_addresses))
        for index, id_address_pair in enumerate(truck.route):
            truck.route[index] = id_address_pair[0]

    # Method that checks if delivery times are currently being met. If not, the packages are rearranged until all
    # delivery times are met.
    # Space-time complexity: O(N)
    def check_late_deliveries(self, truck):
        # Initialize a flag for if late packages exist.
        late_packages = False

        # Assess if package delivery time has been met successfully by iterating over each package.
        # Space-time complexity: O(N)
        for pkg_stop_index, pkg_stop in enumerate(truck.route_addresses):
            pkg_id, pkg_address = pkg_stop
            # Retrieve each package's delivery deadline.
            package = self.get_package_by_id(pkg_id)
            delivery_deadline = package.get_delivery_deadline()
            # If it has a deadline, assess if the deadline was met.
            # Make sure the package is being delivered on time if it has a deadline.
            if delivery_deadline:
                delivered_on_time = self.compare_two_times(package.get_delivered_time(), delivery_deadline)
                # If it is not on time, move it up to the front of the route.
                if not delivered_on_time:
                    # Move the package and any other packages with the same address up together.
                    self.move_package_up(pkg_stop_index, truck)
                    # Break out of the method here as long as there are late packages.
                    late_packages = True

        # Returning a True value indicates that late packages existed, and the method should be called to begin again.
        if late_packages:
            return True
        else:
            return False

    # Method to optimize the routes if delivery times are not being met. Moves the packages between trucks based
    # on their special conditions and locations. Nearest neighbor algorithm is utilized here, too.
    # Space complexity: O(1), Time complexity: O(N)
    def optimize_routes(self):
        # Create empty sets to track packages that need to be moved around
        packages_to_move = set()
        packages_to_move_deadlines = set()
        packages_to_move_cities = set()

        # Compile packages with no deadline or package restrictions from Truck 1 and 2.
        # Space-time complexity O(N) where N is the number of packages.
        for truck in self.trucks:
            for package in truck.get_package_list():
                # Move any packages delivering to other cities that could be grouped better on trucks
                if package.get_destination_city() in ['Holladay', 'Murray', 'West Valley City']:
                    packages_to_move_cities.add(package)
                    continue
                # Move any package from Truck 1 or 2 that does not have a delivery deadline and is not restricted.
                if package.get_delivery_deadline() is None and package.is_package_restricted() is False:
                    if package.get_current_truck() == 1:
                        packages_to_move.add(package)
                        continue
                    if package.get_current_truck() == 2 and not package.identical_packages_are_restricted():
                        packages_to_move.add(package)
                        continue
                # Move any packages with deadlines that aren't delayed from Truck 3.
                if package.get_delivery_deadline() is not None and package.is_package_restricted() is False:
                    if package.get_current_truck() == 3:
                        packages_to_move_deadlines.add(package)

        # Remove the packages that need to be moved from the trucks they are currently on.
        # Space-time complexity: O(N)
        for package in packages_to_move:
            self.remove_package_from_truck(package.get_current_truck(), package)
        for package in packages_to_move_deadlines:
            self.remove_package_from_truck(package.get_current_truck(), package)
        for package in packages_to_move_cities:
            self.remove_package_from_truck(package.get_current_truck(), package)

        # Add different cities packages to the correct trucks.
        # Space-time complexity: O(N)
        for package in packages_to_move_cities:
            # Group Holladay packages to Truck 1.
            if 'Holladay' in package.get_destination_city():
                self.add_package_to_truck(1, package)
            # Group Murray packages to Truck 3.
            elif 'Murray' in package.get_destination_city():
                self.add_package_to_truck(3, package)
            # Group West Valley City packages to Truck 2.
            elif 'West Valley City' in package.get_destination_city():
                self.add_package_to_truck(2, package)

        # Add deadline packages to Truck 1 if possible since it leaves right at 8am.
        # Space-time complexity: O(N)
        for package in packages_to_move_deadlines:
            added_to_truck = self.add_package_to_truck(1, package)
            if not added_to_truck:
                # Add to Truck 2 if Truck 1 is full.
                self.add_package_to_truck(2, package)

        # Add the other packages first based on nearest neighbor. If that does not work, add them to Truck 1 if there
        # is room or Truck 3, since they can be completed at any time.
        # Space-time complexity: O(N)
        for package in packages_to_move:
            added_to_truck = False
            # Retrieve the package's nearest neighbor.
            nearest_neighbor_address = Distance.nearest_neighbor(package.get_dest_st_address(), self.all_addresses)
            if nearest_neighbor_address in self.all_loaded_addresses_by_truck and not added_to_truck:
                associated_trucks = self.all_loaded_addresses_by_truck.get(nearest_neighbor_address)
                for associated_truck in associated_trucks:
                    added_to_truck = self.add_package_to_truck(int(associated_truck), package)
                    if added_to_truck:
                        continue
            # If nearest neighbor was not detected, simply add to a truck based on truck prioritization
            # mentioned earlier.
            if not added_to_truck:
                added_to_truck = self.add_package_to_truck(1, package)
                if not added_to_truck:
                    # Add to Truck 3 if Truck 1 is full.
                    added_to_truck = self.add_package_to_truck(3, package)
                    if not added_to_truck:
                        # Add to Truck 2 as a last resort. The return of Truck 2 determines when Truck 3 leaves, so
                        # keeping its route short is important.
                        self.add_package_to_truck(2, package)

    # Main method for processing truck travel info and updating the start time of the third truck.
    # Space-time complexity: O(1)
    def earliest_return_to_depot_time(self):
        # Set delayed time based on the flight's arrival in the depot.
        delayed_time = datetime(year=1, month=1, day=1, hour=9, minute=5, second=0)

        # Determine if Truck 1 or Truck 2 returned to the depot first. Set the earliest_time.
        if self.first_truck.get_return_time() < self.second_truck.get_return_time():
            earliest_time = self.first_truck.get_return_time()
        else:
            earliest_time = self.second_truck.get_return_time()

        # Make sure the earliest time is not before the delayed packages arrive.
        if earliest_time < delayed_time:
            earliest_time = delayed_time

        # Return the earliest_time which will be set as Truck 3's start time.
        return earliest_time

    # Method to add a package to the truck using the truck's id (in this case: 1, 2, 3, or 4)
    # Space-time complexity: O(N)
    def add_package_to_truck(self, truck_id, package):
        # Get relevant truck_id and make sure it is an integer.
        truck = self.get_truck_index_by_id(truck_id)
        truck_int = int(truck_id)
        # Flag to determine if package was added successfully. Attempts to add the package to the truck.
        # Space-time complexity: O(1)
        package_added_success = truck.add_package(package)

        # If the package is added
        if package_added_success:
            # Make sure the package is not flagged.
            if package.get_package_flagged() is False:
                # Retrieve the package's destination address.
                address = package.get_dest_st_address()

                # Check if the address already exists in the dictionary.
                # Space-time complexity: O(N)
                if address in self.all_loaded_addresses_by_truck:
                    # If the address already exists, check if the truck_id is not already in the list.
                    if truck_int not in self.all_loaded_addresses_by_truck[address]:
                        # If the truck_id is not present, append it to the list for that address.
                        self.all_loaded_addresses_by_truck[address].append(truck_int)
                else:
                    # If the address is not in the dictionary, create a new list with the truck_id.
                    self.all_loaded_addresses_by_truck[address] = [truck_int]

                # Remove the package from remaining_package_ids (for unrestricted package loop).
                if package.get_package_id() in self.remaining_package_ids:
                    self.remaining_package_ids.remove(package.get_package_id())
            # Return True if the package was added.
            return True
        # Return False if the package could not be added, likely because the truck was full.
        # This is ultimately determined in add_package in the Truck class.
        else:
            return False

    # Method to remove a package from the truck.
    # Space-time complexity: O(1)
    def remove_package_from_truck(self, truck_id, package):
        truck = self.get_truck_index_by_id(truck_id)
        truck_int = int(truck_id)
        # Remove the package.
        # Space-time complexity: O(1)
        truck.remove_package(package)

        # Make sure the package is not flagged.
        if package.get_package_flagged() is False:
            # Retrieve the package's destination address.
            address = package.get_dest_st_address()

            # Check if the address already exists in the dictionary.
            # Space-time complexity: O(1)
            if address in self.all_loaded_addresses_by_truck:
                # If the address already exists, check if the truck_id is in the list.
                if truck_int in self.all_loaded_addresses_by_truck[address]:
                    # If the truck_id is present, remove it from the list for that address.
                    self.all_loaded_addresses_by_truck[address].remove(truck_int)
                    # Check if the list for that address is empty after removing the truck_int.
                    if not self.all_loaded_addresses_by_truck[address]:
                        # If the list is empty, remove the address entirely from the dictionary.
                        self.all_loaded_addresses_by_truck.pop(address)

            # Add the package to remaining_package_ids (for unrestricted package loop).
            if package.get_package_id() not in self.remaining_package_ids:
                self.remaining_package_ids.append(package.get_package_id())

    # Method that corrects flagged packages.
    # In a larger implementation of this program, this would be fleshed out more with user input options and more
    # flexibility. For the purposes of this project, only package 9 needs to be corrected.
    # Space-time complexity: O(N)
    def correct_flagged_packages(self, current_time):
        # Set a flag to determine if corrections were made
        # Space-time complexity: O(1)
        corrections_made = False
        flagged_packages = self.get_flagged_packages()

        # Check if there are flagged packages.
        if len(flagged_packages) != 0:
            # Initialize a list to keep track of corrected packages.
            flagged_packages_corrected = []

            # Begin iterating through the flagged packages.
            # Space-time complexity: O(N) where N is the number of flagged packages
            for flagged_package_id in flagged_packages:
                # Retrieve the package.
                package = self.get_package_by_id(flagged_package_id)
                # Set the time that the information should be corrected.
                delayed_until = package.get_delayed_until()
                delayed_until_time_obj = self.convert_to_datetime(delayed_until)

                # Check if the flagged package's delayed time is earlier than the provided current_time
                corrections_needed = self.compare_two_times(delayed_until_time_obj, current_time)

                # If it is later than the delayed time, implement the corrections.
                if corrections_needed:
                    # Make address corrections based on data provided by WGU.
                    package.set_dest_st_address('410 S State St')
                    package.set_destination_city('Salt Lake City')
                    package.set_destination_state('UT')
                    package.set_destination_zipcode('84111')

                    # Add it to the list of corrected packages.
                    flagged_packages_corrected.append(flagged_package_id)
                    # Update the third truck capacity to hold the new packages.
                    self.third_truck.set_capacity(self.third_truck.capacity + len(flagged_packages))
                    # Reset the package's flagged status to False.
                    package.set_package_flagged(False)
                    # Remove the package from the hold truck.
                    self.hold_truck.remove_package(package)
                    # Add it to the third truck package list and route.
                    self.add_package_to_truck(3, package)
                    self.third_truck.route_addresses.append([package.get_package_id(), package.get_dest_st_address()])
                    # Set the corrections_made flag.
                    corrections_made = True
                    # Update the data for the third truck.
                    self.store_route_data(self.third_truck)

            # Remove correct flagged packages from the flagged packages list.
            self.flagged_packages = [pkg for pkg in flagged_packages if pkg not in flagged_packages_corrected]

            if corrections_made:
                return True
            else:
                return False

    # Helper method to move package and associated packages with the same address up earlier in the route.
    # Space-time complexity: O(N)
    @staticmethod
    def move_package_up(package_stop_index, truck):
        # Get the package stop and its address from the current route.
        # Space-time complexity: O(1)
        package_stop = truck.route_addresses.pop(package_stop_index)
        pkg_id, next_address = package_stop

        # Find all other packages with the same address and remove them from the route.
        # Space-time complexity: O(N)
        associated_packages = [stop for stop in truck.route_addresses if stop[1] == next_address]
        for associated_package in associated_packages:
            truck.route_addresses.remove(associated_package)

        # Insert the packages at the beginning of the route.
        # Space-time complexity: O(1)
        truck.route_addresses = [package_stop] + associated_packages + truck.route_addresses

    # Necessary information getters/setters to streamline code and make info retrieval easier
    # Method to get loaded_addresses_by_truck, which stores addresses associated with specific truck numbers
    # Space-time complexity: O(1)
    def get_loaded_addresses_by_truck(self):
        return self.all_loaded_addresses_by_truck

    # Method to set the loaded_addresses_by_truck.
    # Space-time complexity: O(N)
    # Technically, the space-time complexity could be O(N*M), where N is the number of trucks and M is the number of
    # loaded addresses. However, there can only be a maximum of 16 addresses associated with a truck, so that can be
    # considered a constant. There are consistently only 3 trucks, but if the company grows, they could get more.
    def set_loaded_addresses_by_truck(self):
        # Clear any current entries in loaded_addresses_by_truck.
        self.all_loaded_addresses_by_truck = {}

        # Iterate through all the trucks.
        # Retrieve each individual dictionary of addresses and add it to the main dictionary of loaded addresses.
        # Space-time complexity: O(N)
        for truck in self.trucks:
            loaded_addresses = truck.get_loaded_addresses_by_truck()
            for address, truck_number in loaded_addresses.items():
                truck_int = int(truck_number)
                # Check if the address already exists in the dictionary.
                # One address could be associated with multiple trucks due to package restrictions.
                if address in self.all_loaded_addresses_by_truck:
                    # If the address already exists, check if the truck_number is not already in the list.
                    if truck_number not in self.all_loaded_addresses_by_truck[address]:
                        # If the truck_number is not present, append it to the list for that address.
                        self.all_loaded_addresses_by_truck[address].append(truck_int)
                else:
                    # If the address is not in the dictionary, create a new list with the truck_number.
                    self.all_loaded_addresses_by_truck[address] = [truck_int]

    # Retrieve all flagged packages.
    # Space-time complexity: O(1)
    def get_flagged_packages(self):
        return self.flagged_packages

    # Set flagged packages.
    # Space-time complexity: O(1)
    def set_flagged_packages(self, flagged_packages):
        self.flagged_packages = flagged_packages

    # Method to retrieve a truck's index by its ID. The index is 1 less than the ID.
    # Space-time complexity: O(1)
    def get_truck_index_by_id(self, truck_id):
        truck_index = int(truck_id) - 1
        if len(self.trucks_and_hold) >= truck_index:
            return self.trucks_and_hold[truck_index]
        else:
            print('truck id ' + truck_id + ' does not exist in available trucks')
            return None

    # Method to retrieve a truck number by a package ID that is loaded on it.
    # Space-time complexity: O(N) where N is the number of trucks. The number of trucks is consistent for this project,
    # so it may be considered to be O(1).
    def get_truck_from_package_id(self, package_id):
        for truck in self.trucks:
            if truck.is_package_on_truck(package_id):
                return truck.get_truck_number()
        return None

    # Method to retrieve a truck object using its ID.
    # Space-time complexity: O(N), or O(1) if number of trucks is considered constant.
    def get_current_truck_object(self, truck_id):
        # Find the corresponding Truck object in the truck_list.
        for truck in self.trucks_and_hold:
            if truck.get_truck_number() == truck_id:
                return truck
        # If the truck is not found, return None.
        return None

    # Retrieve package by ID.
    # Space-time complexity: O(N)
    def get_package_by_id(self, package_id):
        # Loop through the hash table of packages and find the package with the given package ID.
        for bucket in self._original_package_table.get_hash_table():
            for _, package in bucket:
                if package.get_package_id() == package_id:
                    return package

        # If the package with the given ID is not found, return None or raise an exception.
        print(f'Package with ID {package_id} not found.')
        return None

    # Retrieve the total distance traveled by all trucks.
    # Space-time complexity: O(1)
    def get_total_distance(self):
        return self.total_distance_of_all_trucks

    # Set the total distance traveled by all trucks by adding up each trucks' individual distance traveled.
    # Space-time complexity: O(N), or O(1) if number of trucks is considered constant.
    def set_total_distance(self):
        all_trucks_total_distance = 0
        for truck in self.trucks:
            all_trucks_total_distance += truck.get_total_distance()
        self.total_distance_of_all_trucks = all_trucks_total_distance

    # Get number of drivers.
    # Space-time complexity: O(1)
    def get_number_or_drivers(self):
        return self.number_of_drivers

    # Set number of drivers.
    # Space-time complexity: O(1)
    def set_number_of_drivers(self, total_drivers):
        self.number_of_drivers = total_drivers

    # Function to get the location of a specific truck at a given time
    # Space-time complexity: O(N)
    def get_truck_location_at_time(self, truck, user_time_str):
        try:
            # Convert user_time_str to a datetime object.
            user_datetime = self.convert_to_datetime(user_time_str)

            # Find the nearest time in the log to the user input time.
            nearest_time = None
            min_time_difference = timedelta(days=365)  # Set an initial large value for the difference
            # Space-time complexity: O(N)
            for log_time in truck.truck_location_log.keys():
                time_difference = abs(datetime.combine(datetime.today(), log_time) - user_datetime)
                if time_difference < min_time_difference:
                    min_time_difference = time_difference
                    nearest_time = log_time

            # Return the address corresponding with the nearest time.
            nearest_address = truck.truck_location_log[nearest_time]
            return nearest_address

        except ValueError:
            print('ERROR: Truck location data could not be retrieved.')
            return None

    # Set a package's delivery status based on time input.
    # Space-time complexity: O(N), or O(1) if number of trucks is considered constant.
    def assess_delivery_status(self, package, user_time_input):
        # Retrieve relevant info.
        is_flagged = package.get_package_flagged()

        # Check if it is flagged.
        if is_flagged:
            # Set any flagged package's status to "at hub".
            delivery_status = 'At HUB'
            package.set_delivery_status(delivery_status)
        # If it is not flagged:
        else:
            # Retrieve the package's truck's start time.
            truck_number = package.get_current_truck()
            current_truck_object = self.get_current_truck_object(truck_number)
            truck_start_time = current_truck_object.start_time
            # Retrieve the package's delivery time.
            package_delivery_time = package.get_delivered_time().time()
            # Assess the delivery status of the package based on comparing the user input time with both the start time
            # and delivery times.
            delivery_status = self.assess_time_input(truck_start_time, package_delivery_time, user_time_input)
            # Set the package's delivery status based on the results of assess_time_input.
            package.set_delivery_status(delivery_status)

    # Calculation Methods
    # Method to compare two different times.
    # Space-time complexity: O(1)
    @staticmethod
    def compare_two_times(first_time, second_time):
        # Convert both times into seconds.
        first_time_total_seconds = first_time.hour * 3600 + first_time.minute * 60 + first_time.second
        second_time_total_seconds = second_time.hour * 3600 + second_time.minute * 60 + second_time.second

        # If the first time is earlier than the second time, return True.
        if first_time_total_seconds <= second_time_total_seconds:
            return True
        # If the second time is earlier than the first time, return False.
        else:
            return False

    # Method to determine a package's delivery status based on user time input.
    # Space-time complexity: O(1)
    @staticmethod
    def assess_time_input(start_time, delivered_time, user_time):
        # Convert all times into seconds.
        start_time_total_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        delivered_time_total_seconds = delivered_time.hour * 3600 + delivered_time.minute * 60 + delivered_time.second
        user_time_total_seconds = user_time.hour * 3600 + user_time.minute * 60 + user_time.second

        # If User Time is less than or equal to the Start Time, the package is at the HUB.
        if user_time_total_seconds <= start_time_total_seconds:
            delivery_status = 'At HUB'
        # If User Time is more than or equal to the Delivered Time, the package has been Delivered.
        elif user_time_total_seconds >= delivered_time_total_seconds:
            delivery_status = 'Delivered'
        # Otherwise, the package is En Route.
        else:
            delivery_status = 'En Route'
        return delivery_status

    # Date time conversion for proper time formatting
    # Space-time complexity: O(1)
    @staticmethod
    def read_time(original_time):
        if isinstance(original_time, str):
            format_string = '%H:%M:%S'
            time_object = datetime.strptime(original_time, format_string).time()
        else:
            time_object = original_time
        return time_object

    # This program is created for a single day, so the date functionality is not utilized.
    # Some operations require datetime format, though, so this method can be used to convert a time object to a
    # datetime object.
    # Space-time complexity: O(1)
    def convert_to_datetime(self, original_time):
        if isinstance(original_time, str):
            time_object = self.read_time(original_time)
            datetime_object = datetime.combine(datetime.today(), time_object)
            return datetime_object
        elif isinstance(original_time, time):
            datetime_object = datetime.combine(datetime.today(), original_time)
            return datetime_object
        elif isinstance(original_time, datetime):
            datetime_object = original_time
            return datetime_object
        else:
            print('ERROR: Invalid data. Unable to read datetime data.')
            return None

    # Printing methods
    # Print truck stats. Used for testing purposes. Included for clarity and debugging.
    # Space-time complexity: O(N)
    def print_truck_stats(self, current_time):
        # Correct any flagged packages if time-appropriate.
        # Space-time complexity: O(N)
        self.correct_flagged_packages(current_time)

        # Print info for each truck.
        # Space-time complexity: O(N), or O(1) if number of trucks is considered constant.
        for truck in self.trucks:
            total_distance = truck.get_total_distance()
            start_time_formatted = truck.start_time.strftime('%H:%M:%S')
            return_time_formatted = truck.return_time.strftime('%H:%M:%S')
            truck.print_package_list()
            print(f'Truck {truck.truck_number} route: {truck.route} + travel back to HUB\n'
                  f'Truck {truck.truck_number} final location before HUB: {truck.current_location} \n'
                  f'Truck {truck.truck_number} total distance traveled: {total_distance} miles \n'
                  f'Truck {truck.get_truck_number()} Start Time: {start_time_formatted}, '
                  f'Return Time: {return_time_formatted}\n')

        # Print total distance for all trucks.
        print('TOTAL DISTANCE FOR ALL TRUCKS \n', f'{self.get_total_distance()} miles\n')

        # Print hold truck info.
        print('FLAGGED PACKAGES WITHIN HOLD:')
        self.hold_truck.print_package_list()

        # Print remaining packages. This should be blank and is included for debugging purposes.
        print(f'\n{len(self.remaining_package_ids)} packages remaining:')
        print('Remaining packages:', self.remaining_package_ids)

    # Get all information pertaining to a specific package.
    # Used for option 1 in User Menu search results.
    # Space-time complexity: O(N)
    def print_full_package_info(self, package, user_time):
        # Correct any flagged packages if time-appropriate.
        # Space-time complexity: O(N)
        self.correct_flagged_packages(user_time)

        # Retrieve current truck information.
        current_truck_num = package.get_current_truck()
        current_truck_object = self.get_current_truck_object(current_truck_num)
        # Assess and retrieve delivery status.
        self.assess_delivery_status(package, user_time)
        delivery_status = package.get_delivery_status()

        # Set conditions to format displayed text depending on delivery status.
        # Space-time complexity: O(1)
        # Deliverable trucks:
        if package.current_truck <= 3:
            if 'Delivered' in delivery_status:
                delivered_datetime = package.get_delivered_time()
                delivered_time = self.read_time(delivered_datetime)
                formatted_del_time = delivered_time.strftime('%H:%M:%S')
                current_location = package.get_dest_st_address()
                current_truck_info = f'Delivered to {current_location}'
                delivery_status = f'{delivery_status} at {formatted_del_time}'
            elif 'En Route' in delivery_status:
                current_location = self.get_truck_location_at_time(current_truck_object, user_time)
                current_truck_info = f'On Truck {package.current_truck} Route, {current_location}'
            # If delivery status = 'At HUB'
            else:
                current_location = current_truck_object.starting_location
                current_truck_info = f'Loaded on Truck {package.current_truck}, {current_location}'
        # Non-deliverable trucks (for Flagged Packages):
        else:
            current_truck_info = 'In Hold Compartment, Flagged Package'

        print_id = f'Package ID: {package.pkg_id}'
        print_address = f'Delivery Address: {package.get_full_address()}'
        print_weight = f'Package Weight: {package.pkg_weight} kilos'
        print_deadline = f'Delivery Deadline: {package.delivery_deadline}'
        print_status = f'Delivery Status: {delivery_status}'
        print_time = f'Current Time: {user_time}'
        print_location = f'Current Location: {current_truck_info}'

        # Combine the strings in an array.
        results_line_1 = [print_id, print_address]
        results_line_2 = [print_deadline, print_status]
        results_line_3 = [print_weight, print_time, print_location]
        indent = '\t\t\t\t '

        # Print the arrays with proper formatting.
        print('\n' + ' | '.join(results_line_1))
        print(indent + ' | '.join(results_line_2))
        print(indent + ' | '.join(results_line_3))

    # Print all packages in a list for option 2 in User Menu.
    # Space-time complexity: O(N^2)
    def print_all_packages_details(self, user_time_input):
        user_time_object = self.read_time(user_time_input)
        # Get all packages from the original package table and flatten them into a single list.
        all_packages = [package for bucket in self._original_package_table.get_hash_table() for package in bucket]
        # Sort the list of packages based on package ID.
        sorted_packages = sorted(all_packages, key=lambda package: int(package[0]))

        # Print all packages.
        # Space-time complexity: O(N)
        for package_id, package in sorted_packages:
            # Space-time complexity: O(N)
            self.print_full_package_info(package, user_time_object)
