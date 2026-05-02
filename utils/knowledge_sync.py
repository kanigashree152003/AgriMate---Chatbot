import re
from pymongo import MongoClient
import certifi

# 🌾 --- MONGO CONNECTION ---
def get_mongo_connection():
    """Connect to MongoDB Atlas (secured)"""
    try:
        # ⚠️ Update with your actual credentials
        uri = "mongodb+srv://kani_15:<kanigaravi>@cluster30.c6fxhae.mongodb.net/?appName=Cluster30"
        client = MongoClient(uri, tlsCAFile=certifi.where())
        db = client["RiceCropDB"]
        collection = db["Knowledge_base"]
        print("✅ Connected to MongoDB Atlas successfully.")
        return collection
    except Exception as e:
        print("❌ MongoDB connection error:", e)
        return None


# 🌾 --- ENGLISH KNOWLEDGE BASE (Structured) ---
knowledge_base_en = [
    {
        "language": "en",
        "disease": "Bacterial Leaf Blight",
        "reason": "Caused by bacterium Xanthomonas oryzae pv. oryzae; spreads via irrigation water and rain.",
        "symptoms": "Yellowing and drying of leaves from the tip downward forming a V-shape.",
        "solution": "Spray Copper oxychloride 2g/L or Streptocycline 0.1g/L. Use resistant varieties like ADT 43.",
        "organic": "Spray cow dung extract or turmeric + neem leaf mixture.",
        "irrigation": "Avoid standing water and improve drainage.",
        "fertilizer": "Avoid excess nitrogen; use balanced NPK (60:40:40)."
    },
    {
        "language": "en",
        "disease": "Brown Spot",
        "reason": "Caused by Bipolaris oryzae fungus thriving in humid, nutrient-deficient conditions.",
        "symptoms": "Brown circular spots with yellow halos on leaves.",
        "solution": "Spray Mancozeb 2g/L or Carbendazim 1g/L; use resistant varieties.",
        "organic": "Apply neem oil 3% or garlic extract spray.",
        "irrigation": "Avoid excess water; maintain alternate wetting and drying.",
        "fertilizer": "Increase potash fertilizer to strengthen leaves."
    },
    {
        "language": "en",
        "disease": "Leaf Blast",
        "reason": "Caused by fungus Magnaporthe oryzae; common in cool, humid climates.",
        "symptoms": "Diamond-shaped lesions with brown margins and gray centers.",
        "solution": "Spray Tricyclazole 0.6g/L or Isoprothiolane 1ml/L.",
        "organic": "Apply neem cake or panchagavya 3% every 10 days.",
        "irrigation": "Avoid drought; keep shallow standing water.",
        "fertilizer": "Split nitrogen doses; add silica-based fertilizers."
    },
    {
        "language": "en",
        "disease": "Leaf Scald",
        "reason": "Caused by bacteria Xanthomonas albilineans; spreads through infected seeds.",
        "symptoms": "White or gray lesions appear from leaf tip and edges.",
        "solution": "Use certified seeds, remove infected leaves, and apply Copper hydroxide 2g/L.",
        "organic": "Spray neem extract (5%) or turmeric extract weekly.",
        "irrigation": "Avoid overhead irrigation; maintain clean field channels.",
        "fertilizer": "Apply phosphorus-rich fertilizers for root strength."
    },
    {
        "language": "en",
        "disease": "Sheath Blight",
        "reason": "Caused by soil-borne fungus Rhizoctonia solani; spreads through contact between plants.",
        "symptoms": "Gray-green oval lesions on leaf sheaths merging in humid conditions.",
        "solution": "Spray Validamycin 2ml/L or Hexaconazole 1ml/L.",
        "organic": "Apply Pseudomonas fluorescens 10g/L as bio-agent.",
        "irrigation": "Avoid dense planting; use alternate wetting and drying.",
        "fertilizer": "Reduce nitrogen application during infection."
    },
    {
        "language": "en",
        "disease": "Healthy Rice Leaf",
        "reason": "No disease detected. Leaf appears healthy.",
        "symptoms": "Green uniform leaves, no lesions.",
        "solution": "Continue monitoring and proper irrigation.",
        "organic": "Apply compost and neem cake to enrich soil.",
        "irrigation": "Maintain 2-3 cm water depth.",
        "fertilizer": "Balanced NPK as per soil test."
    }
]


# 🌿 Tamil Knowledge Base
knowledge_base_ta = [
    {
        "language": "ta",
        "disease": "பாக்டீரியா பிளைட்",
        "reason": "Xanthomonas oryzae பாக்டீரியா காரணமாக ஏற்படும்.",
        "symptoms": "இலை முனையில் இருந்து மஞ்சளாகி உலருதல்.",
        "solution": "Copper oxychloride (2 g/L) தெளிக்கவும்.",
        "organic": "பசும்பாலை அல்லது வேப்பிலை கரைசல் தெளிக்கவும்.",
        "irrigation": "நீர் தேங்கவிடாதீர்கள்.",
        "fertilizer": "நைட்ரஜன் உரம் அளவை குறைக்கவும்."
    },
    {
        "language": "ta",
        "disease": "ப்ரவுன் ஸ்பாட்",
        "reason": "Bipolaris oryzae பூஞ்சை காரணமாக ஏற்படுகிறது.",
        "symptoms": "இலைகளில் பழுப்பு புள்ளிகள்.",
        "solution": "Mancozeb (2 g/L) தெளிக்கவும்.",
        "organic": "வேப்பெண்ணெய் தெளிக்கவும்.",
        "irrigation": "அதிக நீர் தவிர்க்கவும்.",
        "fertilizer": "பொட்டாசியம் நிறைந்த உரம் கொடுக்கவும்."
    }
]


# 🌾 Tanglish Knowledge Base
knowledge_base_tg = [
    {
        "language": "tg",
        "disease": "Bacterial Leaf Blight",
        "reason": "Xanthomonas oryzae bacteria cause pannum. Water la spread aagum.",
        "symptoms": "Leaf tip la yellow aagum, dry aagum.",
        "solution": "Copper oxychloride 2g/L spray pannunga.",
        "organic": "Neem leaf extract use pannunga.",
        "irrigation": "Water stagnation avoid pannunga.",
        "fertilizer": "Balanced fertilizer apply pannunga."
    }
]


# 🌾 --- LANGUAGE DETECTION ---
def detect_language(user_input: str) -> str:
    tamil_pattern = r'[\u0B80-\u0BFF]'
    if re.search(tamil_pattern, user_input):
        return "ta"
    elif any(word in user_input.lower() for word in ["vanakkam", "pannunga", "thanni", "nel", "sapdu"]):
        return "tg"
    return "en"


# 🌾 --- UNIFIED RESPONSE RETRIEVAL ---
def get_response(user_input: str):
    lang = detect_language(user_input)
    user_input_lower = user_input.lower()

    kb = knowledge_base_en
    if lang == "ta":
        kb = knowledge_base_ta
    elif lang == "tg":
        kb = knowledge_base_tg

    for entry in kb:
        if entry["disease"].lower() in user_input_lower:
            return entry

    return {
        "disease": "Unknown",
        "reason": "No data found.",
        "symptoms": "Please upload image for diagnosis.",
        "solution": "N/A",
        "organic": "N/A",
        "irrigation": "N/A",
        "fertilizer": "N/A"
    }


# 🌾 --- MONGO SYNC FUNCTION (Fixed) ---
def sync_to_mongo():
    """Uploads local knowledge base data to MongoDB safely"""
    collection = get_mongo_connection()
    if collection is None:
        print("❌ MongoDB connection failed. Could not sync data.")
        return

    # ✅ Handle empty collections safely
    try:
        existing_diseases = [
            doc.get("disease") for doc in collection.find({}, {"disease": 1})
            if "disease" in doc
        ]
    except Exception as e:
        print(f"⚠️ Error reading collection: {e}")
        existing_diseases = []

    # Combine all language entries
    all_entries = knowledge_base_en + knowledge_base_ta + knowledge_base_tg
    added = 0

    for entry in all_entries:
        if entry["disease"] not in existing_diseases:
            collection.insert_one(entry)
            added += 1

    print(f"🌿 Knowledge base sync complete → {added} new records added to MongoDB.")


# 🚀 MAIN EXECUTION
if __name__ == "__main__":
    sync_to_mongo()
