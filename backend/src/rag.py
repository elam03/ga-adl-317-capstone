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

def prepare_db(test: bool = False, clear: bool = False, batch_size: int = 200) -> dict:
    """
    Seed the vector DB from the processed CSV in batches.
    
    If `clear` is True, it will wipe the existing DB first.
    Otherwise, it will check for already indexed game names and skip them,
    allowing the process to resume if it was interrupted or hit an error.

    Returns a dict with the number of documents indexed, skipped, and errors.
    """
    csv_path = os.path.abspath(_CSV_PATH)
    df = pd.read_csv(csv_path, usecols=["name", "description"])
    df = df.dropna(subset=["description", "name"])

    embedding_model = _get_embedding_model()
    persist_dir = os.path.abspath(_CHROMA_PERSIST_DIR)
    os.makedirs(persist_dir, exist_ok=True)

    vectorstore = Chroma(
        collection_name=_CHROMA_COLLECTION,
        embedding_function=embedding_model,
        persist_directory=persist_dir,
    )

    if clear:
        print("Clearing existing vector database...")
        vectorstore.delete_collection()
        vectorstore = Chroma(
            collection_name=_CHROMA_COLLECTION,
            embedding_function=embedding_model,
            persist_directory=persist_dir,
        )

    # Get already indexed IDs to skip them
    try:
        existing_data = vectorstore.get()
        existing_ids = set(existing_data["ids"])
    except Exception:
        existing_ids = set()

    total_indexed = 0
    total_skipped = 0
    total_errors = 0
    chunks_processed = 0

    print(f"Found {len(existing_ids)} items already in the DB.")

    # Process in batches
    for i in range(0, len(df), batch_size):
        batch_df = df.iloc[i:i+batch_size]
        
        batch_texts = []
        batch_metadatas = []
        batch_ids = []
        
        for _, row in batch_df.iterrows():
            # Use the game name as the unique ID
            doc_id = str(row["name"]).strip()
            if doc_id in existing_ids:
                total_skipped += 1
                continue
                
            batch_texts.append(_clean_description(row["description"]))
            batch_metadatas.append({"name": row["name"]})
            batch_ids.append(doc_id)
            
        if not batch_texts:
            continue
            
        try:
            print(f"Indexing batch {i} to {i + len(batch_df)} ({len(batch_texts)} new items)...")
            vectorstore.add_texts(
                texts=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            total_indexed += len(batch_texts)
            chunks_processed += 1
            
            if test and chunks_processed >= 1:
                print("Test mode enabled: stopping after 1 successfully processed chunk.")
                break
        except Exception as e:
            print(f"Error indexing batch {i} to {i + len(batch_df)}: {e}")
            total_errors += 1

    return {
        "indexed": total_indexed,
        "skipped": total_skipped,
        "batch_errors": total_errors,
        "total_in_db": total_indexed + len(existing_ids)
    }

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
