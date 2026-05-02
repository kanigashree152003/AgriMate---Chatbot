import re

# 🌾 English Knowledge Base
knowledge_base_en = {
    "hi": "Hello! I’m your Crop Doctor Assistant. You can upload a leaf photo or ask me about crop diseases.",
    "hello": "Vanakkam! I’m your Crop Doctor Assistant. How can I help you with your paddy crops today?",
    "good morning": "Good morning! Let’s keep your rice field healthy together!",
    "bye": "Goodbye! Take care of your crops and see you soon!",
    "thank you": "You're welcome! Keep your crops green and healthy.",

    "Bacterial Leaf Blight": (
        "Disease: Bacterial Leaf Blight\n"
        "Cause: Xanthomonas oryzae pv. oryzae\n"
        "Symptoms: Yellowing and drying of leaves from the tip downward.\n"
        "Control Measures:\n"
        " - Apply Copper oxychloride (2 g/litre)\n"
        " - Use resistant varieties\n"
        " - Spray Cow dung extract or Turmeric solution."
    ),

    "Brown Spot": (
        "Disease: Brown Spot\n"
        "Cause: Bipolaris oryzae\n"
        "Symptoms: Small brown circular spots on leaves.\n"
        "Control Measures:\n"
        " - Apply Mancozeb (2 g/litre)\n"
        " - Use resistant rice varieties\n"
        " - Spray Neem extract."
    ),

    "Leaf Blast": (
        "Disease: Leaf Blast\n"
        "Cause: Magnaporthe oryzae\n"
        "Symptoms: Diamond-shaped gray lesions appear on leaves.\n"
        "Control Measures:\n"
        " - Spray Tricyclazole (0.6 g/litre)\n"
        " - Apply Neem Oil 3% for organic management."
    ),

    "Leaf scald": (
        "Disease: Leaf Scald\n"
        "Cause: Xanthomonas albilineans (bacteria)\n"
        "Symptoms: White to gray lesions starting from the leaf tip.\n"
        "Control Measures:\n"
        " - Remove infected leaves\n"
        " - Avoid overhead irrigation\n"
        " - Use resistant varieties."
    ),

    "Sheath Blight": (
        "Disease: Sheath Blight\n"
        "Cause: Rhizoctonia solani\n"
        "Symptoms: Oval or irregular gray-green lesions on leaf sheaths.\n"
        "Control Measures:\n"
        " - Spray Validamycin (2 ml/litre)\n"
        " - Apply Pseudomonas fluorescens as bio-agent."
    ),

    "Healthy Rice Leaf": (
        "Your crop appears healthy! \n"
        " - Maintain proper irrigation\n"
        " - Ensure balanced fertilizer use\n"
        " - Regularly monitor for early disease symptoms."
    ),

    "default": (
        "Sorry, I don’t have data on that disease yet.\n"
        "Please upload a leaf image for diagnosis."
    )
}

# 🌾 Tamil Knowledge Base
knowledge_base_ta = {
    "hi": "வணக்கம்! நான் உங்க பயிர் டாக்டர் உதவியாளர். நீங்கள் ஒரு இலை புகைப்படம் பதிவேற்றலாம் அல்லது நோய்கள் பற்றி கேளுங்கள்.",
    "hello": "வணக்கம்! உங்க நெல் பயிருக்கு எப்படி உதவலாம்?",
    "bye": "பை! உங்க பயிர் நன்றாக வளரட்டும்!",
    "thank you": "நன்றி! உங்க நெல் பச்சையாகவும் ஆரோக்கியமாகவும் இருக்கட்டும்!",

    "Bacterial Leaf Blight": (
        "நோய்: நெல் பாக்டீரியா பிளைட்\n"
        "காரணம்: Xanthomonas oryzae pv. oryzae\n"
        "அறிகுறிகள்: இலை முனையில் இருந்து மஞ்சளாகி உலருதல்.\n"
        "தடுப்பு:\n"
        " - Copper oxychloride (2 g/l)\n"
        " - நோய் எதிர்ப்பு வகைகள்\n"
        " - பசும்பாலை அல்லது மஞ்சள் கரைசல் தெளிக்கவும்."
    ),

    "Brown Spot": (
        "நோய்: ப்ரவுன் ஸ்பாட்\n"
        "காரணம்: Bipolaris oryzae\n"
        "அறிகுறிகள்: இலைகளில் சிறிய பழுப்பு புள்ளிகள்.\n"
        "தடுப்பு:\n"
        " - Mancozeb (2 g/l)\n"
        " - வேப்பம் சாறு தெளிக்கவும்."
    ),

    "Leaf Blast": (
        "நோய்: நெல் இலை பிளாஸ்ட்\n"
        "காரணம்: Magnaporthe oryzae பூஞ்சை\n"
        "அறிகுறிகள்: வைரம் வடிவம் கொண்ட புள்ளிகள்.\n"
        "தடுப்பு:\n"
        " - Tricyclazole (0.6 g/l) தெளிக்கவும்\n"
        " - 3% வேப்பெண்ணெய் பயன்படுத்தவும்."
    ),

    "Leaf scald": (
        "நோய்: நெல் இலை ஸ்கால்ட்\n"
        "காரணம்: Xanthomonas albilineans (பாக்டீரியா)\n"
        "அறிகுறிகள்: இலை முனையில் இருந்து வெள்ளை நிற புள்ளிகள்.\n"
        "தடுப்பு:\n"
        " - பாதிக்கப்பட்ட இலைகளை அகற்றவும்\n"
        " - நீர் பாய்ச்சும் முறையை தவிர்க்கவும்\n"
        " - எதிர்ப்பு வகைகள் பயன்படுத்தவும்."
    ),

    "Sheath Blight": (
        "நோய்: ஷீத் பிளைட்\n"
        "காரணம்: Rhizoctonia solani\n"
        "அறிகுறிகள்: இலை அடிப்பகுதியில் சாம்பல் புள்ளிகள்.\n"
        "தடுப்பு:\n"
        " - Validamycin (2 ml/l) தெளிக்கவும்\n"
        " - Pseudomonas உயிரி மருந்து பயன்படுத்தவும்."
    ),

    "healthy rice leaf": (
        "உங்க நெல் பயிர் ஆரோக்கியமாக இருக்கிறது! 🌾\n"
        " - சரியான நீர் அளிப்பு\n"
        " - உரம் சரியாக கொடுக்கவும்\n"
        " - நோய் அறிகுறிகள் பார்த்து நடவடிக்கை எடுக்கவும்."
    ),

    "default": (
        "மன்னிக்கவும், அந்த நோய்க்கான தகவல் இல்லை.\n"
        "தயவுசெய்து இலை புகைப்படம் பதிவேற்றவும்."
    )
}

# 🌾 Tanglish Knowledge Base
knowledge_base_tanglish = {
    "hi": "Vanakkam! Naan unga Crop Doctor assistant. Neenga leaf photo upload pannalam.",
    "hello": "Vanakkam! Eppadi unga paddy ku help panna?",
    "bye": "Bye! Ungal field nalla valarattum.",
    "thank you": "Nandri! Unga crops pacha pacha valarattum.",

    "Bacterial Leaf Blight": (
        "Disease: Bacterial Leaf Blight\n"
        "Cause: Xanthomonas oryzae\n"
        "Symptoms: Leaf la tip la yellow aagi dry aagum.\n"
        "Control:\n"
        " - Copper oxychloride (2 g/l)\n"
        " - Resistant variety use pannunga."
    ),

    "Brown Spot": (
        "Disease: Brown Spot\n"
        "Cause: Bipolaris oryzae\n"
        "Symptoms: Small brown spots varum.\n"
        "Control:\n"
        " - Mancozeb (2 g/l)\n"
        " - Neem extract spray pannunga."
    ),

    "Leaf scald": (
        "Disease: Leaf Scald\n"
        "Cause: Xanthomonas albilineans\n"
        "Symptoms: Ila tip la white patch varum.\n"
        "Control:\n"
        " - Infected leaves remove pannunga\n"
        " - Water spray avoid pannunga."
    ),

    "Sheath Blight": (
        "Disease: Sheath Blight\n"
        "Cause: Rhizoctonia solani\n"
        "Symptoms: Ila keela gray spot varum.\n"
        "Control:\n"
        " - Validamycin (2 ml/l) spray pannunga."
    ),

    "default": (
        "Sorry, indha disease pathi info illa.\n"
        "Neenga leaf image upload pannunga."
    )
}

# 🌿 Image diagnosis helper messages
image_diagnosis = {
    "en": {
        "instruction": " Please upload a clear image of the rice leaf for disease diagnosis.",
        "success": " Image received. Analyzing the leaf...",
        "result_prefix": " Based on the image, the diagnosis result is:"
    },
    "ta": {
        "instruction": " நெல் இலை நோயை கண்டறிய தெளிவான புகைப்படத்தை பதிவேற்றவும்.",
        "success": " படம் கிடைத்தது. பகுப்பாய்வு செய்கிறேன்...",
        "result_prefix": " பதிவேற்றிய படத்தின் அடிப்படையில் நோய் முடிவு:"
    },
    "tg": {
        "instruction": " Nel leaf oda clear photo upload pannunga disease detect panna.",
        "success": " Image vandhachu. Leaf la disease iruka-nu check panren...",
        "result_prefix": " Image-based diagnosis result:"
    }
}


# 🌐 Language Detection
def detect_language(user_input: str) -> str:
    tamil_pattern = r'[\u0B80-\u0BFF]'
    if re.search(tamil_pattern, user_input):
        return "tamil"

    tanglish_keywords = ["vanakkam", "unga", "pannunga", "illa", "pathi", "aagum"]
    if any(word in user_input.lower() for word in tanglish_keywords):
        return "tanglish"

    return "english"

# 🧠 Unified Knowledge Base Access
def get_response(user_input: str) -> str:
    lang = detect_language(user_input)
    user_input = user_input.lower().strip()

    if lang == "tamil":
        kb = knowledge_base_ta
    elif lang == "tanglish":
        kb = knowledge_base_tanglish
    else:
        kb = knowledge_base_en

    for key in kb.keys():
        if key in user_input:
            return kb[key]

    return kb["default"]
