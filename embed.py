import chromadb
from sentence_transformers import SentenceTransformer
from ingest import load_documents, chunk_documents

COLLECTION_NAME = "professor_reviews"

def get_collection():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(COLLECTION_NAME)
    return collection

def embed_and_store():
    docs = load_documents()
    chunks = chunk_documents(docs)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path="./chroma_db")

    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    print(f"Embedding {len(chunks)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=[{"source": s} for s in sources]
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB")

def retrieve(query, k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    collection = get_collection()

    query_embedding = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })
    return chunks

if __name__ == "__main__":
    embed_and_store()
    print("\n--- Testing retrieval ---\n")
    test_queries = [
        "Is Professor Whittaker a good professor?",
        "What do students say about Professor Rahn's grading?",
        "Does Professor Boroojeni give extra credit?"
    ]
    for query in test_queries:
        print(f"QUERY: {query}")
        results = retrieve(query)
        for r in results:
            print(f"  [{r['distance']:.3f}] {r['source']}: {r['text'][:120]}...")
        print()