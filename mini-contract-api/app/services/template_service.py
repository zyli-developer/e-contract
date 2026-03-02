"""合同模板服务"""
from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessException
from app.core.response import PageResult
from app.models.contract_template import ContractTemplate
from app.schemas.template import TemplateDetailResponse, TemplateResponse
from app.utils.pagination import paginate

# 合同分类
CATEGORIES = [
    {"code": "loan", "name": "借款合同"},
    {"code": "lease", "name": "租赁合同"},
    {"code": "labor", "name": "劳动合同"},
    {"code": "purchase", "name": "采购合同"},
    {"code": "sales", "name": "销售合同"},
    {"code": "other", "name": "其他"},
]


def _to_list_response(t: ContractTemplate) -> dict:
    return TemplateResponse(
        id=t.id,
        name=t.name,
        description=t.description,
        category=t.category,
        image_url=t.image_url,
        use_count=t.use_count,
    ).model_dump()


async def search_templates(
    db: AsyncSession,
    keyword: str | None = None,
    category: str | None = None,
    page_no: int = 1,
    page_size: int = 10,
) -> PageResult:
    """搜索模板（分页 + 分类 + 关键词）"""
    logger.debug("搜索模板: keyword=%s, category=%s, page=%d", keyword, category, page_no)
    query = select(ContractTemplate).where(ContractTemplate.status == 1)

    if category:
        query = query.where(ContractTemplate.category == category)
    if keyword:
        query = query.where(ContractTemplate.name.contains(keyword))

    query = query.order_by(ContractTemplate.use_count.desc(), ContractTemplate.create_time.desc())
    result = await paginate(db, query, page_no, page_size)
    result.list = [_to_list_response(t) for t in result.list]
    return result


async def get_template_detail(db: AsyncSession, template_id: int) -> dict:
    """获取模板详情"""
    logger.debug("获取模板详情: template_id=%d", template_id)
    result = await db.execute(
        select(ContractTemplate).where(ContractTemplate.id == template_id, ContractTemplate.status == 1)
    )
    template = result.scalar_one_or_none()
    if not template:
        logger.warning("模板不存在: template_id=%d", template_id)
        raise BusinessException(code=404, msg="模板不存在")

    return TemplateDetailResponse(
        id=template.id,
        name=template.name,
        description=template.description,
        category=template.category,
        image_url=template.image_url,
        use_count=template.use_count,
        content=template.content,
        variables=template.variables,
        signatories=template.signatories,
    ).model_dump()


async def get_hot_templates(db: AsyncSession, limit: int = 6) -> list:
    """获取热门模板（按使用次数排序）"""
    result = await db.execute(
        select(ContractTemplate)
        .where(ContractTemplate.status == 1)
        .order_by(ContractTemplate.use_count.desc())
        .limit(limit)
    )
    return [_to_list_response(t) for t in result.scalars().all()]


async def get_frequently_used(db: AsyncSession, limit: int = 8) -> list:
    """获取常用模板（同热门，后续可根据用户历史调整）"""
    return await get_hot_templates(db, limit)


async def increment_use_count(db: AsyncSession, template_id: int) -> None:
    """递增使用次数"""
    await db.execute(
        update(ContractTemplate)
        .where(ContractTemplate.id == template_id)
        .values(use_count=ContractTemplate.use_count + 1)
    )
