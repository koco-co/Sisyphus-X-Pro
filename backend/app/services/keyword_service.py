"""Keyword service for business logic."""


from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate


class KeywordService:
    """Service for keyword-related business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize keyword service.

        Args:
            db: Database session
        """
        self.db = db

    async def list_keywords(
        self,
        skip: int = 0,
        limit: int = 100,
        keyword_type: str | None = None,
        is_builtin: bool | None = None,
        is_enabled: bool | None = None,
    ) -> tuple[list[Keyword], int]:
        """List keywords with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            keyword_type: Filter by keyword type
            is_builtin: Filter by is_builtin flag
            is_enabled: Filter by is_enabled flag

        Returns:
            Tuple of (keywords list, total count)
        """
        # Build base query
        query = select(Keyword)

        # Apply filters
        if keyword_type:
            query = query.where(Keyword.type == keyword_type)
        if is_builtin is not None:
            query = query.where(Keyword.is_builtin == is_builtin)
        if is_enabled is not None:
            query = query.where(Keyword.is_enabled == is_enabled)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit)
        query = query.order_by(Keyword.created_at.desc())

        result = await self.db.execute(query)
        keywords = result.scalars().all()

        return list(keywords), total

    async def get_keyword_by_id(self, keyword_id: int) -> Keyword | None:
        """Get keyword by ID.

        Args:
            keyword_id: Keyword ID

        Returns:
            Keyword instance or None if not found
        """
        result = await self.db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        return result.scalar_one_or_none()

    async def create_keyword(
        self, keyword_in: KeywordCreate
    ) -> Keyword:
        """Create new keyword.

        Args:
            keyword_in: Keyword creation data

        Returns:
            Created keyword instance

        Raises:
            ValueError: If method_name already exists
        """
        # Check if method_name already exists
        existing = await self.db.execute(
            select(Keyword).where(Keyword.method_name == keyword_in.method_name)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Method name already exists")

        # Create keyword
        keyword = Keyword(
            type=keyword_in.type,
            name=keyword_in.name,
            method_name=keyword_in.method_name,
            code=keyword_in.code,
            params=keyword_in.params,  # type: ignore[arg-type]
            is_builtin=False,  # User-created keywords are never builtin
            is_enabled=True,
        )
        self.db.add(keyword)
        await self.db.flush()
        await self.db.refresh(keyword)
        return keyword

    async def update_keyword(
        self, keyword_id: int, keyword_in: KeywordUpdate
    ) -> Keyword | None:
        """Update keyword.

        Args:
            keyword_id: Keyword ID
            keyword_in: Keyword update data

        Returns:
            Updated keyword instance or None if not found

        Raises:
            ValueError: If keyword is builtin or method_name conflict
        """
        keyword = await self.get_keyword_by_id(keyword_id)
        if not keyword:
            return None

        # Check if builtin
        if keyword.is_builtin:
            raise ValueError("Built-in keywords cannot be modified")

        # Check method_name uniqueness if changed
        if keyword_in.method_name and keyword_in.method_name != keyword.method_name:
            existing = await self.db.execute(
                select(Keyword).where(
                    Keyword.method_name == keyword_in.method_name,
                    Keyword.id != keyword_id,
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError("Method name already exists")

        # Update fields
        update_data = keyword_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "params" and value is not None:
                setattr(keyword, field, value)  # type: ignore[arg-type]
            elif value is not None:
                setattr(keyword, field, value)

        await self.db.flush()
        await self.db.refresh(keyword)
        return keyword

    async def delete_keyword(self, keyword_id: int) -> bool:
        """Delete keyword.

        Args:
            keyword_id: Keyword ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If keyword is builtin
        """
        keyword = await self.get_keyword_by_id(keyword_id)
        if not keyword:
            return False

        # Check if builtin
        if keyword.is_builtin:
            raise ValueError("Built-in keywords cannot be deleted")

        await self.db.delete(keyword)
        await self.db.flush()
        return True

    async def toggle_enabled(self, keyword_id: int, is_enabled: bool) -> Keyword | None:
        """Toggle keyword enabled status.

        Args:
            keyword_id: Keyword ID
            is_enabled: New enabled status

        Returns:
            Updated keyword or None if not found
        """
        keyword = await self.get_keyword_by_id(keyword_id)
        if not keyword:
            return None

        keyword.is_enabled = is_enabled
        await self.db.flush()
        await self.db.refresh(keyword)
        return keyword

    async def get_enabled_keywords_grouped(self) -> dict[str, list[Keyword]]:
        """Get all enabled keywords grouped by type.

        Returns:
            Dictionary mapping type to list of keywords
        """
        result = await self.db.execute(
            select(Keyword)
            .where(Keyword.is_enabled.is_(True))
            .order_by(Keyword.type, Keyword.name)
        )
        keywords = result.scalars().all()

        # Group by type
        grouped: dict[str, list[Keyword]] = {}
        for keyword in keywords:
            if keyword.type not in grouped:
                grouped[keyword.type] = []
            grouped[keyword.type].append(keyword)

        return grouped
