import os
import logging
from sentence_transformers import SentenceTransformer
import chromadb

logger = logging.getLogger(__name__)

class ChromaClient:
    def __init__(self):
        # Initialize persistent ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.collection_name = "pci_dss_knowledge"

        # Load embedding model
        logger.info("Loading sentence-transformers model...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Model loaded successfully")

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB collection ready: {self.collection_name}")

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50):
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
        return chunks

    def load_documents(self, docs_folder: str = "./docs"):
        total_chunks = 0
        for filename in os.listdir(docs_folder):
            if filename.endswith(".txt"):
                filepath = os.path.join(docs_folder, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

                chunks = self.chunk_text(text)
                logger.info(f"File: {filename} — {len(chunks)} chunks created")

                for i, chunk in enumerate(chunks):
                    doc_id = f"{filename}_{i}"

                    # Check if already exists
                    existing = self.collection.get(ids=[doc_id])
                    if existing["ids"]:
                        continue

                    # Embed and store
                    embedding = self.model.encode(chunk).tolist()
                    self.collection.add(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[{"source": filename, "chunk_index": i}]
                    )
                    total_chunks += 1

        logger.info(f"Total chunks stored in ChromaDB: {total_chunks}")
        return total_chunks

    def query(self, question: str, n_results: int = 3):
        embedding = self.model.encode(question).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        return results

    def get_doc_count(self):
        return self.collection.count()