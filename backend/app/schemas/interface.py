"""Interface schemas for request/response validation."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ============== Interface Folder Schemas ==============

class InterfaceFolderBase(BaseModel):
    """Base interface folder schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Folder name")


class InterfaceFolderCreate(InterfaceFolderBase):
    """Schema for creating an interface folder."""

    project_id: int = Field(..., description="Project ID")
    parent_id: int | None = Field(None, description="Parent folder ID")


class InterfaceFolderUpdate(BaseModel):
    """Schema for updating an interface folder."""

    name: str | None = Field(None, min_length=1, max_length=100)


class InterfaceFolderResponse(InterfaceFolderBase):
    """Schema for interface folder response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    parent_id: int | None
    sort_order: int


# ============== Interface Schemas ==============

class InterfaceBase(BaseModel):
    """Base interface schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Interface name")
    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH)$", description="HTTP method")
    path: str = Field(..., min_length=1, max_length=500, description="Request path")


class InterfaceCreate(InterfaceBase):
    """Schema for creating an interface."""

    project_id: int = Field(..., description="Project ID")
    folder_id: int | None = Field(None, description="Folder ID")
    headers: dict[str, Any] | None = Field(default_factory=dict, description="Request headers")
    params: dict[str, Any] | None = Field(default_factory=dict, description="Query parameters")
    body: dict[str, Any] | None = Field(default_factory=dict, description="Request body")
    body_type: str = Field(default="json", pattern="^(json|form-data|raw)$", description="Body type")


class InterfaceUpdate(BaseModel):
    """Schema for updating an interface."""

    name: str | None = Field(None, min_length=1, max_length=200)
    method: str | None = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    path: str | None = Field(None, min_length=1, max_length=500)
    folder_id: int | None = None
    headers: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    body: dict[str, Any] | None = None
    body_type: str | None = Field(None, pattern="^(json|form-data|raw)$")


class InterfaceResponse(InterfaceBase):
    """Schema for interface response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    folder_id: int | None
    headers: dict[str, Any] | None
    params: dict[str, Any] | None
    body: dict[str, Any] | None
    body_type: str
    sort_order: int


# ============== Tree Structure ==============

class InterfaceTreeNode(BaseModel):
    """Schema for interface tree node."""

    id: int
    name: str
    type: str  # "folder" or "interface"
    method: str | None = None
    path: str | None = None
    folder_id: int | None = None
    parent_id: int | None = None
    sort_order: int
    children: list["InterfaceTreeNode"] = Field(default_factory=list)


# Enable forward reference
InterfaceTreeNode.model_rebuild()


# ============== Batch Operations ==============

class InterfaceReorderRequest(BaseModel):
    """Schema for batch reordering interfaces."""

    updates: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="List of {id, sort_order} updates"
    )


class CurlImportRequest(BaseModel):
    """Schema for importing cURL command."""

    curl: str = Field(..., description="cURL command string")
    project_id: int = Field(..., description="Project ID")
    folder_id: int | None = Field(None, description="Target folder ID")
