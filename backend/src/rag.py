"""
RAG (Retrieval-Augmented Generation) utilities for board game search.

Uses ChromaDB in persistent local mode — no separate server required.
The DB is stored at a path relative to this file so it works regardless
of the working directory (Railway, local, etc.).
"""

import html
import os
import re

import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_CHROMA_PERSIST_DIR = os.path.join(_ROOT, "data", "chroma_db")
_CHROMA_COLLECTION = "boardgames"

_CSV_PATH = os.path.join(
    _ROOT, "data", "processed", "games_detailed_info2025.csv"
)

_EMBEDDING_MODEL = "text-embedding-3-small"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _clean_description(raw: str) -> str:
    """Strip HTML entities and excess whitespace from BGG descriptions."""
    text = html.unescape(raw)                    # &amp; → &, &#10; → \n, etc.
    text = re.sub(r"\s+", " ", text).strip()     # collapse whitespace
    return text


def _get_embedding_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=_EMBEDDING_MODEL)


def _get_vectorstore(embedding_model: OpenAIEmbeddings) -> Chroma:
    """Open (or create) the persistent Chroma collection."""
    persist_dir = os.path.abspath(_CHROMA_PERSIST_DIR)
    return Chroma(
        collection_name=_CHROMA_COLLECTION,
        embedding_function=embedding_model,
        persist_directory=persist_dir,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def prepare_db(test: bool = False) -> dict:
    """
    Clear the existing vector DB and re-seed it from the processed CSV.

    Each document is the cleaned description, with 'name' stored as metadata
    so callers can surface the game title alongside search results.

    Returns a dict with the number of documents indexed.
    """
    csv_path = os.path.abspath(_CSV_PATH)
    df = pd.read_csv(csv_path, usecols=["name", "description"])
    df = df.dropna(subset=["description", "name"])

    if test:
        df = df.head(100)

    texts = [_clean_description(desc) for desc in df["description"]]
    metadatas = [{"name": name} for name in df["name"]]

    embedding_model = _get_embedding_model()
    persist_dir = os.path.abspath(_CHROMA_PERSIST_DIR)
    os.makedirs(persist_dir, exist_ok=True)

    # Delete existing collection so we start fresh on each prepare call
    existing = Chroma(
        collection_name=_CHROMA_COLLECTION,
        embedding_function=embedding_model,
        persist_directory=persist_dir,
    )
    existing.delete_collection()

    # Re-create and seed
    Chroma.from_texts(
        texts=texts,
        metadatas=metadatas,
        embedding=embedding_model,
        collection_name=_CHROMA_COLLECTION,
        persist_directory=persist_dir,
    )

    return {"indexed": len(texts)}


def search_db(query: str, k: int = 5) -> list[dict]:
    """
    Search the vector DB for board games matching *query*.

    Returns a list of dicts with keys:
        - name: game name
        - description: (truncated) description excerpt
        - score: similarity distance (lower = more similar)
    """
    embedding_model = _get_embedding_model()
    vectorstore = _get_vectorstore(embedding_model)

    results = vectorstore.similarity_search_with_score(query, k=k)

    return [
        {
            "name": doc.metadata.get("name", "Unknown"),
            "description": doc.page_content[:500],  # truncate for API response
            "score": float(score),
        }
        for doc, score in results
    ]
