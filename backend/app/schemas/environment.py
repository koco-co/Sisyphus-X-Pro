"""Environment schemas for request/response validation."""


from pydantic import BaseModel, ConfigDict, Field

# ============== Environment Schemas ==============

class EnvironmentBase(BaseModel):
    """Base environment schema."""

    name: str = Field(..., min_length=1, max_length=100, description="Environment name")
    base_url: str = Field(..., max_length=500, description="Base URL for the environment")


class EnvironmentCreate(EnvironmentBase):
    """Schema for creating an environment."""

    project_id: int = Field(..., description="Project ID")


class EnvironmentUpdate(BaseModel):
    """Schema for updating an environment."""

    name: str | None = Field(None, min_length=1, max_length=100)
    base_url: str | None = Field(None, max_length=500)


class EnvironmentResponse(EnvironmentBase):
    """Schema for environment response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


# ============== Environment Variable Schemas ==============

class EnvVariableBase(BaseModel):
    """Base environment variable schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Variable name")
    value: str = Field(..., description="Variable value")
    description: str | None = Field(None, max_length=500, description="Variable description")


class EnvVariableCreate(EnvVariableBase):
    """Schema for creating an environment variable."""

    environment_id: int = Field(..., description="Environment ID")


class EnvVariableResponse(EnvVariableBase):
    """Schema for environment variable response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    environment_id: int
    source: str


# ============== Global Variable Schemas ==============

class GlobalVariableBase(BaseModel):
    """Base global variable schema."""

    name: str = Field(..., min_length=1, max_length=200, description="Variable name")
    value: str = Field(..., description="Variable value")
    description: str | None = Field(None, max_length=500, description="Variable description")


class GlobalVariableCreate(GlobalVariableBase):
    """Schema for creating a global variable."""

    project_id: int = Field(..., description="Project ID")


class GlobalVariableUpdate(BaseModel):
    """Schema for updating a global variable."""

    name: str | None = Field(None, min_length=1, max_length=200)
    value: str | None = None
    description: str | None = Field(None, max_length=500)


class GlobalVariableResponse(GlobalVariableBase):
    """Schema for global variable response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    source: str
