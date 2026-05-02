from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import certifi
import numpy as np

# -------------------------------------------------------
# 🌿 MongoDB Connection
# -------------------------------------------------------
client = MongoClient(
    "mongodb+srv://kani_15:kanigaravi@cluster30.c6fxhae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster30",
    tlsCAFile=certifi.where()
)
db = client["RiceCropDB"]
kb_collection = db["Knowledge_base"]
emb_collection = db["Disease_Embeddings"]
chat_collection = db["Chat_History"]

# -------------------------------------------------------
# 💬 Store Chat Log in MongoDB
# -------------------------------------------------------
def log_chat(user_input, bot_response, lang="en", mode="text", prediction=None, confidence=None):
    try:
        chat_doc = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "language": lang,
            "mode": mode,  # 'text' or 'image'
            "bot_response": bot_response,
            "predicted_disease": prediction,
            "confidence": confidence
        }
        chat_collection.insert_one(chat_doc)
        print(f"🗂️ Chat saved: [{lang}] {user_input[:40]}...")
    except Exception as e:
        print("⚠️ Error saving chat:", e)

# -------------------------------------------------------
# 🧠 Load Sentence Transformer Model
# -------------------------------------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded successfully!")

# -------------------------------------------------------
# 🧩 Fetch All Disease Names
# -------------------------------------------------------
records = list(kb_collection.find({}, {"_id": 1, "disease": 1}))
print(f"🧠 Found {len(records)} disease records in Knowledge_base.")

# -------------------------------------------------------
# 💾 Generate and Store Embeddings in New Collection
# -------------------------------------------------------
emb_collection.delete_many({})  # Optional: clear previous entries

for record in records:
    disease_name = record.get("disease", "").strip()
    if not disease_name:
        continue

    embedding = model.encode(disease_name).tolist()

    emb_doc = {
        "disease_id": record["_id"],
        "disease": disease_name,
        "embedding_vector": embedding
    }

    emb_collection.insert_one(emb_doc)
    print(f"✅ Stored vector for: {disease_name}")

print("\n🎉 All disease embeddings stored in 'Disease_Embeddings' collection!")
