"""
MilvusVectorStore: Handles document vector storage and similarity search in Milvus.
"""
from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility,
)
from typing import List
from ..config import DB_HOST, DB_PORT, DB_NAME


class MilvusVectorStore:
    def __init__(self, collection_name: str = "document_vectors", dim: int = 384):
        self.collection_name = collection_name
        self.dim = dim
        self.connect()
        self.setup_collection()

    def connect(self):
        connections.connect(DB_NAME, host=DB_HOST, port=DB_PORT)

    def setup_collection(self):
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(
                    name="doc_id",
                    dtype=DataType.VARCHAR,
                    max_length=64,
                    is_primary=True,
                    auto_id=False,
                ),
                FieldSchema(name="username", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=16),
                FieldSchema(
                    name="document_name", dtype=DataType.VARCHAR, max_length=256
                ),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=2048),
                FieldSchema(
                    name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim
                ),
            ]
            schema = CollectionSchema(
                fields=fields, description="Document vector collection"
            )
            self.collection = Collection(
                self.collection_name, schema, consistency_level="Strong"
            )
            self.collection.create_index(
                field_name="embedding",
                index_params={
                    "index_type": "IVF_FLAT",
                    "metric_type": "L2",
                    "params": {"nlist": 128},
                },
            )
        else:
            self.collection = Collection(self.collection_name)
        self.collection.load()

    def insert_documents(
        self,
        doc_ids: List[str],
        usernames: List[str],
        session_ids: List[str],
        doc_types: List[str],
        document_names: List[str],
        contents: List[str],
        embeddings: List[List[float]],
    ):
        self.collection.insert(
            [
                doc_ids,
                usernames,
                session_ids,
                doc_types,
                document_names,
                contents,
                embeddings,
            ]
        )

    def similarity_search(
        self, query_embedding: List[float], k: int = 4, session_id: str = None
    ):
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        expr = None
        if session_id:
            expr = f"session_id == '{session_id}'"
        results = self.collection.search(
            [query_embedding],
            "embedding",
            search_params,
            limit=k,
            output_fields=["doc_id", "content"],
            expr=expr,
        )
        docs = [hit.entity.get("content") for hit in results[0]]
        return docs
