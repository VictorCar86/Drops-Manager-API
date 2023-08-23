### MongoDB client ###

from pymongo import MongoClient

# Local Mongo DB
# db_client = MongoClient().local.

# Remote Mongo DB
uri = "mongodb+srv://droppsdb:tz6iT6cV4MBQn9kc@clustersoftonsteroids.np2zz29.mongodb.net/?retryWrites=true&w=majority"
db_client = MongoClient(uri).drops

# Send a ping to confirm a successful connection
def _ping_db():
    try:
        print("Pinging db deployment...")
        print(f"Response: {MongoClient(uri).admin.command('ping')}")
    except Exception as e:
        print(e)
