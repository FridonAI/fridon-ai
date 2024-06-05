from collections.abc import AsyncGenerator, AsyncIterator, Generator
from contextlib import asynccontextmanager, contextmanager

import psycopg
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.checkpoint.base import (
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.serde.base import SerializerProtocol
from psycopg_pool import AsyncConnectionPool, ConnectionPool

from app.core.checkpoint.utils import search_where


@contextmanager
def _get_sync_connection(
    connection: psycopg.Connection | ConnectionPool | None,
) -> Generator[psycopg.Connection, None, None]:
    if isinstance(connection, psycopg.Connection):
        yield connection
    elif isinstance(connection, ConnectionPool):
        with connection.connection() as conn:
            yield conn
    else:
        raise ValueError(
            "Invalid sync connection object. Please initialize the check pointer "
            f"with an appropriate sync connection object. "
            f"Got {type(connection)}."
        )


@asynccontextmanager
async def _get_async_connection(
    connection: psycopg.AsyncConnection | AsyncConnectionPool | None,
) -> AsyncGenerator[psycopg.AsyncConnection, None]:
    if isinstance(connection, psycopg.AsyncConnection):
        yield connection
    elif isinstance(connection, AsyncConnectionPool):
        async with connection.connection() as conn:
            yield conn
    else:
        raise ValueError(
            "Invalid async connection object. Please initialize the check pointer "
            f"with an appropriate async connection object. "
            f"Got {type(connection)}."
        )


class PostgresSaver(BaseCheckpointSaver):
    def __init__(
        self,
        *,
        sync_connection: psycopg.Connection | ConnectionPool | None = None,
        async_connection: psycopg.AsyncConnection | AsyncConnectionPool | None = (None),
        serde: SerializerProtocol | None = None,
    ) -> None:
        super().__init__(serde=serde)
        self.sync_connection = sync_connection
        self.async_connection = async_connection

    @contextmanager
    def _get_sync_connection(self) -> Generator[psycopg.Connection, None, None]:
        with _get_sync_connection(self.sync_connection) as connection:
            yield connection

    @asynccontextmanager
    async def _get_async_connection(
        self,
    ) -> AsyncGenerator[psycopg.AsyncConnection, None]:
        async with _get_async_connection(self.async_connection) as connection:
            yield connection

    @staticmethod
    def create_tables(connection: psycopg.Connection | ConnectionPool, /) -> None:
        with _get_sync_connection(connection) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS checkpoints (
                        thread_id TEXT NOT NULL,
                        thread_ts TEXT NOT NULL,
                        parent_ts TEXT,
                        checkpoint BYTEA NOT NULL,
                        metadata BYTEA
                        PRIMARY KEY (thread_id, thread_ts)
                    );
                    """
                )

    @staticmethod
    async def acreate_tables(
        connection: psycopg.AsyncConnection | AsyncConnectionPool, /
    ) -> None:
        async with _get_async_connection(connection) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS checkpoints (
                        thread_id TEXT NOT NULL,
                        thread_ts TEXT NOT NULL,
                        parent_ts TEXT,
                        checkpoint BYTEA NOT NULL,
                        metadata BYTEA,
                        PRIMARY KEY (thread_id, thread_ts)
                    );
                    """
                )

    @staticmethod
    def drop_tables(connection: psycopg.Connection, /) -> None:
        with connection.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS checkpoints;")

    @staticmethod
    async def adrop_tables(connection: psycopg.AsyncConnection, /) -> None:
        async with connection.cursor() as cur:
            await cur.execute("DROP TABLE IF EXISTS checkpoints;")

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        parent_ts = config["configurable"].get("thread_ts")

        with self._get_sync_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO checkpoints
                        (thread_id, thread_ts, parent_ts, checkpoint, metadata)
                    VALUES
                        (%(thread_id)s, %(thread_ts)s, %(parent_ts)s, %(checkpoint)s, %(metadata)s)
                    ON CONFLICT (thread_id, thread_ts)
                    DO UPDATE SET checkpoint = EXCLUDED.checkpoint, metadata = EXCLUDED.metadata;
                    """,
                    {
                        "thread_id": thread_id,
                        "thread_ts": checkpoint["id"],
                        "parent_ts": parent_ts if parent_ts else None,
                        "checkpoint": self.serde.dumps(checkpoint),
                        "metadata": self.serde.dumps(metadata),
                    },
                )

        return {
            "configurable": {
                "thread_id": thread_id,
                "thread_ts": checkpoint["id"],
            },
        }

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
    ) -> RunnableConfig:
        thread_id = config["configurable"]["thread_id"]
        parent_ts = config["configurable"].get("thread_ts")
        async with self._get_async_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO checkpoints
                        (thread_id, thread_ts, parent_ts, checkpoint, metadata)
                    VALUES
                        (%(thread_id)s, %(thread_ts)s, %(parent_ts)s, %(checkpoint)s, %(metadata)s)
                    ON CONFLICT (thread_id, thread_ts)
                    DO UPDATE SET checkpoint = EXCLUDED.checkpoint, metadata = EXCLUDED.metadata;
                    """,
                    {
                        "thread_id": thread_id,
                        "thread_ts": checkpoint["id"],
                        "parent_ts": parent_ts if parent_ts else None,
                        "checkpoint": self.serde.dumps(checkpoint),
                        "metadata": self.serde.dumps(metadata),
                    },
                )

        return {
            "configurable": {
                "thread_id": thread_id,
                "thread_ts": checkpoint["id"],
            },
        }

    def list(
        self,
        config: RunnableConfig,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Generator[CheckpointTuple, None, None]:
        with self._get_sync_connection() as conn:
            with conn.cursor() as cur:
                query = (
                    "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = %(thread_id)s ORDER BY thread_ts DESC"
                    if before is None
                    else "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = %(thread_id)s AND thread_ts < %(thread_ts)s ORDER BY thread_ts DESC"
                )
                if limit:
                    query += f" LIMIT {limit}"
                cur.execute(
                    query,
                    (
                        (str(config["configurable"]["thread_id"]),)
                        if before is None
                        else (
                            str(config["configurable"]["thread_id"]),
                            str(before["configurable"]["thread_ts"]),
                        )
                    ),
                )
                for value in cur:
                    yield CheckpointTuple(
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[1],
                            }
                        },
                        self.serde.loads(value[3]),
                        self.serde.loads(value[4]) if value[4] is not None else {},
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[2],
                            }
                        }
                        if value[2]
                        else None,
                    )

    async def alist(
        self,
        config: RunnableConfig,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        async with self._get_async_connection() as conn:
            async with conn.cursor() as cur:
                query = (
                    "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = %(thread_id)s ORDER BY thread_ts DESC"
                    if before is None
                    else "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints WHERE thread_id = %(thread_id)s AND thread_ts < %(thread_ts)s ORDER BY thread_ts DESC"
                )
                if limit:
                    query += f" LIMIT {limit}"
                await cur.execute(
                    query,
                    (
                        (str(config["configurable"]["thread_id"]),)
                        if before is None
                        else (
                            str(config["configurable"]["thread_id"]),
                            str(before["configurable"]["thread_ts"]),
                        )
                    ),
                )
                async for value in cur:
                    yield CheckpointTuple(
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[1],
                            }
                        },
                        self.serde.loads(value[3]),
                        self.serde.loads(value[4]) if value[4] is not None else {},
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[2],
                            }
                        }
                        if value[2]
                        else None,
                    )

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        thread_id = config["configurable"]["thread_id"]
        thread_ts = config["configurable"].get("thread_ts")
        with self._get_sync_connection() as conn:
            with conn.cursor() as cur:
                if thread_ts:
                    cur.execute(
                        "SELECT checkpoint, metadata, parent_ts "
                        "FROM checkpoints "
                        "WHERE thread_id = %(thread_id)s AND thread_ts = %(thread_ts)s",
                        {
                            "thread_id": thread_id,
                            "thread_ts": thread_ts,
                        },
                    )
                    if value := cur.fetchone():
                        return CheckpointTuple(
                            config,
                            self.serde.loads(value[0]),
                            self.serde.loads(value[1]),
                            {
                                "configurable": {
                                    "thread_id": thread_id,
                                    "thread_ts": value[2],
                                }
                            }
                            if value[2]
                            else None,
                        )
                else:
                    cur.execute(
                        "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata "
                        "FROM checkpoints "
                        "WHERE thread_id = %(thread_id)s "
                        "ORDER BY thread_ts DESC LIMIT 1",
                        {
                            "thread_id": thread_id,
                        },
                    )
                    if value := cur.fetchone():
                        return CheckpointTuple(
                            {
                                "configurable": {
                                    "thread_id": value[0],
                                    "thread_ts": value[1],
                                }
                            },
                            self.serde.loads(value[3]),
                            self.serde.loads(value[4])
                            if value[4] is not None
                            else {},
                            (
                                {
                                    "configurable": {
                                        "thread_id": value[0],
                                        "thread_ts": value[2],
                                    }
                                }
                                if value[2]
                                else None
                            ),
                        )
        return None

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        print(">>>", config)
        thread_id = config["configurable"]["thread_id"]
        thread_ts = config["configurable"].get("thread_ts")
        async with self._get_async_connection() as conn:
            async with conn.cursor() as cur:
                if thread_ts:
                    await cur.execute(
                        "SELECT checkpoint, metadata, parent_ts "
                        "FROM checkpoints "
                        "WHERE thread_id = %(thread_id)s AND thread_ts = %(thread_ts)s",
                        {
                            "thread_id": thread_id,
                            "thread_ts": thread_ts,
                        },
                    )
                    if value := await cur.fetchone():
                        return CheckpointTuple(
                            config,
                            self.serde.loads(value[0]),
                            self.serde.loads(value[1]) if value[1] is not None else {},
                            {
                                "configurable": {
                                    "thread_id": thread_id,
                                    "thread_ts": value[2],
                                }
                            }
                            if value[2]
                            else None,
                        )
                else:
                    await cur.execute(
                        "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata "
                        "FROM checkpoints "
                        "WHERE thread_id = %(thread_id)s "
                        "ORDER BY thread_ts DESC LIMIT 1",
                        {
                            "thread_id": thread_id,
                        },
                    )
                    if value := await cur.fetchone():
                        print("value", value)
                        return CheckpointTuple(
                            {
                                "configurable": {
                                    "thread_id": value[0],
                                    "thread_ts": value[1],
                                }
                            },
                            self.serde.loads(value[3]),
                            self.serde.loads(value[4])
                            if value[4] is not None
                            else {},
                            (
                                {
                                    "configurable": {
                                        "thread_id": value[0],
                                        "thread_ts": value[2],
                                    }
                                }
                                if value[2]
                                else None
                            ),
                        )
        return None

    def search(
        self,
        metadata_filter: CheckpointMetadata,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Generator[CheckpointTuple, None, None]:
        with self._get_sync_connection() as conn:
            with conn.cursor() as cur:
                SELECT = "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints "
                WHERE, params = search_where(metadata_filter, before)
                ORDER_BY = "ORDER BY thread_ts DESC "
                LIMIT = f"LIMIT {limit}" if limit else ""

                query = f"{SELECT}{WHERE}{ORDER_BY}{LIMIT}"
                cur.execute(query, params)
                for value in cur:
                    yield CheckpointTuple(
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[1],
                            }
                        },
                        self.serde.loads(value[3]),
                        self.serde.loads(value[4]) if value[4] is not None else {},
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[2],
                            }
                        }
                        if value[2]
                        else None,
                    )

    async def asearch(
        self,
        metadata_filter: CheckpointMetadata,
        *,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]:
        async with self._get_async_connection() as conn:
            async with conn.cursor() as cur:
                SELECT = "SELECT thread_id, thread_ts, parent_ts, checkpoint, metadata FROM checkpoints "
                WHERE, params = search_where(metadata_filter, before)
                ORDER_BY = "ORDER BY thread_ts DESC "
                LIMIT = f"LIMIT {limit}" if limit else ""

                query = f"{SELECT}{WHERE}{ORDER_BY}{LIMIT}"
                await cur.execute(query, params)
                async for value in cur:
                    yield CheckpointTuple(
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[1],
                            }
                        },
                        self.serde.loads(value[3]),
                        self.serde.loads(value[4]) if value[4] is not None else {},
                        {
                            "configurable": {
                                "thread_id": value[0],
                                "thread_ts": value[2],
                            }
                        }
                        if value[2]
                        else None,
                    )
