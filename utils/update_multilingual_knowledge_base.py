# ------------------------------------------------------------
# 🌾 AgriMate Knowledge Base Multilingual Updater
# Automatically creates Tamil (ta) and Tanglish (tg) versions
# for each disease record in MongoDB Knowledge_base
# ------------------------------------------------------------

from pymongo import MongoClient
from deep_translator import GoogleTranslator
import certifi
import time

# ------------------------------------------------------------
# 🔗 MongoDB Connection
# ------------------------------------------------------------
client = MongoClient(
    "mongodb+srv://kani_15:kanigaravi@cluster30.c6fxhae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster30",
    tlsCAFile=certifi.where()
)
db = client["RiceCropDB"]
collection = db["Knowledge_base"]

print("✅ Connected to MongoDB — RiceCropDB / Knowledge_base")

# ------------------------------------------------------------
# 💬 Helper Function — Convert English to Tanglish
# ------------------------------------------------------------
def english_to_tanglish(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    tanglish_map = {
        "rice": "nel", "leaf": "ilai", "disease": "noi", "solution": "theervu",
        "spray": "spray pannunga", "water": "thanni", "use": "use pannunga",
        "avoid": "avoid pannunga", "fertilizer": "uruvagam", "cow": "maadu",
        "mixture": "mix", "apply": "apply pannunga", "yellow": "manjal", "dry": "vada"
    }
    for en, tg in tanglish_map.items():
        text = text.replace(en, tg).replace(en.capitalize(), tg.capitalize())
    return text

# ------------------------------------------------------------
# 🔁 Update Each Record
# ------------------------------------------------------------
records = list(collection.find())
print(f"🧠 Found {len(records)} knowledge base entries.\n")

for record in records:
    disease = record.get("disease", "Unknown")
    print(f"🌿 Processing: {disease}")

    try:
        update_fields = {}
        # Translate key fields into Tamil
        for field in ["disease", "reason", "symptoms", "solution", "organic", "irrigation", "fertilizer"]:
            text = record.get(field, "")
            if text:
                # Tamil translation
                ta_value = GoogleTranslator(source="en", target="ta").translate(text)
                update_fields[f"ta_{field}"] = ta_value

                # Tanglish (phonetic-style)
                tg_value = english_to_tanglish(text)
                update_fields[f"tg_{field}"] = tg_value

                time.sleep(0.5)  # rate-limit Google Translate API slightly

        # Update record
        collection.update_one({"_id": record["_id"]}, {"$set": update_fields})
        print(f"✅ Updated Tamil & Tanglish fields for: {disease}\n")

    except Exception as e:
        print(f"❌ Error translating {disease}: {e}\n")

print("🎉 All records updated successfully with Tamil and Tanglish fields!")
