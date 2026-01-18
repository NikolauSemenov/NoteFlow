import abc
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import AsyncContextManager, AsyncIterator, Callable, TypeVar

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

T = TypeVar("T", covariant=True)

_session_cv: ContextVar[dict[AsyncEngine, AsyncConnection]] = ContextVar("_session_cv")
_tx_session_cv: ContextVar[dict[AsyncEngine, AsyncConnection]] = ContextVar("_tx_session_cv")


class SqlAlchemyAcquire[T](abc.ABC):
    """
    Данная фабрика позволяет переиспользовать AsyncConnection в рамках одного клиентского запроса

    async with self._first_repo() as first_repo:
        async with self._second_repo() as second_repo:
            ...
    В этом случае будет использоваться один экземпляр AsyncConnection
    """

    SESSION_STORAGE: ContextVar[dict[AsyncEngine, AsyncConnection]]

    def __init__(
        self,
        engine: AsyncEngine,
        repo_factory: Callable[[AsyncConnection], T],
    ) -> None:
        self._engine_factory = engine
        self._repo_factory = repo_factory

    @abc.abstractmethod
    def _get_connection(self) -> AsyncContextManager[AsyncConnection]:
        raise NotImplementedError

    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[T]:
        storage = self.SESSION_STORAGE.get({})

        storage_conn = storage.get(self._engine_factory)
        if storage_conn is None:
            async with self._get_connection() as conn:
                token = self.SESSION_STORAGE.set({**storage, self._engine_factory: conn})
                try:
                    yield self._repo_factory(conn)
                finally:
                    self.SESSION_STORAGE.reset(token)
        else:
            yield self._repo_factory(storage_conn)


class AcquireTxRepository(SqlAlchemyAcquire[T]):
    """Фабрика для транзакционных репозиториев."""

    SESSION_STORAGE = _tx_session_cv

    @asynccontextmanager
    async def _get_connection(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine_factory.begin() as conn:
            yield conn


class AcquireRepository(SqlAlchemyAcquire[T]):
    """Фабрика для не-транзакционных (read-only) репозиториев."""

    SESSION_STORAGE = _session_cv

    @asynccontextmanager
    async def _get_connection(self) -> AsyncIterator[AsyncConnection]:
        async with self._engine_factory.connect() as conn:
            yield conn
