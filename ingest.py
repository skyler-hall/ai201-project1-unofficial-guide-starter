import os

DATA_DIR = "data"

def load_documents():
    documents = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"source": filename, "text": text})
    return documents

def chunk_documents(documents):
    chunks = []
    for doc in documents:
        source = doc["source"]
        parts = doc["text"].split("---")
        for part in parts:
            part = part.strip()
            if len(part) > 50:
                chunks.append({"source": source, "text": part})
    return chunks

if __name__ == "__main__":
    import random
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    chunks = chunk_documents(docs)
    print(f"Total chunks: {len(chunks)}")
    print("\n--- 5 random chunks ---\n")
    for chunk in random.sample(chunks, 5):
        print(f"SOURCE: {chunk['source']}")
        print(chunk['text'])
        print("\n" + "="*60 + "\n")