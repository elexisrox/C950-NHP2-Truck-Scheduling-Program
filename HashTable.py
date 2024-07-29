# Main class for the package hash table, utilizing no other classes or libraries.
# Space-time complexity: O(N)
class HashTable:
    # Initialize the class
    # The number of buckets in the hash table is set to 23. This number was arbitrarily chosen, within the expectation
    # that it should be less than the number of packages to deliver in order to exhibit the flexibility of a hash table.
    def __init__(self, initial_capacity=23):
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])

    # Method to create the hash key.
    # Space-time complexity: O(1)
    def get_hash(self, key):
        bucket = hash(key) % len(self.table)
        return bucket

    # Method to retrieve hash table.
    # Space-time complexity: O(1)
    def get_hash_table(self):
        return self.table

    # Creates new entry and inserts it into the hash table
    # Space-time complexity: O(1)
    def insert(self, package_id, package):
        bucket_hash = self.get_hash(package_id)
        key_entry = [package_id, package]

        # Checks if bucket is empty. If it is, the bucket is converted to an array.
        if self.table[bucket_hash] is None:
            self.table[bucket_hash] = list([key_entry])
            return True
        # If the bucket is not empty, append the entry to the list.
        else:
            for new_entry in self.table[bucket_hash]:
                if new_entry[0] == package_id:
                    new_entry[1] = key_entry
                    return True
            self.table[bucket_hash].append(key_entry)
            return True

    # Updates an entry within the hash table.
    # Space-time complexity: O(N) where N is the number of entries in the bucket
    def modify(self, key, value):
        bucket_hash = self.get_hash(key)
        if self.table[bucket_hash] is not None:
            for new_entry in self.table[bucket_hash]:
                if new_entry[0] == key:
                    new_entry[1] = value
                    return True
            else:
                print('An error occurred while updating key #' + key)

    # Searches for an entry within the hash table.
    # Space-time complexity: O(N)
    def search(self, key):
        bucket_hash = self.get_hash(key)

        if self.table[bucket_hash] is not None:
            for new_entry in self.table[bucket_hash]:
                if new_entry[0] == key:
                    return new_entry[1]
        else:
            print('The entry could not be found because it does not exist.')
            return None

    # Deletes an entry from the hash table.
    # Space-time complexity: O(1)
    def remove(self, key):
        bucket_hash = self.get_hash(key)
        if self.table[bucket_hash] is None:
            print('The entry was not deleted because it does not exist.')
        for i in range(0, len(self.table[bucket_hash])):
            if self.table[bucket_hash][i][0] == key:
                self.table[bucket_hash].pop(i)
                return True
        return False
