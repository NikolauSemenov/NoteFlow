from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncConnection

RowType = TypeVar("RowType", bound=BaseModel)


class QueryMixIn:
    def __init__(self, conn: AsyncConnection):
        self.conn = conn

    async def execute(self, query: Executable, **params: Any) -> Result[Any]:
        return await self.conn.execute(query, params)

    async def many_row_result(self, query: Executable, schema: type[RowType], **params: Any) -> list[RowType]:
        result = await self.conn.execute(query, params)
        return [schema.model_validate(row, from_attributes=True) for row in result.fetchall()]

    async def first_row_result(self, query: Executable, schema: type[RowType], **params: Any) -> RowType | None:
        result = await self.conn.execute(query, params)
        if row := result.fetchone():
            return schema.model_validate(row, from_attributes=True)
        return None
