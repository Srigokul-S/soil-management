from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional
import joblib
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(__file__))
from logic.fertilizer import calculate_fertilizer
from logic.soil_correction import get_soil_corrections
from logic.llm_provider import generate_advisory

app = FastAPI(title="AI Soil Health Advisory System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the client directory
# Note: Ensure the path is correct relative to main.py
client_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client')
app.mount("/site", StaticFiles(directory=client_path, html=True), name="client")

# Seasonal Crop Classification (India - UPAg Official)
KHARIF_CROPS = {
    'rice', 'maize', 'pigeonpeas', 'mothbeans', 'mungbean', 
    'blackgram', 'groundnut', 'soybean', 'cotton', 'jute', 
    'turmeric', 'sesame', 'sugarcane', 'jowar', 'bajra', 'ragi'
}
RABI_CROPS = {
    'wheat', 'barley', 'chickpea', 'lentil', 'mustard', 
    'linseed', 'peas', 'potato', 'coriander', 'cumin', 'oats'
}
ZAID_CROPS = {
    'watermelon', 'muskmelon', 'cucumber', 'pumpkin', 
    'bitter gourd', 'moong', 'fodder crops', 'sunflower'
}

# Extra Crop Data for Rules-Engine (Official APY Data Integration)
EXTRA_CROP_DATA = [
    {"name": "Wheat", "season": "Rabi", "category": "Food Grain", "cost": "Medium", "min_temp": 12, "max_temp": 25, "min_ph": 6.0, "max_ph": 7.5, "n": 100, "p": 50, "k": 40},
    {"name": "Sugarcane", "season": "Kharif", "category": "Commercial", "cost": "High", "min_temp": 20, "max_temp": 35, "min_ph": 5.0, "max_ph": 8.5, "n": 120, "p": 80, "k": 60},
    {"name": "Mustard", "season": "Rabi", "category": "Oilseed", "cost": "Low", "min_temp": 10, "max_temp": 25, "min_ph": 6.0, "max_ph": 7.5, "n": 80, "p": 40, "k": 40},
    {"name": "Bajra", "season": "Kharif", "category": "Food Grain", "cost": "Low", "min_temp": 25, "max_temp": 35, "min_ph": 5.5, "max_ph": 7.5, "n": 40, "p": 40, "k": 20},
    {"name": "Jowar", "season": "Kharif", "category": "Food Grain", "cost": "Low", "min_temp": 25, "max_temp": 32, "min_ph": 6.0, "max_ph": 7.5, "n": 60, "p": 40, "k": 30},
    {"name": "Barley", "season": "Rabi", "category": "Food Grain", "cost": "Medium", "min_temp": 15, "max_temp": 20, "min_ph": 6.0, "max_ph": 7.5, "n": 60, "p": 30, "k": 20},
    {"name": "Ginger", "season": "Kharif", "category": "Commercial", "cost": "High", "min_temp": 20, "max_temp": 28, "min_ph": 6.0, "max_ph": 6.5, "n": 75, "p": 50, "k": 50},
    {"name": "Tobacco", "season": "Rabi", "category": "Money", "cost": "High", "min_temp": 20, "max_temp": 30, "min_ph": 5.5, "max_ph": 6.5, "n": 100, "p": 50, "k": 80},
    {"name": "Potato", "season": "Rabi", "category": "Food", "cost": "Medium", "min_temp": 15, "max_temp": 20, "min_ph": 5.0, "max_ph": 6.5, "n": 120, "p": 100, "k": 120},
    {"name": "Soybean", "season": "Kharif", "category": "Oilseed", "cost": "Medium", "min_temp": 15, "max_temp": 30, "min_ph": 6.0, "max_ph": 7.5, "n": 20, "p": 60, "k": 40}
]

# Perennial or multi-season
PERENNIAL_CROPS = {'banana', 'pomegranate', 'mango', 'grapes', 'apple', 'orange', 'papaya', 'coconut', 'coffee', 'rubber'}

# Cost tags per crop
CROP_COST_MAP = {
    'rice': 'Medium', 'maize': 'Medium', 'chickpea': 'Low', 'kidneybeans': 'Low',
    'pigeonpeas': 'Low', 'mothbeans': 'Low', 'mungbean': 'Low', 'blackgram': 'Low',
    'lentil': 'Low', 'pomegranate': 'High', 'banana': 'Medium', 'mango': 'High',
    'grapes': 'High', 'watermelon': 'Medium', 'muskmelon': 'Medium', 'apple': 'High',
    'orange': 'Medium', 'papaya': 'Medium', 'coconut': 'Medium', 'cotton': 'Medium',
    'jute': 'Low', 'coffee': 'High', 'wheat': 'Medium', 'sugarcane': 'High',
    'mustard': 'Low', 'groundnut': 'Medium', 'soybean': 'Medium', 'millets': 'Low',
    'turmeric': 'Medium', 'ginger': 'Medium', 'tobacco': 'High', 'rubber': 'High'
}

# Load model at startup
model_path = os.path.join(os.path.dirname(__file__), 'crop_model.joblib')
labels_path = os.path.join(os.path.dirname(__file__), 'labels.joblib')

MODEL = None
LABELS = None

def load_model():
    global MODEL, LABELS
    if os.path.exists(model_path) and os.path.exists(labels_path):
        MODEL = joblib.load(model_path)
        LABELS = joblib.load(labels_path)
        print("Model loaded successfully.")
    else:
        print("Model not found. Run train_model.py first.")

load_model()


class SoilInput(BaseModel):
    nitrogen: float = Field(..., ge=0, le=140, description="N value")
    phosphorus: float = Field(..., ge=0, le=145, description="P value")
    potassium: float = Field(..., ge=0, le=205, description="K value")
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    moisture: float = Field(..., ge=0, le=100, description="Soil moisture %")
    soil_type: str
    location: Optional[str] = "India"
    season: str
    water_availability: str
    preferred_crop: Optional[str] = None
    land_area: float = Field(..., gt=0)
    land_unit: str
    language: str = "English"
    temperature: float = Field(default=25.0, ge=0, le=50)
    humidity: float = Field(default=60.0, ge=0, le=100)
    rainfall: float = Field(default=100.0, ge=0, le=500)


@app.get("/")
def root():
    return {"message": "AI Soil Health Advisory System API is running."}


@app.post("/predict")
def predict(data: SoilInput):
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Run train_model.py first.")

    features = np.array([[
        data.nitrogen, data.phosphorus, data.potassium,
        data.temperature, data.humidity, data.ph, data.rainfall
    ]])

    proba = MODEL.predict_proba(features)[0]
    class_labels = MODEL.classes_

    # Build ranked crop list
    ranked = sorted(zip(class_labels, proba), key=lambda x: x[1], reverse=True)
    top_crops = ranked[:10]  # Increased to 10 for more variety

    def get_color(score):
        if score >= 75: return "green"
        elif score >= 50: return "yellow"
        return "red"

    crops = []
    for name, prob in top_crops:
        name_lower = name.lower()
        score = round(prob * 100, 1)
        
        # Season compatibility check
        is_oob = False
        if data.season == "Kharif" and name_lower in RABI_CROPS: is_oob = True
        elif data.season == "Rabi" and name_lower in KHARIF_CROPS: is_oob = True
        elif data.season == "Zaid" and name_lower not in ZAID_CROPS and name_lower not in PERENNIAL_CROPS: is_oob = True
        
        # Penalize score slightly if off-season but still high prob
        if is_oob: score *= 0.8
        
        # Determine season type for categorization
        season_type = "Perennial"
        if name_lower in KHARIF_CROPS: season_type = "Kharif"
        elif name_lower in RABI_CROPS: season_type = "Rabi"
        elif name_lower in ZAID_CROPS: season_type = "Zaid"
        
        # Determine category for display
        category = "Food"
        if name_lower in {'rice', 'maize', 'wheat', 'barley'}: category = "Food Grain"
        elif name_lower in {'cotton', 'jute', 'sugarcane'}: category = "Commercial"
        elif name_lower in {'coffee', 'tea'}: category = "Money"
        
        crops.append({
            "name": name.capitalize(),
            "score": round(score, 1),
            "color": get_color(score),
            "cost": CROP_COST_MAP.get(name_lower, "Medium"),
            "is_seasonal": not is_oob or name_lower in PERENNIAL_CROPS,
            "season_type": season_type,
            "category": category
        })

    # 3. Add Extra Crops (Rule-Based)
    for extra in EXTRA_CROP_DATA:
        # Simple match calculation
        match_score = 100
        if not (extra["min_temp"] <= data.temperature <= extra["max_temp"]): match_score -= 20
        if not (extra["min_ph"] <= data.ph <= extra["max_ph"]): match_score -= 20
        if data.season != extra["season"]: match_score -= 50
        
        # NPK similarity check (simplified)
        n_diff = abs(extra["n"] - data.nitrogen) / extra["n"]
        match_score -= (n_diff * 10)
        
        final_score = max(5, min(95, match_score)) # Cap rule-based logic to 95%
        
        crops.append({
            "name": extra["name"],
            "score": round(final_score, 1),
            "color": get_color(final_score),
            "cost": extra["cost"],
            "is_seasonal": data.season == extra["season"],
            "season_type": extra["season"],
            "category": extra["category"]
        })

    # Final Rank across all sources
    crops = sorted(crops, key=lambda x: x['score'], reverse=True)[:10]

    # Fertilizer
    fertilizer = calculate_fertilizer(data.land_area, data.land_unit)

    # Soil correction
    corrections = get_soil_corrections(data.ph, data.soil_type, data.moisture)

    # LLM Advisory
    advisory = generate_advisory(crops, fertilizer, corrections, data.language, data.season, data.preferred_crop)

    return {
        "crops": crops,
        "fertilizer": fertilizer,
        "soil_correction": corrections,
        "advisory": advisory
    }
