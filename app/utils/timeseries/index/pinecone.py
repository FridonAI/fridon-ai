import time

from pinecone import PodSpec
from pinecone import Pinecone, Index

from app.utils.timeseries.index._base import BaseTimeSeriesIndex


class PineconeTimeSeriesIndex(BaseTimeSeriesIndex):

    def __init__(self, index_name: str, dimension: int):
        pinecone = Pinecone()
        self._index = self._create_index(pinecone, index_name, dimension)

    @staticmethod
    def _create_index(pinecone: Pinecone, index_name: str, dimension: int) -> Index:
        existing_indexes = [
            index_info["name"] for index_info in pinecone.list_indexes()
        ]

        if index_name not in existing_indexes:
            # if does not exist, create index
            pinecone.create_index(
                index_name,
                dimension=dimension,
                metric="cosine",
                spec=PodSpec(
                    environment="gcp-starter",
                )
            )
            # wait for index to be initialized
            while not pinecone.describe_index(index_name).status["ready"]:
                time.sleep(1)

        return pinecone.Index(index_name)

    def upsert(self, vectors: tuple[str, list[float]] | list[tuple[str, list[float]]]):
        if isinstance(vectors, tuple):
            vectors = [vectors]

        resp = self._index.upsert(vectors)
        print(resp)

    def query(self, query_vector: list[float], top_k: int) -> list[tuple[str, float]]:
        query_response = self._index.query(
            vector=query_vector,
            top_k=top_k,
        )

        matches = [(m.id, m.score) for m in query_response.matches]

        return matches
