from pymongo import MongoClient


class DBConnection:
    def __init__(self, host: str = 'localhost', port: int = 27017, dbName: str = 'ency'):
        self.client = MongoClient(host, port)
        self.db = self.client[dbName]

    def get_collection_names(self):
        return self.db.list_collection_names()

    def get_collection_data(self, collectionName: str, fields: list, amount: int = 200):
        collection = self.db[collectionName]
        existed_fields = collection.find_one().keys()
        query = {field: (1 if field in fields else 0) for field in existed_fields}
        return collection.find({}, {'_id': 0}).limit(amount)

    def close(self):
        self.client.close()
