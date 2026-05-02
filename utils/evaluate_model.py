import os
import csv
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models, transforms, datasets
from PIL import Image
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------
# 🌾 Auto Path Detection
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "rice_model.pth")
TEST_DIR = os.path.join(os.path.dirname(BASE_DIR), "Rice_Dataset_split", "test")
OUTPUT_CSV = os.path.join(BASE_DIR, "predictions.csv")

# -----------------------------
# 🌾 Class Names (MUST match training order)
# -----------------------------
CLASSES = [
    'Bacterial Leaf Blight',
    'Brown Spot',
    'Healthy Rice Leaf',
    'Leaf Blast',
    'Leaf scald',
    'Sheath Blight'
]

# -----------------------------
# 🌾 Load Model
# -----------------------------
model = models.resnet18(weights="IMAGENET1K_V1")
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, len(CLASSES))
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()
print(f" Model loaded successfully from {MODEL_PATH}")

# -----------------------------
# 🌾 Transforms
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# -----------------------------
# 🌾 Evaluate on Test Folder
# -----------------------------
y_true = []
y_pred = []
results = []

for class_name in os.listdir(TEST_DIR):
    class_folder = os.path.join(TEST_DIR, class_name)
    if not os.path.isdir(class_folder):
        continue

    print(f"\n Processing class: {class_name}")

    for img_name in os.listdir(class_folder):
        img_path = os.path.join(class_folder, img_name)
        try:
            img = Image.open(img_path).convert('RGB')
            img = transform(img).unsqueeze(0)

            with torch.no_grad():
                outputs = model(img)
                probs = F.softmax(outputs, dim=1)[0]
                predicted_idx = torch.argmax(probs).item()
                predicted_class = CLASSES[predicted_idx]
                confidence = probs[predicted_idx].item() * 100

            y_true.append(class_name)
            y_pred.append(predicted_class)
            results.append([img_name, class_name, predicted_class, f"{confidence:.2f}%"])

        except Exception as e:
            print(f" Error processing {img_name}: {e}")

# -----------------------------
# 🌾 Save Results to CSV
# -----------------------------
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Image Name", "Actual Class", "Predicted Class", "Confidence"])
    writer.writerows(results)

print(f"\n Predictions saved to: {OUTPUT_CSV}")

# -----------------------------
# 🌾 Print Accuracy Summary
# -----------------------------
acc = accuracy_score(y_true, y_pred)
print(f"\n Overall Accuracy: {acc * 100:.2f}%")

print("\n Classification Report:")
print(classification_report(y_true, y_pred, target_names=CLASSES))
