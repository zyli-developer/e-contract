from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.response import PageResult


async def paginate(
    db: AsyncSession,
    query: Select,
    page_no: int = 1,
    page_size: int = 10,
) -> PageResult:
    """通用分页工具"""
    # 查询总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 查询分页数据
    offset = (page_no - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    items = result.scalars().all()

    return PageResult(
        list=items,
        total=total,
        pageNo=page_no,
        pageSize=page_size,
    )
