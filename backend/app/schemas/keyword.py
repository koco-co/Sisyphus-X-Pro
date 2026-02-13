"""Keyword-related schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KeywordBase(BaseModel):
    """Base keyword schema."""

    type: str = Field(..., min_length=1, max_length=50, description="关键字类型")
    name: str = Field(..., min_length=1, max_length=200, description="关键字名称")
    method_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="方法名(字母开头,仅含字母数字下划线)",
    )
    code: str = Field(..., min_length=1, description="Python 代码块")
    params: list[dict[str, Any]] = Field(
        default=[], description="参数列表 [{name, description}]"
    )


class KeywordCreate(KeywordBase):
    """Keyword creation schema."""

    pass


class KeywordUpdate(BaseModel):
    """Keyword update schema."""

    type: str | None = Field(None, min_length=1, max_length=50)
    name: str | None = Field(None, min_length=1, max_length=200)
    method_name: str | None = Field(None, min_length=1, max_length=200)
    code: str | None = Field(None, min_length=1)
    params: list[dict[str, Any]] | None = None


class KeywordResponse(KeywordBase):
    """Keyword response schema."""

    id: int
    is_builtin: bool
    is_enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KeywordListResponse(BaseModel):
    """Paginated keyword list response."""

    items: list[KeywordResponse]
    total: int
    page: int
    pageSize: int  # noqa: N815


class KeywordEnabledResponse(BaseModel):
    """Enabled keywords grouped by type."""

    keywords: dict[str, list[KeywordResponse]]


class DocstringParseRequest(BaseModel):
    """Request for parsing Python code docstring."""

    code: str = Field(..., min_length=1, description="Python 代码")


class DocstringParam(BaseModel):
    """Parameter extracted from docstring."""

    name: str
    type: str | None = None
    description: str = ""
    default: str | None = None


class DocstringParseResponse(BaseModel):
    """Response from docstring parsing."""

    function_name: str | None = None
    params: list[DocstringParam] = []
    description: str = ""
    error: str | None = None
