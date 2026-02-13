"""Unit tests for DatabaseConfig service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database_config import DatabaseConfig
from app.models.user import User
from app.models.project import Project
from app.schemas.database_config import (
    DatabaseConfigCreate,
    DatabaseConfigUpdate,
)
from app.services.db_config_service import DatabaseConfigService


@pytest.mark.asyncio
async def test_create_db_config(
    db_session: AsyncSession, test_project: Project
):
    """Test creating a database config."""
    service = DatabaseConfigService(db_session)
    config_in = DatabaseConfigCreate(
        name="Test DB",
        variable_name="test_db",
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="testdb",
        username="testuser",
        password="testpass",
    )

    config = await service.create_db_config(test_project.id, config_in)

    assert config.id is not None
    assert config.name == "Test DB"
    assert config.variable_name == "test_db"
    assert config.db_type == "postgresql"


@pytest.mark.asyncio
async def test_create_db_config_duplicate_variable(
    db_session: AsyncSession, test_project: Project
):
    """Test creating config with duplicate variable_name raises error."""
    service = DatabaseConfigService(db_session)
    config_in = DatabaseConfigCreate(
        name="Test DB",
        variable_name="test_db",
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="testdb",
        username="testuser",
        password="testpass",
    )

    # Create first config
    await service.create_db_config(test_project.id, config_in)

    # Try to create duplicate
    with pytest.raises(ValueError, match="Variable name already exists"):
        await service.create_db_config(test_project.id, config_in)


@pytest.mark.asyncio
async def test_list_db_configs(
    db_session: AsyncSession, test_project: Project
):
    """Test listing database configs."""
    service = DatabaseConfigService(db_session)

    # Create multiple configs
    await service.create_db_config(
        test_project.id,
        DatabaseConfigCreate(
            name="DB1",
            variable_name="db1",
            db_type="mysql",
            host="localhost",
            port=3306,
            database="db1",
            username="user",
            password="pass",
        ),
    )
    await service.create_db_config(
        test_project.id,
        DatabaseConfigCreate(
            name="DB2",
            variable_name="db2",
            db_type="postgresql",
            host="localhost",
            port=5432,
            database="db2",
            username="user",
            password="pass",
        ),
    )

    configs, total = await service.list_db_configs(test_project.id)

    assert total == 2
    assert len(configs) == 2


@pytest.mark.asyncio
async def test_update_db_config(
    db_session: AsyncSession, test_project: Project
):
    """Test updating a database config."""
    service = DatabaseConfigService(db_session)
    config_in = DatabaseConfigCreate(
        name="Test DB",
        variable_name="test_db",
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="testdb",
        username="testuser",
        password="testpass",
    )

    created = await service.create_db_config(test_project.id, config_in)
    update_data = DatabaseConfigUpdate(name="Updated DB", host="newhost")

    updated = await service.update_db_config(created.id, update_data)

    assert updated.id == created.id
    assert updated.name == "Updated DB"
    assert updated.host == "newhost"


@pytest.mark.asyncio
async def test_delete_db_config(
    db_session: AsyncSession, test_project: Project
):
    """Test deleting a database config."""
    service = DatabaseConfigService(db_session)
    config_in = DatabaseConfigCreate(
        name="Test DB",
        variable_name="test_db",
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="testdb",
        username="testuser",
        password="testpass",
    )

    created = await service.create_db_config(test_project.id, config_in)
    deleted = await service.delete_db_config(created.id)

    assert deleted is True

    # Verify config is deleted
    config = await service.get_db_config_by_id(created.id)
    assert config is None


@pytest.mark.asyncio
async def test_toggle_enabled(
    db_session: AsyncSession, test_project: Project
):
    """Test toggling database config enabled status."""
    service = DatabaseConfigService(db_session)
    config_in = DatabaseConfigCreate(
        name="Test DB",
        variable_name="test_db",
        db_type="postgresql",
        host="localhost",
        port=5432,
        database="testdb",
        username="testuser",
        password="testpass",
    )

    created = await service.create_db_config(test_project.id, config_in)

    # Disable
    disabled = await service.toggle_enabled(created.id, False)
    assert disabled.is_enabled is False

    # Enable
    enabled = await service.toggle_enabled(created.id, True)
    assert enabled.is_enabled is True
