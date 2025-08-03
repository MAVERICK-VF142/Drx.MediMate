from flask import current_app

def get_health_data():
    """Fetch all health data records from the MongoDB collection."""
    mongo = current_app.mongo
    return list(mongo.db.health_data.find())

def add_health_data(data):
    """Insert a new health data record into the MongoDB collection."""
    mongo = current_app.mongo
    mongo.db.health_data.insert_one(data)
