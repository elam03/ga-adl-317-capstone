import os
import pickle
import warnings
from typing import List

import pandas as pd
import torch
import torch.nn as nn


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
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# 1. Load Preprocessing Assets
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
input_dim = len(feature_names)
model = DeepNet(input_features=input_dim)
model_path = os.path.join(MODELS_DIR, 'boardgame_rating_model.pth')
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()


def predict_rating_from_features(categories: List[str], mechanics: List[str]) -> float:
    """Predicts a board game rating given its categories and mechanics."""
    sample_series = pd.Series(0.0, index=feature_names)
    
    # Fill numerical defaults
    for col in original_numerical_means.index:
        if col in sample_series.index:
            sample_series[col] = original_numerical_means[col]

    # One-hot encoding
    cats_encoded = mlb_category.transform([categories])
    mechs_encoded = mlb_mechanic.transform([mechanics])

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

    return round(pred, 2)
