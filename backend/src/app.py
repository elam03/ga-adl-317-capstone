import os
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from backend.src.predictor import predict_rating_from_features
from backend.src import rag

# Load backend-local env vars (backend/.env)
_backend_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
load_dotenv(_backend_env)

from backend.src.auth import verify_api_key

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


class GameInput(BaseModel):
    categories: List[str]
    mechanics: List[str]

@app.post("/predict")
def predict_rating(game: GameInput, _: str = Security(verify_api_key)):
    pred = predict_rating_from_features(game.categories, game.mechanics)
    return {"predicted_rating": pred}


@app.post("/rag/prepare")
def rag_prepare(test: bool = False, clear: bool = False, _: str = Security(verify_api_key)):
    """Seed the vector DB from the board game CSV. Set clear=True to wipe it first."""
    result = rag.prepare_db(test=test, clear=clear)
    return {"status": "ok", **result}


@app.get("/rag/search")
def rag_search(query: str, k: int = 5, _: str = Security(verify_api_key)):
    """Search the vector DB for board games matching *query*."""
    results = rag.search_db(query, k=k)
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run("backend.src.app:app", host="127.0.0.1", port=8000, reload=True)
