"""Embedding + vector store and retrieval layers (Milestone 4).

  * build_vector_store()  embeds every chunk with all-MiniLM-L6-v2 and stores
                          the vectors, text, and metadata in a persistent
                          ChromaDB collection (cosine similarity).

  * retrieve()            embeds a user query and returns the top-k most similar
                          chunks, each with its similarity score and original
                          metadata, dropping matches below the similarity floor.

All tunable values come from config.py. The embedding model and Chroma client
are created lazily and cached so importing this module is cheap.
"""

import chromadb

import config

_model = None


def _get_model():
    """Lazily load and cache the SentenceTransformer embedding model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer  # heavy import
        _model = SentenceTransformer(config.EMBED_MODEL)
    return _model


def _get_client():
    """Return a persistent ChromaDB client rooted at config.CHROMA_DIR."""
    return chromadb.PersistentClient(path=str(config.CHROMA_DIR))


def embed_texts(texts):
    """Embed a list of texts into 384-dim L2-normalized vectors (as lists)."""
    model = _get_model()
    vectors = model.encode(
        texts,
        batch_size=config.EMBED_BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


# =========================================================================== #
# Embedding + vector store
# =========================================================================== #

def build_vector_store(chunks):
    """Embed chunks and (re)build the ChromaDB collection. Returns the collection.

    The collection is dropped and recreated so re-running yields exactly one
    record per chunk (count == len(chunks)), never duplicates.
    """
    client = _get_client()
    try:
        client.delete_collection(config.COLLECTION_NAME)
    except Exception:
        pass  # nothing to delete on a first run

    collection = client.create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": config.DISTANCE_METRIC},
    )

    metadata_keys = ("source", "url", "title", "doc_type", "date")
    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        embeddings=embed_texts([c["text"] for c in chunks]),
        documents=[c["text"] for c in chunks],
        metadatas=[{k: c[k] for k in metadata_keys} for c in chunks],
    )
    return collection


def get_collection():
    """Open the existing persisted collection (raises if it doesn't exist)."""
    return _get_client().get_collection(config.COLLECTION_NAME)


# =========================================================================== #
# Retrieval
# =========================================================================== #

def retrieve(query, k=config.TOP_K, collection=None):
    """Return up to k chunks most similar to `query`, above the similarity floor.

    Each result is a dict: {text, score, source, url, title, doc_type, date},
    where `score` is cosine similarity in [0, 1] (higher is more relevant).
    """
    collection = collection if collection is not None else get_collection()
    query_embedding = embed_texts([query])

    result = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for text, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        similarity = 1.0 - distance  # cosine distance -> similarity
        if similarity < config.MIN_SIMILARITY:
            continue
        chunks.append({"text": text, "score": similarity, **meta})
    return chunks
