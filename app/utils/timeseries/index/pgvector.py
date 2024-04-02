import json

import psycopg2

from app.utils.timeseries.index._base import BaseTimeSeriesIndex


class PgVectorTimeSeriesIndex(BaseTimeSeriesIndex):

    def __init__(self):
        self.conn = psycopg2.connect(
            user="user",
            password="pass",
            host="localhost",
            port=5432,  # The port you exposed in docker-compose.yml
            database="app"
        )

    def upsert(self, vectors: tuple[str, list[float]] | list[tuple[str, list[float]]]):
        if isinstance(vectors, tuple):
            vectors = [vectors]

        cur = self.conn.cursor()

        for symbol, vector in vectors:
            print(type(vector), symbol)
            cur.execute(
                "INSERT INTO coins (symbol, embedding) VALUES (%s, %s)",
                (symbol, json.dumps(vector))
            )

    def query(self, query_vector: list[float], top_k: int) -> list[tuple[str, float]]:
        cur = self.conn.cursor()
        print(query_vector)
        cur.execute(
            f"""SELECT symbol, 1 - (embedding <-> %s) AS cosine_similarity
               FROM coins
               ORDER BY cosine_similarity DESC LIMIT {top_k}""",
            (json.dumps(query_vector),)
        )

        matches = [row for row in cur.fetchall()]

        return matches
