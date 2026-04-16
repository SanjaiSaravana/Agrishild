import torch
from torchvision import transforms, models
import torch.nn as nn
from PIL import Image
import io
import os

# Define the absolute path to the model file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Referencing the model from the "pest and disease" directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
MODEL_PATH = os.path.join(PROJECT_ROOT, "pest and disease", "plant_disease_model.pth")

DISEASE_INFO = {
    "Bacterial_Spot": {
        "pesticide": "Copper-based Fungicides (e.g., Kocide) or Streptomycin sulfate.",
        "fertilizer": "Balanced N-P-K (10-10-10) to boost plant immunity.",
        "directions": "Spray every 7-10 days during wet weather. Avoid overhead watering.",
        "color": "#ef4444" 
    },
    "Black_Measles": {
        "pesticide": "Lime Sulfur or Myclobutanil.",
        "fertilizer": "High Potassium (Potash) to strengthen vine wood.",
        "directions": "Prune out infected wood during dormancy and treat wounds with sealant.",
        "color": "#7c3aed"
    },
    "Black_Rot": {
        "pesticide": "Mancozeb, Captan, or Myclobutanil.",
        "fertilizer": "Organic compost to improve soil drainage.",
        "directions": "Remove 'mummified' fruit. Apply spray from 'pre-bloom' until fruit set.",
        "color": "#1e293b"
    },
    "Gray_Leaf_Spot": {
        "pesticide": "Strobilurin fungicides (e.g., Azoxystrobin).",
        "fertilizer": "Avoid excess Nitrogen; use slow-release Phosphorus.",
        "directions": "Improve air circulation. Rotate crops every 2 years.",
        "color": "#64748b"
    },
    "Healthy": {
        "pesticide": "None needed. Neem Oil can be used for prevention.",
        "fertilizer": "Organic liquid seaweed or compost tea.",
        "directions": "Maintain consistent watering at the base of the plant.",
        "color": "#22c55e"
    },
    "Powdery": {
        "pesticide": "Sulfur-based sprays or Potassium Bicarbonate.",
        "fertilizer": "Silica-based fertilizers to thicken leaf cell walls.",
        "directions": "Spray in the evening. Ensure plants have full sun exposure.",
        "color": "#94a3b8"
    },
    "Rust": {
        "pesticide": "Copper Fungicides or Myclobutanil.",
        "fertilizer": "Low Nitrogen, High Potassium fertilizer.",
        "directions": "Remove infected leaves immediately. Destroy infected debris.",
        "color": "#b45309"
    },
    "Scab": {
        "pesticide": "Dodine or Fenarimol fungicides.",
        "fertilizer": "Calcium Nitrate to support fruit development.",
        "directions": "Apply spray at 'green tip' stage and repeat every 10 days.",
        "color": "#854d0e"
    }
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(path=MODEL_PATH):
    if not os.path.exists(path):
        print(f"Model file NOT found at: {path}")
        return None, list(DISEASE_INFO.keys())
    
    try:
        checkpoint = torch.load(path, map_location=device)
        model = models.resnet18(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(checkpoint['class_names']))
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device).eval()
        print(f"Model loaded successfully from: {path}")
        return model, checkpoint['class_names']
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, list(DISEASE_INFO.keys())

# Load model globally for efficiency
model, class_names = load_model()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def get_treatment(predicted_name):
    predicted_name = predicted_name.upper().replace(" ", "_")
    for key in DISEASE_INFO.keys():
        if key.upper() in predicted_name:
            return DISEASE_INFO[key]
    return DISEASE_INFO["Healthy"]

async def predict_disease(image_bytes: bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = transform(img).unsqueeze(0).to(device)
        
        if model:
            with torch.no_grad():
                outputs = model(input_tensor)
                probabilities = torch.softmax(outputs, 1)
                conf, pred = torch.max(probabilities, 1)
                
                if conf.item() < 0.40:
                    return {
                        'disease': "Unclear Image",
                        'confidence': float(conf.item()),
                        'treatment': {"pesticide": "N/A", "fertilizer": "N/A", "directions": "The AI is unsure. Please take a clearer photo of the leaf."},
                        'status': 'unknown'
                    }
                
                raw_disease = class_names[pred.item()]
                confidence = conf.item()
        else:
            raw_disease, confidence = "Healthy", 1.0

        treatment = get_treatment(raw_disease)

        return {
            'disease': raw_disease.replace('_', ' '),
            'confidence': float(confidence),
            'treatment': treatment,
            'status': 'healthy' if 'healthy' in raw_disease.lower() else 'diseased'
        }
    except Exception as e:
        raise Exception(f"Prediction Error: {str(e)}")
