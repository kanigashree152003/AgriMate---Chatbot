# ------------------------------------------------------------
# 🌿 AgriMate Auto-Updater for Multilingual Knowledge Base
# Checks MongoDB for new English-only entries and
# automatically adds Tamil (ta_) and Tanglish (tg_) fields.
# ------------------------------------------------------------

from pymongo import MongoClient
from deep_translator import GoogleTranslator
import certifi
import time
from datetime import datetime

# ------------------------------------------------------------
# 🔗 MongoDB Connection
# ------------------------------------------------------------
client = MongoClient(
    "mongodb+srv://kani_15:kanigaravi@cluster30.c6fxhae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster30",
    tlsCAFile=certifi.where()
)
db = client["RiceCropDB"]
collection = db["Knowledge_base"]

print("✅ Connected to MongoDB — RiceCropDB / Knowledge_base\n")

# ------------------------------------------------------------
# 💬 Helper: Convert English → Tanglish
# ------------------------------------------------------------
def english_to_tanglish(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    tanglish_map = {
        "rice": "nel", "leaf": "ilai", "disease": "noi", "solution": "theervu",
        "spray": "spray pannunga", "water": "thanni", "use": "use pannunga",
        "avoid": "avoid pannunga", "fertilizer": "uruvagam", "cow": "maadu",
        "mixture": "mix", "apply": "apply pannunga", "yellow": "manjal", "dry": "vada",
        "infection": "noi", "remove": "remove pannunga", "balance": "balance pannunga"
    }
    for en, tg in tanglish_map.items():
        text = text.replace(en, tg).replace(en.capitalize(), tg.capitalize())
    return text

# ------------------------------------------------------------
# 🧠 Function to update multilingual fields for new records
# ------------------------------------------------------------
def update_new_records():
    updated_count = 0
    all_records = list(collection.find())

    for record in all_records:
        disease = record.get("disease", "Unknown")
        update_fields = {}

        # ✅ Skip if Tamil fields already exist
        if any(k.startswith("ta_") for k in record.keys()):
            continue

        print(f"🌿 New English-only record found → Translating: {disease}")

        try:
            for field in ["disease", "reason", "symptoms", "solution", "organic", "irrigation", "fertilizer"]:
                text = record.get(field, "")
                if text:
                    # Translate into Tamil
                    ta_value = GoogleTranslator(source="en", target="ta").translate(text)
                    update_fields[f"ta_{field}"] = ta_value

                    # Generate Tanglish
                    tg_value = english_to_tanglish(text)
                    update_fields[f"tg_{field}"] = tg_value

                    time.sleep(0.5)  # gentle rate-limit

            if update_fields:
                collection.update_one({"_id": record["_id"]}, {"$set": update_fields})
                updated_count += 1
                print(f"✅ Added Tamil & Tanglish fields for: {disease}\n")

        except Exception as e:
            print(f"❌ Error processing {disease}: {e}\n")

    print(f"🎉 Update complete — {updated_count} new records enriched.")
    print(f"🕒 Last run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ------------------------------------------------------------
# 🚀 Run as a continuous auto-checker (every 10 minutes)
# ------------------------------------------------------------
if __name__ == "__main__":
    print("🔁 Starting multilingual auto-updater...")
    while True:
        update_new_records()
        print("⏳ Waiting 10 minutes before next check...\n")
        time.sleep(600)  # 10 minutes
