import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import json
import time
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class EpisodicMemory:
    """
    Experience memory storing trajectories, outcomes, and reflections using OpenAI Embeddings.
    """
    def __init__(self, persist_directory: str = "./data/episodic"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Use the official ChromaDB OpenAI embedding function
        self.embedding_fn = OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name="episodes",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.embedding_fn
        )

    def add_episode(self, task: str, trajectory: List[str], outcome: str, reflection: str, importance: float = 0.5):
        episode_id = f"ep_{int(time.time())}_{hash(task) % 1000}"
        metadata = {
            "task": task,
            "outcome": outcome,
            "reflection": reflection,
            "importance": importance,
            "timestamp": time.time(),
            "trajectory": json.dumps(trajectory)
        }
        
        self.collection.add(
            documents=[f"Task: {task}. Outcome: {outcome}. Reflection: {reflection}"],
            metadatas=[metadata],
            ids=[episode_id]
        )

    def retrieve_episodes(self, query: str, top_k: int = 3, min_importance: float = 0.0) -> List[Dict]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"importance": {"$gte": min_importance}}
        )
        
        episodes = []
        if results['metadatas']:
            for meta in results['metadatas'][0]:
                meta['trajectory'] = json.loads(meta['trajectory'])
                episodes.append(meta)
        return episodes
