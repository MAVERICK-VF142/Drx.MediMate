from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI and database name
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# Validate environment variables
if not MONGO_URI or not DB_NAME:
    raise ValueError("Missing MONGO_URI or DB_NAME in .env file")

# Create MongoDB client and database
client = MongoClient(MONGO_URI)
mongo = client[DB_NAME]  # ✅ Export this for use across backend routes
