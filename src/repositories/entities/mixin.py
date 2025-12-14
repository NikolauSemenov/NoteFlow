from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import Executable, Result
from sqlalchemy.ext.asyncio import AsyncSession

RowType = TypeVar("RowType", bound=BaseModel)
ScalarType = TypeVar("ScalarType")


class SelectableMixIn:
    session: AsyncSession

    async def execute(self, query: Executable, **params: Any) -> Result[Any]:
        return await self.session.execute(query, params)

    async def many_row_result(self, query: Executable, schema: type[RowType], **params: Any) -> list[RowType]:
        result = await self.session.execute(query, params)
        return [schema.model_validate(row, from_attributes=True) for row in result.scalars().all()]

    async def one_row_result(self, query: Executable, schema: type[RowType], **params: Any) -> RowType | None:
        if result := await self.session.scalar(query, params):
            return schema.model_validate(result, from_attributes=True)
        return None
