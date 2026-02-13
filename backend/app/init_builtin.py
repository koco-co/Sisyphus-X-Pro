"""Initialize built-in keywords in database."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.builtin_keywords import BUILTIN_KEYWORDS
from app.models.keyword import Keyword


async def init_builtin_keywords(db: AsyncSession) -> int:
    """Initialize built-in keywords in database.

    This function checks if built-in keywords exist, and creates/updates them
    to ensure the database has the latest versions.

    Args:
        db: Database session

    Returns:
        Number of keywords initialized
    """
    count = 0

    for keyword_data in BUILTIN_KEYWORDS:
        # Check if keyword already exists
        result = await db.execute(
            select(Keyword).where(
                Keyword.method_name == keyword_data["method_name"],
                Keyword.is_builtin.is_(True),
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing builtin keyword
            existing.name = keyword_data["name"]
            existing.type = keyword_data["type"]
            existing.code = keyword_data["code"]
            existing.params = keyword_data["params"]  # type: ignore[arg-type]
        else:
            # Create new builtin keyword
            keyword = Keyword(
                type=keyword_data["type"],
                name=keyword_data["name"],
                method_name=keyword_data["method_name"],
                code=keyword_data["code"],
                params=keyword_data["params"],  # type: ignore[arg-type]
                is_builtin=True,
                is_enabled=True,
            )
            db.add(keyword)

        count += 1

    await db.flush()
    return count
