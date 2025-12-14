from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from nlq.schemas import QueryIntent
from nlq.sql_builder import build_scalar_query

async def execute_intent(session: AsyncSession, intent: QueryIntent) -> int:
    q = build_scalar_query(intent)
    result = await session.execute(q)
    value = result.scalar_one()
    return int(value)
