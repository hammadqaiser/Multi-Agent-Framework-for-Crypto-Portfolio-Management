"""
Crypto MAS – Memory System (FINAL, Gemini-safe)

✔ No Gemini embedding usage (prevents quota exhaustion)
✔ Uses local SentenceTransformers embeddings
✔ Persistent ChromaDB storage
✔ Stable for demos, testing, LangGraph, MAS
"""

from typing import List, Tuple, Dict
import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings


class CryptoMemory:
    """
    Memory system for Crypto MAS.
    Stores past market situations & decisions.
    Retrieves similar historical patterns for reasoning.
    """

    def __init__(
        self,
        name: str,
        persist_dir: str = ".chroma_memory",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        # -----------------------------
        # Embedding (LOCAL, SAFE)
        # -----------------------------
        self.embedding = HuggingFaceEmbeddings(
            model_name=embedding_model
        )

        # -----------------------------
        # ChromaDB (Persistent)
        # -----------------------------
        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_dir,
                allow_reset=True,
            )
        )

        self.collection = self.client.get_or_create_collection(name=name)

    # --------------------------------------------------
    # Get embedding
    # --------------------------------------------------
    def _embed(self, text: str) -> List[float]:
        return self.embedding.embed_query(text)

    # --------------------------------------------------
    # Add memories
    # --------------------------------------------------
    def add_situations(self, items: List[Tuple[str, str]]):
        """
        items:
        [
            ("market situation description", "decision / lesson"),
            ...
        ]
        """
        docs, metas, ids, embeds = [], [], [], []
        offset = self.collection.count()

        for i, (situation, decision) in enumerate(items):
            docs.append(situation)
            metas.append({"decision": decision})
            ids.append(str(offset + i))
            embeds.append(self._embed(situation))

        self.collection.add(
            documents=docs,
            metadatas=metas,
            embeddings=embeds,
            ids=ids,
        )

    # --------------------------------------------------
    # Retrieve memories
    # --------------------------------------------------
    def get_memories(self, situation: str, n_matches: int = 2) -> List[Dict]:
        query_embedding = self._embed(situation)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_matches,
            include=["documents", "metadatas", "distances"],
        )

        memories = []
        for i in range(len(results["documents"][0])):
            memories.append({
                "matched_situation": results["documents"][0][i],
                "decision": results["metadatas"][0][i]["decision"],
                "similarity": round(1 - results["distances"][0][i], 4),
            })

        return memories


# --------------------------------------------------
# Standalone test
# --------------------------------------------------
if __name__ == "__main__":
    memory = CryptoMemory(name="crypto_mas_memory")

    examples = [
        (
            "BTC volatility spikes while whale outflows increase",
            "Reduce leverage, widen stop-loss, wait for confirmation"
        ),
        (
            "ETH staking deposits surge with bullish sentiment",
            "Gradually increase ETH exposure using laddered entries"
        ),
    ]

    memory.add_situations(examples)

    query = "BTC showing selling pressure and negative sentiment"
    results = memory.get_memories(query, n_matches=2)

    print("\nRetrieved Memories:")
    for r in results:
        print(r)
