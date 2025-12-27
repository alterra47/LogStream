from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client.logstream_db

logs_collection = db.logs

def get_db_status():
  try:
    client.admin.command('ping')
    return True
  except Exception:
    return False
