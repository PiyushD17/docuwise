import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
print("Connecting to:", MONGO_URI)

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in the environment.")

client = MongoClient(MONGO_URI)
db = client["docuwise"]
metadata_collection = db["file_metadata"]


def save_metadata(metadata: dict) -> None:
    metadata_collection.insert_one(metadata)
