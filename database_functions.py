"""
Tarık Burhan
"""


import pymongo
from typing import Any


class Database:
    """
    Database functionality class of MongoDB client.
    """
    def __init__(self, client_ip: str, database_name: str, collection_name: str):
        """
        Connect to MongoDB database client.

        Initialize MongoDB client with given database name and collection name of the given IP address of database.

        :param str client_ip: Client IP of the database to connect. (IP and PORT address must be given together).
        :param str database_name: Database name in the given Client.
        :param str collection_name: Collection name in the given database name in the given Client.
        """
        self.client_ip = client_ip
        self.client = pymongo.MongoClient(self.client_ip)
        self.database_name = database_name
        self.collection_name = collection_name
        self.db = self.client[self.database_name]
        self.col = self.db[self.collection_name]

    def insert(self, item: dict):
        """
        Inserts given item in database as new item.

        :param dict item: Item to insert into the database.
        """
        self.col.insert_one(item)

    def delete_collection(self):
        """
        Delete the current collection that is connected to Client and create new empty instance of the collection.
        """
        self.db[self.collection_name].drop()
        self.db.create_collection(self.collection_name)

    def exists(self, key: str, value: Any) -> int:
        """
        Find if given key-value pair exists in the collection and returns number of occurences in collection.

        :param str key: Key value of the search.
        :param Any value: Value of the given key of the search.
        :rtype: int
        """
        return self.col.count_documents({key: value})

    def find_exists_in_key(self, key:str, value: Any) -> dict:
        """
        Find if given value is in the key value in the collection.

        :param str key: Key value of the search
        :param Any value: Value of the given key of the search
        :rtype: dict
        """
        search = f'.*{value}.*'
        return self.col.find({key: {'$regex': search}})

    def get_all(self) -> dict:
        """
        Gets all the collection in the database.

        :rtype: dict
        """
        return self.col.find({})
    
    def replace(self, key: str, value: Any, new_item: dict):
        """
        Replaces given new item with the existing item in the collection

        :param str key: Replaced key 
        :param Any value: Replaced value
        :param dict new_item: New item to replace existing item
        """
        self.col.replace_one({key: value}, new_item)

    def update_one(self, key: str, value: Any, change_key: str, new_value: Any):
        """
        Updates the item in the collection

        :param str key: Key of the updated item
        :param Any value: Value of the updated item
        :param str change_key: Key to be added or updated in the item
        :param Any new_value: New value to added or updated in the item of the change_key
        """
        self.col.update_one({key, value}, {"$set":{change_key:new_value}})