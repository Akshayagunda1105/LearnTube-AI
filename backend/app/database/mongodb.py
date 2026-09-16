from pymongo import MongoClient


MONGO_URI = "mongodb://127.0.0.1:27017"

client = MongoClient(MONGO_URI)

database = client["learntube_ai"]


def check_mongodb_connection():
    """
    Check whether MongoDB is reachable.
    """

    client.admin.command("ping")

    return True