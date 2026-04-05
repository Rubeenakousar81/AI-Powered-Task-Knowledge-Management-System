"""
This is the AI part of the project.
I'm using sentence-transformers to convert text into vectors (embeddings)
and FAISS to store and search them.
No external LLM API - everything runs locally.

took me a while to figure out FAISS but it works well
"""

import os
import json
import numpy as np

# these libraries need to be installed via pip
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    AI_READY = True
    print("AI model loaded successfully")
except:
    AI_READY = False
    print("sentence-transformers not installed, using keyword search instead")

try:
    import faiss
    FAISS_READY = True
except:
    FAISS_READY = False

# files to save the index between restarts
INDEX_FILE = "faiss_index.bin"
META_FILE  = "faiss_meta.json"
DIM = 384  # all-MiniLM-L6-v2 gives 384 dimensions

# load existing index if available
metadata = []  # list of {doc_id, title, chunk}
index = None

if FAISS_READY:
    index = faiss.IndexFlatIP(DIM)
    if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(META_FILE) as f:
            metadata = json.load(f)


def save_index():
    if FAISS_READY and index:
        faiss.write_index(index, INDEX_FILE)
        with open(META_FILE, "w") as f:
            json.dump(metadata, f)


def add_to_index(doc_id, title, content):
    """split doc into chunks, embed them, store in faiss"""
    if not AI_READY or not FAISS_READY:
        # just save to metadata so keyword search still works
        metadata.append({"doc_id": doc_id, "title": title, "chunk": content[:500]})
        return

    # split into chunks of ~200 words
    words = content.split()
    chunks = []
    for i in range(0, len(words), 150):
        chunk = " ".join(words[i:i+200])
        chunks.append(chunk)

    if not chunks:
        chunks = [content]

    # convert to embeddings
    vecs = model.encode(chunks, convert_to_numpy=True).astype("float32")

    # normalize so inner product = cosine similarity
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    vecs = vecs / np.maximum(norms, 1e-9)

    index.add(vecs)

    for chunk in chunks:
        metadata.append({"doc_id": doc_id, "title": title, "chunk": chunk})

    save_index()


def search_docs(query, top_k=5):
    """search for documents similar to query"""

    if AI_READY and FAISS_READY and index and index.ntotal > 0:
        # embed the query
        q_vec = model.encode([query], convert_to_numpy=True).astype("float32")
        norm = np.linalg.norm(q_vec)
        q_vec = q_vec / max(norm, 1e-9)

        k = min(top_k * 3, index.ntotal)
        scores, indices = index.search(q_vec, k)

        # collect results, one per doc
        seen = {}
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(metadata):
                item = metadata[idx]
                doc_id = item["doc_id"]
                if doc_id not in seen:
                    seen[doc_id] = {"meta": item, "score": float(score)}

        results = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    else:
        # fallback: simple keyword matching
        query_words = set(query.lower().split())
        results = []
        seen = set()
        for item in metadata:
            if item["doc_id"] in seen:
                continue
            chunk_words = set(item["chunk"].lower().split())
            overlap = len(query_words & chunk_words)
            if overlap > 0:
                results.append({"meta": item, "score": overlap / len(query_words)})
                seen.add(item["doc_id"])

        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]


def remove_from_index(doc_id):
    """remove a document from the index"""
    global index, metadata
    metadata = [m for m in metadata if m["doc_id"] != doc_id]

    # rebuild index without that doc
    if FAISS_READY:
        index = faiss.IndexFlatIP(DIM)
        if metadata and AI_READY:
            vecs = model.encode([m["chunk"] for m in metadata], convert_to_numpy=True).astype("float32")
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            vecs = vecs / np.maximum(norms, 1e-9)
            index.add(vecs)
        save_index()
