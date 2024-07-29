from datetime import datetime


# Contains all data relevant to each individual package.
# Space_time complexity: O(N) based on the number of identical delivery address packages.
class Package:
    # Initializer
    def __init__(self, pkg_id, dest_street_add, dest_city, dest_state, dest_zip, deadline, pkg_weight, notes):
        self.pkg_id = pkg_id
        self.dest_st_address = dest_street_add
        self.dest_city = dest_city
        self.dest_state = dest_state
        self.dest_zip = dest_zip
        self.delivery_deadline = deadline
        self.pkg_weight = pkg_weight
        self.special_notes = notes

        self.required_truck = None
        self.delayed_until = None
        self.deliver_with = []
        self.delivery_status = 'At HUB'
        self.delivered_time = None
        self.current_truck = 0
        # Used to track which packages have an identical delivery address to another package.
        self.has_delivery_identical = False
        self.delivery_identical = set()
        # Used to flag packages that may cause errors, such as an incorrect address.
        self.package_flagged = False

    # Getters for all package data
    # Space_time complexity for getters: O(1)
    def get_package_id(self):
        return self.pkg_id

    def get_dest_st_address(self):
        return self.dest_st_address

    def get_destination_city(self):
        return self.dest_city

    def get_destination_state(self):
        return self.dest_state

    def get_destination_zipcode(self):
        return self.dest_zip

    def get_delivery_deadline(self):
        if self.delivery_deadline == 'EOD':
            return None
        else:
            del_deadline = datetime.strptime(self.delivery_deadline, "%H:%M:%S").time()
            return del_deadline

    def get_package_weight(self):
        return self.pkg_weight

    def get_special_notes(self):
        return self.special_notes

    def get_delivery_status(self):
        return self.delivery_status

    def get_delivered_time(self):
        if self.delivered_time:
            return self.delivered_time
        else:
            return None

    # Setters for all package data.
    # Some are not used within this project, but are declared for program flexibility.
    # Space_time complexity for all setters: O(1)
    def set_package_id(self, pkg_id):
        self.pkg_id = pkg_id

    def set_dest_st_address(self, dest_street_add):
        self.dest_st_address = dest_street_add

    def set_destination_city(self, dest_city):
        self.dest_city = dest_city

    def set_destination_state(self, dest_state):
        self.dest_state = dest_state

    def set_destination_zipcode(self, dest_zip):
        self.dest_zip = dest_zip

    def set_delivery_deadline(self, deadline):
        self.delivery_deadline = deadline

    def set_package_weight(self, pkg_weight):
        self.pkg_weight = pkg_weight

    def set_special_notes(self, notes):
        self.special_notes = notes

    def set_delivery_status(self, delivery_status):
        self.delivery_status = delivery_status

    def set_delivered_time(self, delivered_time):
        self.delivered_time = delivered_time

    # Combines multiple address properties into one full address.
    # No setter provided because all address properties should be set individually by the above setters.
    def get_full_address(self):
        return f'{self.dest_st_address}, {self.dest_city}, {self.dest_state} {self.dest_zip}'

    # Getters for all parsed notes properties and other flags.
    def get_required_truck(self):
        return self.required_truck

    def get_delayed_until(self):
        return self.delayed_until

    def get_deliver_with(self):
        return self.deliver_with

    def get_current_truck(self):
        return self.current_truck

    def get_has_delivery_identical(self):
        return self.has_delivery_identical

    def get_delivery_identical(self):
        if self.delivery_identical:
            return self.delivery_identical
        else:
            return None

    def get_package_flagged(self):
        return self.package_flagged

    # Setters for all parsed notes properties.
    def set_required_truck(self, req_truck):
        self.required_truck = req_truck

    def set_delayed_until(self, delayed_until):
        self.delayed_until = delayed_until

    def set_deliver_with(self, deliver_with):
        self.deliver_with = deliver_with

    def set_current_truck(self, current_truck):
        self.current_truck = current_truck

    def set_has_delivery_identical(self, boolean_value):
        self.has_delivery_identical = boolean_value

    def add_delivery_identical(self, delivery_sibling):
        self.delivery_identical.add(delivery_sibling)

    def set_package_flagged(self, package_flagged):
        self.package_flagged = package_flagged

    # Determines if a package has special conditions.
    # Space_time complexity: O(1)
    def is_package_restricted(self):
        is_flagged = self.package_flagged
        has_required_truck = self.required_truck is not None
        has_sibling_packages = len(self.deliver_with) > 0
        has_delayed_until = self.get_delayed_until() is not None
        return is_flagged or has_required_truck or has_sibling_packages or has_delayed_until

    # Check to see if a package's identical address matches are restricted or have deadlines.
    # Space_time complexity: O(N)
    def identical_packages_are_restricted(self):
        # Check if the package has identical delivery address packages.
        if self.get_delivery_identical() is not None:
            # If it does, iterate over the "identical" packages.
            for identical_package in self.get_delivery_identical():
                # Make sure the "identical" package being reviewed is not itself.
                if identical_package.get_package_id() != self.get_package_id():
                    # Check if the "identical" package is restricted or has a deadline.
                    if identical_package.is_package_restricted() or \
                            identical_package.get_delivery_deadline() is not None:
                        # If either of those things are true, return True.
                        return True
                    else:
                        return False
        return False
