from __future__ import annotations
from typing import Any, Dict, List, Sequence

from .base import VectorBackend

try:
    from pymongo import MongoClient
    from pymongo.collection import Collection
except ImportError:  # pragma: no cover
    MongoClient = None
    Collection = None


class MongoVectorBackend(VectorBackend):
    """
    MongoDB Atlas Vector Search backend.

    Requirements:
      - pymongo>=4.6
      - A collection with a vector field (e.g., "vector": [float,...])
      - Atlas Search index configured for the vector field.

    Notes:
      - ensure_index() attempts to create/verify a vector search index via
        `db.command({"createSearchIndexes": ...})` — you might need proper permissions.
      - If creation is not allowed by your role, create the index in Atlas UI and skip.
    """

    def __init__(
        self,
        uri: str,
        db_name: str,
        collection_name: str = "jane_memory",
        vector_field: str = "vector",
        text_field: str = "text",
        meta_field: str = "meta",
        id_field: str = "_id",
        similarity: str = "cosine",
        num_dimensions: int = 384,  # set to your embedding dimension
    ) -> None:
        if MongoClient is None:
            raise RuntimeError("pymongo is not installed. `pip install pymongo`.")
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.col: Collection = self.db[collection_name]
        self.vector_field = vector_field
        self.text_field = text_field
        self.meta_field = meta_field
        self.id_field = id_field
        self.similarity = similarity
        self.num_dimensions = num_dimensions

    def upsert(self, items: Sequence[Dict[str, Any]]) -> None:
        ops = []
        for it in items:
            doc = {
                self.id_field: it["id"],
                self.text_field: it.get("text", ""),
                self.meta_field: it.get("meta", {}),
                self.vector_field: it["vector"],
            }
            ops.append(
                {
                    "updateOne": {
                        "filter": {self.id_field: it["id"]},
                        "update": {"$set": doc},
                        "upsert": True,
                    }
                }
            )
        if ops:
            self.col.bulk_write(ops, ordered=False)

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        # Atlas Vector Search aggregation stage (knnBeta). For classic "atlas search",
        # use the $search stage with "knnBeta". See Atlas docs for details.
        pipeline = [
            {
                "$search": {
                    "index": "jane_vector_index",
                    "knnBeta": {
                        "vector": query_vector,
                        "path": self.vector_field,
                        "k": max(1, top_k),
                    },
                }
            },
            {"$limit": max(1, top_k)},
            {
                "$project": {
                    "_id": 0,
                    "id": f"${self.id_field}",
                    "text": f"${self.text_field}",
                    "meta": f"${self.meta_field}",
                    "score": {"$meta": "searchScore"},
                }
            },
        ]
        out = []
        for doc in self.col.aggregate(pipeline):
            out.append(
                {
                    "id": doc.get("id"),
                    "text": doc.get("text", ""),
                    "score": float(doc.get("score", 0.0)),
                    "meta": doc.get("meta", {}),
                }
            )
        return out

    def ensure_index(self, **kwargs: Any) -> None:
        """
        Attempt to create the Atlas Search vector index if not present.

        Example spec:
        {
          "name": "jane_vector_index",
          "definition": {
            "fields": [
              {
                "type": "vector",
                "path": "vector",
                "numDimensions": 384,
                "similarity": "cosine"
              }
            ]
          }
        }
        """
        spec = {
            "name": "jane_vector_index",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": self.vector_field,
                        "numDimensions": self.num_dimensions,
                        "similarity": self.similarity,
                    }
                ]
            },
        }
        try:
            self.db.command(
                {
                    "createSearchIndexes": self.col.name,
                    "indexes": [spec],
                }
            )
        except Exception:
            # If already exists or not permitted, ignore.
            pass
