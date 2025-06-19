from pymongo import MongoClient
from django.conf import settings
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import os

load_dotenv()

# returning the collection in that mongodb database.
def getMongoConnection():
    # print("Printing mongoURL :",settings.MONGO_URL)
    client = MongoClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB_NAME]
    return db['logs']


# function which is storing log into mongodb.
def log_in_db(level, action, resource, details=None):
    logs_collection = getMongoConnection()
    log_entry = {
            "timestamp": datetime.now(),
            "level": level,
            "action": action,
            "resource": resource,
            "details": details or {}
        }

    logs_collection.insert_one(log_entry)




# function to delete logs in the database.
def delete_old_logs(hours):
    collection = getMongoConnection()
     # deletion_time = datetime.now() - relativedelta(months=int(months))
    deletion_time = datetime.now() - timedelta(hours=int(hours))

    logsCollection = list(collection.find({"timestamp": {"$lt": deletion_time}}))
    
    if not logsCollection:
        return "",0

    # converting it to json object correctly.
    for log in logsCollection:
        log["_id"] = str(log["_id"])
        log["timestamp"] = log["timestamp"].isoformat()

    backup_dir = os.path.join(settings.BASE_DIR, 'backup')
    os.makedirs(backup_dir, exist_ok=True)

    filename = f"logs_backup_{hours}_hours.json"
    file_path = os.path.join(backup_dir, filename)

    with open(file_path, 'w') as f:
        json.dump(logsCollection, f, indent=4)

    result = collection.delete_many({"timestamp": {"$lt": deletion_time}})
    
    return filename, result.deleted_count
