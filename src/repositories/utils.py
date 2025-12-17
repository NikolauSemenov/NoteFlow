import abc
from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import TypeVar, AsyncIterator, Callable, AsyncContextManager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

T = TypeVar("T", covariant=True)

_session_cv: ContextVar[dict[async_sessionmaker[AsyncSession], AsyncSession]] = ContextVar("_session_cv")


class SqlAlchemyAcquire[T](abc.ABC):
    """
    Данная фабрика позволяет переиспользовать AsyncSession в рамках одного клиентского запроса

    async with self._first_repo() as first_repo:
        async with self._second_repo() as second_repo:
            ...
    В этом случае будет использоваться один экземпляр AsyncSession
    """
    SESSION_STORAGE: ContextVar[dict[async_sessionmaker[AsyncSession], AsyncSession]]

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repo_factory: Callable[[AsyncSession], T],
    ) -> None:
        self._session_factory = session_factory
        self._repo_factory = repo_factory

    @abc.abstractmethod
    def _get_session(self) -> AsyncContextManager[AsyncSession]:
        raise NotImplementedError

    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[T]:
        storage = self.SESSION_STORAGE.get({})

        session = storage.get(self._session_factory)
        if session is None:
            async with self._get_session() as session:
                token = self.SESSION_STORAGE.set({**storage, self._session_factory: session})
                try:
                    yield self._repo_factory(session)
                finally:
                    self.SESSION_STORAGE.reset(token)
        else:
            yield self._repo_factory(session)


class AcquireTxRepository(SqlAlchemyAcquire[T]):
    SESSION_STORAGE = _session_cv

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory.begin() as session:
            yield session


class AcquireRepository(SqlAlchemyAcquire[T]):
    SESSION_STORAGE = _session_cv

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            yield session
