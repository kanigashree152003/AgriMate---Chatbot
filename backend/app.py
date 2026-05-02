from flask import Flask, render_template, request, jsonify, url_for
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
from pymongo import MongoClient
import certifi
import os, re, logging
from datetime import datetime
from deep_translator import GoogleTranslator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# -------------------------------------------------------
# 🌾 Flask Setup
# -------------------------------------------------------
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------------------------------
# 🪵 Logging Setup
# -------------------------------------------------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "chat_history.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------------------------------------------------------
# 🌿 MongoDB Setup
# -------------------------------------------------------
try:
    client = MongoClient(
        "mongodb+srv://kani_15:kanigaravi@cluster30.c6fxhae.mongodb.net/?retryWrites=true&w=majority&appName=Cluster30",
        tlsCAFile=certifi.where()
    )
    db = client["RiceCropDB"]
    collection = db["Knowledge_base"]
    collection = db["Chat_History"]
    print(" MongoDB connected successfully!")
except Exception as e:
    print(" MongoDB connection error:", e)
    collection = None

# -------------------------------------------------------
# 💬 Log Chat to MongoDB
# -------------------------------------------------------
def log_chat(user_input, bot_response, lang="en", mode="text", prediction=None, confidence=None):
    try:
        chat_doc = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "language": lang,
            "mode": mode,
            "bot_response": bot_response,
            "predicted_disease": prediction,
            "confidence": confidence
        }
        collection.insert_one(chat_doc)
        print(f" Chat logged — Mode: {mode.upper()}, Lang: {lang.upper()}, Prediction: {prediction}")
    except Exception as e:
        print(" Error saving chat:", e)

# -------------------------------------------------------
# 🌿 Load CNN Model (ResNet18)
# -------------------------------------------------------
def load_model(model_path):
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 6)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

model_path = "utils/rice_model.pth"
model = load_model(model_path)
CLASSES = [
    "Bacterial Leaf Blight",
    "Brown Spot",
    "Healthy Rice Leaf",
    "Leaf Blast",
    "Leaf Scald",
    "Sheath Blight"
]

# -------------------------------------------------------
# 🧠 Language Detection
# -------------------------------------------------------
def detect_language(text):
    tamil_pattern = r'[\u0B80-\u0BFF]'
    tanglish_keywords = ["unga", "pannunga", "aakum", "thanni", "nel", "sapdu", "vedippu", "vaadal", "pazhuppu"]
    if re.search(tamil_pattern, text):
        return "ta"
    elif any(word in text.lower() for word in tanglish_keywords):
        return "tg"
    return "en"

# -------------------------------------------------------
# 🌐 Semantic Model
# -------------------------------------------------------
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------------------------------------
# 🌿 Disease Info Fetch + Semantic Fallback
# -------------------------------------------------------
def get_disease_info(disease_name, lang="en"):
    if collection is None:
        print(" MongoDB collection not found.")
        return None

    try:
        disease_name = disease_name.strip().lower()

        # Tamil/Tanglish mapping
        tamil_tanglish_map = {
            "இலை வெடிப்பு": "Leaf Blast",
            "ilai vedippu": "Leaf Blast",
            "பாக்டீரியல் இலை வாடல்": "Bacterial Leaf Blight",
            "ilai vaadal": "Bacterial Leaf Blight",
            "பழுப்பு புள்ளி": "Brown Spot",
            "pazhuppu pulli": "Brown Spot",
            "இலை கறை": "Leaf Scald",
            "ilai karai": "Leaf Scald",
            "sheath": "Sheath Blight",
        }

        for key, val in tamil_tanglish_map.items():
            if key in disease_name:
                print(f" Matched Tamil/Tanglish keyword: {key} → {val}")
                disease_name = val
                break

        # Step 1: Direct match
        result = collection.find_one({"disease": {"$regex": disease_name, "$options": "i"}})

        # Step 2: Semantic fallback
        if not result:
            print(f" No direct match, running semantic fallback for '{disease_name}'")
            all_docs = list(collection.find({}, {"disease": 1}))
            disease_names = [doc.get("disease", "") for doc in all_docs]
            query_emb = semantic_model.encode([disease_name])
            disease_embs = semantic_model.encode(disease_names)
            sims = cosine_similarity(query_emb, disease_embs)[0]
            best_idx = np.argmax(sims)
            best_match = disease_names[best_idx]
            confidence = sims[best_idx] * 100
            print(f" Closest match: {best_match} ({confidence:.2f}% confidence)")
            result = collection.find_one({"disease": {"$regex": best_match, "$options": "i"}})

        if not result:
            return None

        # Step 3: Localized fields
        def get_field(field):
            field_map = {"ta": f"ta_{field}", "tg": f"tg_{field}"}
            return result.get(field_map.get(lang, field), result.get(field, "Not available"))

        return {
            "disease": get_field("disease"),
            "reason": get_field("reason"),
            "symptoms": get_field("symptoms"),
            "solution": get_field("solution"),
            "organic": get_field("organic"),
            "irrigation": get_field("irrigation"),
            "fertilizer": get_field("fertilizer")
        }

    except Exception as e:
        print(" Error fetching disease info:", e)
        return None

# -------------------------------------------------------
# 🌐 Translation Utility
# -------------------------------------------------------
def translate_response(response_text, lang):
    if lang == "ta":
        try:
            return GoogleTranslator(source="en", target="ta").translate(response_text)
        except:
            return response_text
    elif lang == "tg":
        tanglish = response_text
        tanglish = (
            tanglish.replace("Disease", "Noi")
                    .replace("Reason", "Kaaranam")
                    .replace("Solution", "Theervu")
                    .replace("Irrigation", "Thanni valaivu")
                    .replace("Fertilizer", "Uravu upayogam")
                    .replace("Organic", "Organic method")
        )
        return "Vanakkam! \n" + tanglish + "\nNalla morning la pannunga!"
    else:
        return response_text

# -------------------------------------------------------
# 🖼️ Image Prediction
# -------------------------------------------------------
def predict_disease(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    img = Image.open(image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        probs = F.softmax(outputs, dim=1)[0]
        _, predicted = torch.max(probs, 0)

    print("\n Confidence:")
    for i, cls in enumerate(CLASSES):
        print(f"   {cls}: {probs[i].item() * 100:.2f}%")

    return CLASSES[predicted.item()]

# -------------------------------------------------------
# 🏡 Routes
# -------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -------------------------------------------------------
# 💬 Text Chat
# -------------------------------------------------------
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input', '').strip()
    if not user_input:
        return jsonify({'response_html': "<p>தயவுசெய்து ஒரு செய்தி உள்ளிடுங்கள் / Please enter a message.</p>"})

    lang = detect_language(user_input)
    data = get_disease_info(user_input, lang)

    if not data:
        fallback = "I'm here to help with rice crop problems. Try describing symptoms or upload a leaf image."
        translated = translate_response(fallback, lang)
        log_chat(user_input, translated, lang=lang, mode="text")
        return jsonify({'response_html': f"<p>{translated}</p>"})

    response_text = (
        f"Disease: {data['disease']}\n"
        f"Reason: {data['reason']}\n"
        f"Symptoms: {data['symptoms']}\n"
        f"Solution: {data['solution']}\n"
        f"Organic: {data['organic']}\n"
        f"Irrigation: {data['irrigation']}\n"
        f"Fertilizer: {data['fertilizer']}"
    )

    translated = translate_response(response_text, lang)
    response_html = f"<pre style='color:#ffffff;white-space:pre-wrap;font-family:Poppins, sans-serif;'>{translated}</pre>"
    log_chat(user_input, response_html, lang=lang, mode="text", prediction=data['disease'])
    return jsonify({'response_html': response_html})

# -------------------------------------------------------
# 🖼️ Predict Image — Ask Language
# -------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'result': 'No image uploaded.', 'details_html': '', 'image_url': None})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'result': 'No file selected.', 'details_html': '', 'image_url': None})

    lang = request.form.get('lang', 'en').lower()
    filename = file.filename.replace(" ", "_")
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(image_path)

    prediction = predict_disease(image_path)
    image_url = url_for('static', filename=f'uploads/{filename}')

    with open("last_prediction.txt", "w", encoding="utf-8") as f:
        f.write(prediction)

    log_chat("Uploaded Image", f"Disease: {prediction}", lang=lang, mode="image", prediction=prediction)

    language_choice_html = f"""
    <div style='color:#00ff91;text-align:center;'>
         <b>Disease Detected:</b> {prediction}<br><br>
         <b>Please choose your preferred language for solution:</b><br><br>
        <button class='lang-btn' onclick="sendLanguageChoice('English')">🇬🇧 English</button>
        <button class='lang-btn' onclick="sendLanguageChoice('Tamil')">🇮🇳 தமிழ்</button>
        <button class='lang-btn' onclick="sendLanguageChoice('Tanglish')"> Tanglish</button>
    </div>
    """

    return jsonify({
        'result': f"<b>Disease Detected: {prediction}</b>",
        'details_html': language_choice_html,
        'image_url': image_url
    })

# -------------------------------------------------------
# 🗣️ Image Solution (Based on Language)
# -------------------------------------------------------
@app.route('/image_response', methods=['POST'])
def image_response():
    user_choice = request.form.get('user_input', '').strip().lower()

    if not os.path.exists("last_prediction.txt"):
        return jsonify({'response_html': "<p> No recent image detected. Please upload again.</p>"})
    with open("last_prediction.txt", "r", encoding="utf-8") as f:
        prediction = f.read().strip()

    if "tam" in user_choice or "தமிழ்" in user_choice:
        lang = "ta"
    elif "tanglish" in user_choice:
        lang = "tg"
    else:
        lang = "en"

    data = get_disease_info(prediction, lang)
    if not data:
        return jsonify({'response_html': "<p>No details found for this disease.</p>"})

    response_text = (
        f"Disease: {data['disease']}\n"
        f"Reason: {data['reason']}\n"
        f"Symptoms: {data['symptoms']}\n"
        f"Solution: {data['solution']}\n"
        f"Organic: {data['organic']}\n"
        f"Irrigation: {data['irrigation']}\n"
        f"Fertilizer: {data['fertilizer']}"
    )

    translated = translate_response(response_text, lang)
    response_html = f"<pre style='color:#ffffff;white-space:pre-wrap;font-family:Poppins, sans-serif;'>{translated}</pre>"

    log_chat(
        user_input=f"Language selected: {user_choice}",
        bot_response=response_html,
        lang=lang,
        mode="image",
        prediction=prediction
    )

    return jsonify({'response_html': response_html})

# -------------------------------------------------------
# 🚀 Run Flask App
# -------------------------------------------------------
if __name__ == '__main__':
    print(" AgriMate Chatbot running → http://127.0.0.1:5000")
    app.run(debug=True)
