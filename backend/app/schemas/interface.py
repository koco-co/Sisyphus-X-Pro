"""Interface schemas for request/response validation."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ============== Interface Folder Schemas ==============

class InterfaceFolderBase(BaseModel):
    """Base interface folder schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Folder name")


class InterfaceFolderCreate(InterfaceFolderBase):
    """Schema for creating an interface folder."""

    project_id: int = Field(..., description="Project ID")
    parent_id: Optional[int] = Field(None, description="Parent folder ID")


class InterfaceFolderUpdate(BaseModel):
    """Schema for updating an interface folder."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)


class InterfaceFolderResponse(InterfaceFolderBase):
    """Schema for interface folder response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    parent_id: Optional[int]
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
    folder_id: Optional[int] = Field(None, description="Folder ID")
    headers: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Request headers")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Query parameters")
    body: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Request body")
    body_type: str = Field(default="json", pattern="^(json|form-data|raw)$", description="Body type")


class InterfaceUpdate(BaseModel):
    """Schema for updating an interface."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    path: Optional[str] = Field(None, min_length=1, max_length=500)
    folder_id: Optional[int] = None
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    body_type: Optional[str] = Field(None, pattern="^(json|form-data|raw)$")


class InterfaceResponse(InterfaceBase):
    """Schema for interface response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    folder_id: Optional[int]
    headers: Optional[Dict[str, Any]]
    params: Optional[Dict[str, Any]]
    body: Optional[Dict[str, Any]]
    body_type: str
    sort_order: int


# ============== Tree Structure ==============

class InterfaceTreeNode(BaseModel):
    """Schema for interface tree node."""

    id: int
    name: str
    type: str  # "folder" or "interface"
    method: Optional[str] = None
    path: Optional[str] = None
    folder_id: Optional[int] = None
    parent_id: Optional[int] = None
    sort_order: int
    children: List["InterfaceTreeNode"] = Field(default_factory=list)


# Enable forward reference
InterfaceTreeNode.model_rebuild()


# ============== Batch Operations ==============

class InterfaceReorderRequest(BaseModel):
    """Schema for batch reordering interfaces."""

    updates: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="List of {id, sort_order} updates"
    )


class CurlImportRequest(BaseModel):
    """Schema for importing cURL command."""

    curl: str = Field(..., description="cURL command string")
    project_id: int = Field(..., description="Project ID")
    folder_id: Optional[int] = Field(None, description="Target folder ID")
