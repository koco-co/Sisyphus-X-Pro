"""Tests for built-in keywords initialization."""

import pytest

from app.builtin_keywords import BUILTIN_KEYWORDS
from app.init_builtin import init_builtin_keywords
from app.models.keyword import Keyword
from sqlalchemy import select


@pytest.mark.asyncio
async def test_init_builtin_keywords_creates_records(db):
    """Test that init_builtin_keywords creates built-in keyword records."""
    # Initialize built-in keywords
    count = await init_builtin_keywords(db)
    await db.commit()

    # Should initialize 5 keywords
    assert count == 5

    # Verify records exist in database
    result = await db.execute(
        select(Keyword).where(Keyword.is_builtin.is_(True))
    )
    builtin_keywords = result.scalars().all()

    assert len(builtin_keywords) == 5

    # Verify specific keywords
    method_names = {k.method_name for k in builtin_keywords}
    expected = {"http_request", "assert_response", "extract_variable", "db_query", "db_update"}
    assert method_names == expected


@pytest.mark.asyncio
async def test_builtin_keywords_params(db):
    """Test that built-in keywords have correct parameters."""
    await init_builtin_keywords(db)
    await db.commit()

    # Check http_request keyword
    result = await db.execute(
        select(Keyword).where(Keyword.method_name == "http_request")
    )
    keyword = result.scalar_one()

    assert keyword.name == "HTTP 请求"
    assert keyword.type == "http_request"
    assert keyword.is_builtin is True
    assert keyword.is_enabled is True
    assert len(keyword.params) == 5

    param_names = [p["name"] for p in keyword.params]
    assert "url" in param_names
    assert "method" in param_names
    assert "headers" in param_names


@pytest.mark.asyncio
async def test_init_builtin_keywords_is_idempotent(db):
    """Test that running init_builtin_keywords twice is idempotent."""
    # First run
    count1 = await init_builtin_keywords(db)
    await db.commit()

    # Second run
    count2 = await init_builtin_keywords(db)
    await db.commit()

    # Both should process same number of keywords
    assert count1 == count2 == 5

    # But total count should still be 5 (no duplicates)
    result = await db.execute(
        select(Keyword).where(Keyword.is_builtin.is_(True))
    )
    assert len(result.scalars().all()) == 5


@pytest.mark.asyncio
async def test_builtin_keyword_code_validity(db):
    """Test that built-in keywords have valid Python code."""
    await init_builtin_keywords(db)
    await db.commit()

    result = await db.execute(
        select(Keyword).where(Keyword.is_builtin.is_(True))
    )
    keywords = result.scalars().all()

    for keyword in keywords:
        # Code should not be empty
        assert keyword.code
        assert len(keyword.code) > 100

        # Should contain function definition
        assert f"def {keyword.method_name}(" in keyword.code

        # Should contain docstring
        assert '"""' in keyword.code or "'''" in keyword.code
