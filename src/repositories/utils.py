import abc
from contextlib import asynccontextmanager
from typing import TypeVar, AsyncIterator, Callable, AsyncContextManager

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

T = TypeVar("T", covariant=True)


class SqlAlchemyAcquire[T](abc.ABC):
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
        async with self._get_session() as session:
            yield self._repo_factory(session)


class AcquireTxRepository(SqlAlchemyAcquire[T]):
    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory.begin() as session:
            yield session


class AcquireRepository(SqlAlchemyAcquire[T]):
    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self._session_factory() as session:
            yield session
