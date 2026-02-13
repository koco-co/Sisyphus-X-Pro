"""Database configuration schemas."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class DatabaseConfigBase(BaseModel):
    """Base database config schema."""

    name: str = Field(..., min_length=1, max_length=200, description="连接名称")
    variable_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="引用变量名(字母开头,仅含字母数字下划线)",
    )
    db_type: Literal["mysql", "postgresql"] = Field(..., description="数据库类型")
    host: str = Field(..., min_length=1, max_length=255, description="主机地址")
    port: int = Field(..., gt=0, le=65535, description="端口")
    database: str = Field(..., min_length=1, max_length=255, description="数据库名")
    username: str = Field(..., min_length=1, max_length=255, description="用户名")
    password: str = Field(..., min_length=1, max_length=255, description="密码")


class DatabaseConfigCreate(DatabaseConfigBase):
    """Database config creation schema."""

    pass


class DatabaseConfigUpdate(BaseModel):
    """Database config update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    variable_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
    )
    db_type: Optional[Literal["mysql", "postgresql"]] = None
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, gt=0, le=65535)
    database: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=1, max_length=255)


class DatabaseConfigResponse(BaseModel):
    """Database config response schema."""

    id: int
    project_id: int
    name: str
    variable_name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    config_display: str  # Format: host:port/database
    is_connected: bool
    is_enabled: bool
    created_at: datetime
    last_check_at: Optional[datetime] = None
    last_error: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DatabaseConfigListResponse(BaseModel):
    """Paginated database config list response."""

    items: List[DatabaseConfigResponse]
    total: int
    page: int
    pageSize: int  # noqa: N815


class TestConnectionRequest(DatabaseConfigBase):
    """Test connection request schema."""

    pass


class TestConnectionResponse(BaseModel):
    """Test connection response schema."""

    connected: bool
    message: str
