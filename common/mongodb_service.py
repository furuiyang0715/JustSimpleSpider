import logging

from pymongo import MongoClient, errors
from pymongo.collection import Collection
from pymongo.database import Database
MAX_POOL_SIZE = 5


logger = logging.getLogger()


def get_client(host: str, port: int) -> MongoClient:
    try:
        client = MongoClient(host, port, maxPoolSize=MAX_POOL_SIZE)
        # logger.debug("MongoClient Connected successfully.")
        return client
    except errors.ConnectionFailure as e:
        logger.warning("Create MongoClient Fail: {}".format(e))


def get_db(client: MongoClient, db_name: str) -> Database:
    try:
        db = Database(client, db_name)
        # logger.debug("MongoDB Connected successfully.")
        return db
    except Exception as e:
        logger.warning("Create MongoDB Fail: ".format(e))


def get_collection(db: Database, name: str) -> Collection:
    collection = Collection(db, name)
    # logger.debug("MongoCollection Connected successfully.")
    return collection


def insert(collection: Collection, data):
    collection.insert_one(data)


if __name__ == '__main__':
    mongo_client = get_client('127.0.0.1', 27017)
    db = get_db(mongo_client, "test")
    collection = get_collection(db, "test1")
    collection.drop()

    insert(collection, {"test": "helloworld"})
    print(list(collection.find({"test": "helloworld"})))
