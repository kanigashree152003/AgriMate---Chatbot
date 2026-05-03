from pymongo import MongoClient
import certifi
from utils.knowledge_sync import knowledge_base_en  

# MongoDB Connection 
try:
    uri = "mongodb+srv://kani_15:kanigaravi@cluster30.c6fxhae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster30"
    client = MongoClient(uri, tlsCAFile=certifi.where())
    
    db = client["RiceCropDB"]               
    collection = db["Knowledge_base"]
    collection = db["Chat_History"]       
    print("MongoDB Connected Successfully!")

    # Check existing records to avoid duplicates
    existing_diseases = [doc["disease"] for doc in collection.find({}, {"disease": 1})]
    
    # Filter out duplicates before inserting
    new_records = [record for record in knowledge_base_en if record["disease"] not in existing_diseases]

    if new_records:
        collection.insert_many(new_records)
        print(f" Inserted {len(new_records)} new records into MongoDB.")
    else:
        print(" All records already exist. No new inserts needed.")

    # Print available collections
    print(" Collections:", db.list_collection_names())

except Exception as e:
    print(" MongoDB connection or insertion failed:", e)
