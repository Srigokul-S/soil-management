import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

# Crop labels (representing most common Indian crops from Kaggle dataset)
CROP_LABELS = [
    'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
    'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
    'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 'apple',
    'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'
]

def generate_synthetic_data(samples_per_crop=100):
    """
    Generates synthetic soil data that mimics the Kaggle Crop Recommendation dataset.
    Features: N, P, K, temperature, humidity, ph, rainfall
    """
    data = []
    
    # Ranges are roughly based on historical crop suitability data
    ranges = {
        'rice': {'N': (60, 100), 'P': (35, 60), 'K': (35, 45), 'temp': (20, 30), 'hum': (80, 90), 'ph': (6.0, 7.0), 'rain': (180, 300)},
        'maize': {'N': (60, 100), 'P': (35, 60), 'K': (15, 25), 'temp': (18, 28), 'hum': (55, 75), 'ph': (5.5, 7.0), 'rain': (60, 110)},
        'chickpea': {'N': (20, 60), 'P': (55, 80), 'K': (75, 85), 'temp': (17, 21), 'hum': (14, 20), 'ph': (5.3, 9.0), 'rain': (65, 95)},
        'pigeonpeas': {'N': (0, 40), 'P': (55, 80), 'K': (15, 25), 'temp': (18, 37), 'hum': (30, 70), 'ph': (4.5, 8.5), 'rain': (90, 200)},
        'lentil': {'N': (0, 40), 'P': (35, 60), 'K': (15, 25), 'temp': (15, 30), 'hum': (60, 70), 'ph': (5.9, 7.8), 'rain': (35, 55)},
        # ... simplified logic for others ...
    }
    
    # Default range for unspecified crops to ensure variety
    default_range = {'N': (20, 100), 'P': (20, 100), 'K': (20, 100), 'temp': (20, 35), 'hum': (30, 90), 'ph': (5.5, 7.5), 'rain': (50, 250)}

    for crop in CROP_LABELS:
        r = ranges.get(crop, default_range)
        for _ in range(samples_per_crop):
            row = {
                'N': np.random.uniform(*r['N']),
                'P': np.random.uniform(*r['P']),
                'K': np.random.uniform(*r['K']),
                'temperature': np.random.uniform(*r['temp']),
                'humidity': np.random.uniform(*r['hum']),
                'ph': np.random.uniform(*r['ph']),
                'rainfall': np.random.uniform(*r['rain']),
                'label': crop
            }
            data.append(row)
            
    return pd.DataFrame(data)

def train():
    print("Generating synthetic data...")
    df = generate_synthetic_data()
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Save the model and labels
    joblib.dump(model, 'server/crop_model.joblib')
    joblib.dump(CROP_LABELS, 'server/labels.joblib')
    print("Model saved to server/crop_model.joblib")

if __name__ == "__main__":
    train()
