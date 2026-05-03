import os
import torch
import pickle
import pandas as pd
from fastapi import FastAPI, Security, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List
import torch.nn as nn
from dotenv import load_dotenv

# Load backend-local env vars (backend/.env)
_backend_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_backend_env)

# --- Auth ---
_API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=_API_KEY_NAME, auto_error=False)
_API_SECRET_KEY = os.getenv("API_SECRET_KEY", "")

if not _API_SECRET_KEY:
    raise RuntimeError("API_SECRET_KEY env var is not set. Add it to backend/.env")


def verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    """Dependency that validates the X-API-Key header."""
    if not api_key or api_key != _API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key",
        )
    return api_key

app = FastAPI(title="Board Game Rating Predictor")

# Support multiple origins via a comma-separated ALLOWED_ORIGINS env var.
# Falls back to localhost for local development.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

class DeepNet(nn.Module):
    def __init__(self, input_features, dropout_rate=0.3):
        super().__init__()

        self.model = nn.Sequential(
            nn.Linear(input_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, x):
        return self.model(x)

# --- Initialization Logic ---
# Update: Added an extra dirname because app.py is now in src/backend/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# 1. Load Preprocessing Assets
import warnings
assets_path = os.path.join(MODELS_DIR, 'preprocessing_assets.pkl')

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    with open(assets_path, 'rb') as f:
        assets = pickle.load(f)

scaler = assets['scaler']
mlb_category = assets['mlb_category']
mlb_mechanic = assets['mlb_mechanic']
original_numerical_means = assets['original_numerical_means']
feature_names = assets['feature_names']

# 2. Reconstruct Model and Load Weights
# Note: Ensure DeepNet class definition is imported or defined here
input_dim = len(feature_names)
model = DeepNet(input_features=input_dim) # Use the class defined earlier
model_path = os.path.join(MODELS_DIR, 'boardgame_rating_model.pth')
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

class GameInput(BaseModel):
    categories: List[str]
    mechanics: List[str]

@app.post("/predict")
def predict_rating(game: GameInput, _: str = Security(verify_api_key)):
    # Re-use the logic from our predict_with_mechanics function
    sample_series = pd.Series(0.0, index=feature_names)
    
    # Fill numerical defaults
    for col in original_numerical_means.index:
        if col in sample_series.index:
            sample_series[col] = original_numerical_means[col]

    # One-hot encoding
    cats_encoded = mlb_category.transform([game.categories])
    mechs_encoded = mlb_mechanic.transform([game.mechanics])

    for i, val in enumerate(cats_encoded[0]):
        if val == 1 and f'category_{mlb_category.classes_[i]}' in sample_series.index:
            sample_series[f'category_{mlb_category.classes_[i]}'] = 1.0
            
    for i, val in enumerate(mechs_encoded[0]):
        if val == 1 and f'mechanic_{mlb_mechanic.classes_[i]}' in sample_series.index:
            sample_series[f'mechanic_{mlb_mechanic.classes_[i]}'] = 1.0

    # Scale and Predict
    sample_df = pd.DataFrame([sample_series])
    num_cols = original_numerical_means.index
    sample_df[num_cols] = scaler.transform(sample_df[num_cols])
    
    sample_tensor = torch.tensor(sample_df.values, dtype=torch.float32)
    with torch.no_grad():
        pred = model(sample_tensor).item()

    return {"predicted_rating": round(pred, 2)}

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run("backend.src.app:app", host="127.0.0.1", port=8000, reload=True)
