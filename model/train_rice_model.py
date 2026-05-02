# 🌾 train_rice_model.py — Train Rice Disease Detection Model

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import json
import os

# -----------------------------
# 🔧 CONFIGURATION
# -----------------------------
DATA_DIR = "Rice_Dataset_split"  # <-- your folder: dataset/train & dataset/valid
BATCH_SIZE = 16
EPOCHS = 20
LR = 0.0003
NUM_CLASSES = 6
MODEL_NAME = "rice_model.pth"

# -----------------------------
# 📦 DATASET PREPARATION
# -----------------------------
# 📦 DATASET PREPARATION
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

train_data = datasets.ImageFolder(root=os.path.join("Rice_Dataset_split", "train"), transform=transform_train)
val_data = datasets.ImageFolder(root=os.path.join("Rice_Dataset_split", "val"), transform=transform_val)


train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False)

print(" Class-to-Index Mapping:")
print(train_data.class_to_idx)

# Save class mapping for Flask app
with open("class_mapping.json", "w") as f:
    json.dump(train_data.class_to_idx, f)
print(" Saved class_mapping.json for Flask integration")

# -----------------------------
# 🧠 MODEL SETUP (ResNet18)
# -----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet18(pretrained=True)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, NUM_CLASSES)
model = model.to(device)

# -----------------------------
# ⚖️ HANDLE CLASS IMBALANCE
# -----------------------------
class_counts = np.bincount([label for _, label in train_data.samples])
class_weights = 1.0 / torch.tensor(class_counts, dtype=torch.float)
criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))

optimizer = optim.Adam(model.parameters(), lr=LR)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

# -----------------------------
# 🚀 TRAINING LOOP
# -----------------------------
train_losses, val_losses, val_accuracies = [], [], []

for epoch in range(EPOCHS):
    model.train()
    running_loss = 0.0

    for images, labels in tqdm(train_loader, desc=f"Epoch {epoch+1}/{EPOCHS}"):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()

        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    # Validation
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            val_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    epoch_train_loss = running_loss / len(train_loader)
    epoch_val_loss = val_loss / len(val_loader)
    accuracy = 100 * correct / total

    train_losses.append(epoch_train_loss)
    val_losses.append(epoch_val_loss)
    val_accuracies.append(accuracy)

    print(f" Epoch [{epoch+1}/{EPOCHS}] | Train Loss: {epoch_train_loss:.4f} | "
          f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {accuracy:.2f}%")

    scheduler.step()

# -----------------------------
# 💾 SAVE MODEL
# -----------------------------
torch.save(model.state_dict(), MODEL_NAME)
print(f"\n Model saved successfully as {MODEL_NAME}")

# -----------------------------
# 📈 PLOT RESULTS
# -----------------------------
plt.figure(figsize=(10,5))
plt.plot(train_losses, label="Train Loss")
plt.plot(val_losses, label="Val Loss")
plt.plot(val_accuracies, label="Val Accuracy (%)")
plt.title("Training & Validation Performance")
plt.xlabel("Epochs")
plt.legend()
plt.show()
