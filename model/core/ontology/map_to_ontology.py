import json
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

# Load embeddings
with open("skill_embeddings.json", "r", encoding="utf-8") as f:
    SKILL_DB = json.load(f)

# Convert embeddings into arrays for fast math
EMB = np.array([np.array(s["embedding"]) for s in SKILL_DB])
IDS = [s["id"] for s in SKILL_DB]
NAMES = [s["name"] for s in SKILL_DB]

# Load local embedding model (same as before)
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("intfloat/e5-base", device=device)

def cosine(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

def map_to_esco(skill_phrase):
    # embed candidate phrase
    emb = model.encode("query: " + skill_phrase, convert_to_numpy=True)

    # compute cosine similarity against all ESCO embeddings
    sims = EMB @ emb / (norm(EMB, axis=1) * norm(emb))

    # find best match
    idx = np.argmax(sims)
    best_score = sims[idx]

    if best_score < 0.60:
        return None  # too weak match

    return {
        "phrase": skill_phrase,
        "esco_id": IDS[idx],
        "esco_name": NAMES[idx],
        "similarity": float(best_score)
    }
