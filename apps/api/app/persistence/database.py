from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, Protocol


class Cursor(Protocol):
    def execute(
        self, query: str, params: dict[str, Any] | tuple[Any, ...] = ()
    ) -> Any: ...

    def fetchone(self) -> Any: ...


class Connection(Protocol):
    def cursor(self) -> Any: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


class Database:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    @contextmanager
    def connection(self) -> Iterator[Any]:
        import psycopg

        connection = psycopg.connect(self.database_url)
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
