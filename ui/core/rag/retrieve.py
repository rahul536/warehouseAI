import os
import sys
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from openai import OpenAI


# Add project root to Python path and load .env
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

VECTOR_DIR = PROJECT_ROOT / "knowledge_base" / "vector_store"
COLLECTION_NAME = "warehouse_knowledge"

EMBEDDING_MODEL = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "text-embedding-3-small",
)


def embed_query(query: str) -> list[float]:
    """Generate embedding for a user query."""
    client = OpenAI()
    
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=query,
    )
    
    return response.data[0].embedding


def retrieve_knowledge(
    query: str,
    n_results: int = 5,
    filter_metadata: dict[str, Any] | None = None,
) -> dict:
    """
    Retrieve relevant knowledge chunks from the vector store.
    
    Args:
        query: User question or search query
        n_results: Number of relevant chunks to retrieve
        filter_metadata: Optional metadata filter (e.g., {"source_type": "pdf_text"})
    
    Returns:
        Dictionary with retrieved chunks and metadata
    """
    client = chromadb.PersistentClient(path=str(VECTOR_DIR))
    collection = client.get_collection(name=COLLECTION_NAME)
    
    query_embedding = embed_query(query)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=filter_metadata,
    )
    
    if not results["ids"][0]:
        return {
            "status": "NO_RESULTS",
            "query": query,
            "chunks": [],
        }
    
    chunks = []
    for i, doc_id in enumerate(results["ids"][0]):
        chunks.append({
            "id": doc_id,
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i] if "distances" in results else None,
        })
    
    return {
        "status": "FOUND",
        "query": query,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }


def format_chunks_for_context(chunks: list[dict]) -> str:
    """Format retrieved chunks for inclusion in AI context."""
    if not chunks:
        return "No relevant knowledge base documents found."
    
    lines = ["Relevant knowledge base information:"]
    
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source_file", "unknown")
        source_type = metadata.get("source_type", "unknown")
        locator = metadata.get("locator", "unknown")
        
        lines.append(f"\n--- Document {i} ---")
        lines.append(f"Source: {source}")
        lines.append(f"Type: {source_type}")
        lines.append(f"Location: {locator}")
        lines.append(f"Content: {chunk['text']}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    
    # Test retrieval
    test_queries = [
        "logistics procedures",
        "warehouse operations",
        "inventory management",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        result = retrieve_knowledge(query, n_results=3)
        print(json.dumps(result, indent=2))
        
        if result["status"] == "FOUND":
            print("\n--- Formatted Context ---")
            print(format_chunks_for_context(result["chunks"]))
