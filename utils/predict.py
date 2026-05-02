import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models
from PIL import Image
import os
from knowledge_base import get_response
from knowledge_base import knowledge_base_en, knowledge_base_ta, knowledge_base_tanglish
# ------------------------
# MODEL DEFINITION (ResNet18)
# ------------------------
def load_model(model_path):
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 6)  # ✅ 6 output classes
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

model = load_model("rice_model.pth")

# ------------------------
# CLASS DEFINITIONS
# ------------------------
CLASSES = [
    'Bacterial Leaf Blight',
    'Brown Spot',
    'Healthy Rice Leaf',
    'Leaf Blast',
    'Leaf scald',
    'Sheath Blight'
]

# ------------------------
# IMAGE PREDICTION FUNCTION
# ------------------------
def predict_disease(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])

    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img)
        probs = F.softmax(outputs, dim=1)[0]
        _, predicted = torch.max(probs, 0)

    print("\n Model confidence per class:")
    for i, cls in enumerate(CLASSES):
        print(f"{cls}: {probs[i].item() * 100:.2f}%")

    disease = CLASSES[predicted.item()]
    info = get_response(disease.lower())
    return disease

# ------------------------
# KNOWLEDGE BASE LOADER
# ------------------------
def load_knowledge_base():
    return {
        "en": knowledge_base_en,
        "ta": knowledge_base_ta,
        "tg": knowledge_base_tanglish
    }

# ------------------------
# IMAGE CHAT RESPONSE (USED BY FLASK)
# ------------------------
def handle_image_input(image_path):
    disease_name = predict_disease(image_path)
    info = get_response(disease_name.lower())
    return {
        "disease": disease_name,
        "details": info
    }

# ------------------------
# TEXT CHAT RESPONSE
# ------------------------
def chatbot_response(user_input):
    user_input = user_input.lower()

    if "hi" in user_input or "hello" in user_input:
        return "Hi! I’m your Crop Doctor Assistant . You can upload an image to detect rice disease."
    elif "help" in user_input:
        return "You can upload a rice leaf image for diagnosis or ask about irrigation and fertilizers."
    elif "disease" in user_input:
        return "Please upload a rice leaf image for disease detection."
    elif "thank" in user_input:
        return "You're welcome! Keep your crops green and healthy."
    else:
        return "I'm not sure about that yet . Try uploading a leaf image for diagnosis."
