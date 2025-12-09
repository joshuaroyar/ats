import json
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

# Load the skill graph from Step 1
GRAPH_FILE = "utils/esco/esco_skill_graph.json"
OUTPUT_FILE = "utils/esco/skill_embeddings.json"

print("Loading ESCO graph...")
with open(GRAPH_FILE, "r", encoding="utf-8") as f:
    graph = json.load(f)

nodes = graph["nodes"]

print("Total skills to embed:", len(nodes))

# Load the embedding model
print("Loading model: intfloat/e5-base ...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("intfloat/e5-base", device=device)

embeddings_output = []

print("Generating embeddings...")

for n in tqdm(nodes):
    skill_id = n["id"]
    name = n["name"]
    alt_labels = n["alt"]

    # Combine name + synonyms into a single string
    text = name

    if alt_labels:
        text += " " + " ".join(alt_labels)

    # E5 requires prefix "query: "
    emb = model.encode("query: " + text, convert_to_numpy=True)

    embeddings_output.append({
        "id": skill_id,
        "name": name,
        "alt": alt_labels,
        "embedding": emb.tolist()
    })

print("Saving embeddings to", OUTPUT_FILE)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(embeddings_output, f, ensure_ascii=False, indent=2)

print("DONE — Embeddings successfully generated!")
