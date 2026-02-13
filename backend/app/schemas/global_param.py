"""Global parameter-related schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GlobalParamBase(BaseModel):
    """Base global parameter schema."""

    class_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="类名(目录分组,如StringUtils/TimeUtils/RandomUtils)",
    )
    method_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="方法名(字母开头,仅含字母数字下划线)",
    )
    description: str = Field(..., min_length=1, description="功能描述")
    code: str = Field(..., min_length=1, description="Python 代码块")
    params_in: List[Dict[str, Any]] = Field(
        default=[], description="输入参数列表 [{name, type, description}]"
    )
    params_out: List[Dict[str, Any]] = Field(
        default=[], description="输出参数列表 [{type, description}]"
    )


class GlobalParamCreate(GlobalParamBase):
    """Global parameter creation schema."""

    pass


class GlobalParamUpdate(BaseModel):
    """Global parameter update schema."""

    class_name: Optional[str] = Field(None, min_length=1, max_length=200)
    method_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    code: Optional[str] = Field(None, min_length=1)
    params_in: Optional[List[Dict[str, Any]]] = None
    params_out: Optional[List[Dict[str, Any]]] = None


class GlobalParamResponse(GlobalParamBase):
    """Global parameter response schema."""

    id: int
    is_builtin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GlobalParamListResponse(BaseModel):
    """Paginated global parameter list response."""

    items: List[GlobalParamResponse]
    total: int
    page: int
    pageSize: int  # noqa: N815


class GlobalParamGroupedResponse(BaseModel):
    """Global parameters grouped by class name."""

    params: Dict[str, List[GlobalParamResponse]]


class FunctionParseRequest(BaseModel):
    """Function parse request schema."""

    text: str = Field(..., description="包含{{函数调用}}的文本")
    context: Dict[str, Any] = Field(default={}, description="执行上下文变量")


class FunctionParseResponse(BaseModel):
    """Function parse response schema."""

    original_text: str
    parsed_text: str
    functions_called: List[str] = Field(description="调用的函数列表")
    success: bool
    error: Optional[str] = None
