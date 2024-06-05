import json
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    CheckpointMetadata,
)


def _metadata_predicate(
    metadata_filter: CheckpointMetadata,
) -> tuple[str, tuple[Any, ...]]:
    def _where_value(query_key: str, query_value: Any) -> tuple[str, Any]:
        if query_value is None:
            return (f"IS %({query_key})s", None)
        elif (
            isinstance(query_value, str)
            or isinstance(query_value, int)
            or isinstance(query_value, float)
        ):
            return (f"= %({query_key})s", query_value)
        elif isinstance(query_value, bool):
            return (f"= %({query_key})s", 1 if query_value else 0)
        elif isinstance(query_value, dict) or isinstance(query_value, list):
            return (f"= %({query_key})s", json.dumps(query_value, separators=(",", ":")))
        else:
            return (f"= %({query_key})s", str(query_value))

    predicate = ""
    param_values = ()

    for query_key, query_value in metadata_filter.items():
        operator, param_value = _where_value(query_key, query_value)
        predicate += (
            f"CAST(metadata AS JSON)->>'{query_key}' {operator} AND"
        )
        param_values += (param_value,)

    if predicate != "":
        predicate = predicate[:-4]

    return (predicate, param_values)


def search_where(
    metadata_filter: CheckpointMetadata,
    before: RunnableConfig | None = None,
) -> tuple[str, tuple[Any, ...]]:
    where = "WHERE "
    param_values = ()

    metadata_predicate, metadata_values = _metadata_predicate(metadata_filter)
    if metadata_predicate != "":
        where += metadata_predicate
        param_values += metadata_values

    if before is not None:
        if metadata_predicate != "":
            where += "AND thread_ts < %(thread_ts)s "
        else:
            where += "thread_ts < %(thread_ts)s "

        param_values += (before["configurable"]["thread_ts"],)

    if where == "WHERE ":
        # no predicates, return an empty WHERE clause string
        return ("", ())
    else:
        return (where, param_values)
