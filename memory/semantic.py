import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class SemanticMemory:
    """
    RAG-based knowledge retrieval using OpenAI Embeddings.
    """
    def __init__(self, persist_directory: str = "./data/semantic"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name="knowledge",
            embedding_function=self.embedding_fn
        )

    def add_knowledge(self, content: str, source: str, metadata: Dict = None):
        if metadata is None:
            metadata = {}
        metadata["source"] = source
        
        doc_id = f"doc_{hash(content) % 10000}"
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def query_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        findings = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                findings.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return findings
