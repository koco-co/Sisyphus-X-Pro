"""Tests for keyword toggle functionality."""

import pytest

from app.init_builtin import init_builtin_keywords
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordUpdate
from sqlalchemy import select

# Import all models to avoid SA configuration warnings
from app.models import (  # noqa: F401
    database_config,
    environment,
    execution_scenario,
    execution_step,
    global_param,
    global_variable,
    interface,
    interface_folder,
    keyword,
    plan_scenario,
    project,
    scenario,
    scenario_step,
    test_execution,
    test_plan,
    test_report,
    user,
)


@pytest.mark.asyncio
async def test_toggle_keyword_enabled(db):
    """Test toggling keyword enabled status."""
    # Initialize built-in keywords
    await init_builtin_keywords(db)
    await db.commit()

    # Get a keyword
    result = await db.execute(select(Keyword).limit(1))
    keyword = result.scalar_one()

    original_status = keyword.is_enabled

    # Toggle to opposite
    from app.services.keyword_service import KeywordService

    service = KeywordService(db)
    updated = await service.toggle_enabled(keyword.id, not original_status)

    assert updated.is_enabled == (not original_status)


@pytest.mark.asyncio
async def test_toggle_keyword_not_found(db):
    """Test toggling non-existent keyword."""
    from app.services.keyword_service import KeywordService

    service = KeywordService(db)
    result = await service.toggle_enabled(99999, True)

    assert result is None


@pytest.mark.asyncio
async def test_get_enabled_keywords_grouped(db):
    """Test getting enabled keywords grouped by type."""
    # Initialize built-in keywords
    await init_builtin_keywords(db)
    await db.commit()

    from app.services.keyword_service import KeywordService

    service = KeywordService(db)
    grouped = await service.get_enabled_keywords_grouped()

    # Should have at least 3 types
    assert len(grouped) >= 3

    # All keywords should be enabled
    for keyword_type, keywords in grouped.items():
        for keyword in keywords:
            assert keyword.is_enabled is True

    # Check specific types exist
    assert "http_request" in grouped or "database" in grouped
