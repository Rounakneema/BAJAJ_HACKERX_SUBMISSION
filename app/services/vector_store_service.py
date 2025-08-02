import pinecone
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict
from ..config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_CLOUD,
    PINECONE_REGION
)

pc = Pinecone(api_key=PINECONE_API_KEY)

if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
    )

index = pc.Index(PINECONE_INDEX_NAME)

# NEW: A function to get the current vector count
def get_vector_count() -> int:
    """Returns the total number of vectors in the index."""
    return index.describe_index_stats().get('total_vector_count', 0)

def upsert_chunks(document_id: str, chunks_with_metadata: List[Dict], embeddings: List[List[float]]):
    """Upserts chunks with their rich metadata (page, clause_ref)."""
    vectors_to_upsert = []
    for i, embedding in enumerate(embeddings):
        metadata = chunks_with_metadata[i]
        vectors_to_upsert.append({
            "id": f"{document_id}_{i}",
            "values": embedding,
            "metadata": metadata
        })
    if vectors_to_upsert:
        index.upsert(vectors=vectors_to_upsert)

def query_by_vector(document_id: str, vector: List[float], top_k: int) -> List[dict]:
    """Queries and returns the full metadata, including page and clause ref."""
    results = index.query(
        vector=vector, top_k=top_k, include_metadata=True, filter={"document_id": {"$eq": document_id}}
    )
    return [match['metadata'] for match in results.get('matches', [])]

def delete_by_id(document_id: str):
    index.delete(filter={"document_id": {"$eq": document_id}})