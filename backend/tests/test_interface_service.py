"""Tests for interface service."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interface import Interface
from app.models.interface_folder import InterfaceFolder
from app.schemas.interface import (
    CurlImportRequest,
    InterfaceCreate,
    InterfaceFolderCreate,
)
from app.services.interface_service import InterfaceService


@pytest.mark.asyncio
async def test_get_interface_tree(db_session: AsyncSession, test_project):
    """Test getting full interface tree."""
    service = InterfaceService(db_session)

    # Create folders
    folder1 = InterfaceFolder(project_id=test_project.id, name="API")
    folder2 = InterfaceFolder(project_id=test_project.id, name="Auth", parent_id=folder1.id)
    db_session.add_all([folder1, folder2])
    await db_session.flush()

    # Create interfaces
    interface1 = Interface(
        project_id=test_project.id,
        folder_id=folder1.id,
        name="Get User",
        method="GET",
        path="/user",
    )
    interface2 = Interface(
        project_id=test_project.id,
        folder_id=folder2.id,
        name="Login",
        method="POST",
        path="/auth/login",
    )
    db_session.add_all([interface1, interface2])
    await db_session.flush()

    # Get tree
    tree = await service.get_interface_tree(test_project.id)

    # Assertions
    assert len(tree) == 1
    assert tree[0].type == "folder"
    assert tree[0].name == "API"
    assert len(tree[0].children) == 2


@pytest.mark.asyncio
async def test_create_folder(db_session: AsyncSession, test_project):
    """Test creating a new folder."""
    service = InterfaceService(db_session)

    folder_in = InterfaceFolderCreate(
        project_id=test_project.id, name="Test Folder", parent_id=None
    )

    folder = await service.create_folder(folder_in)

    assert folder.id is not None
    assert folder.name == "Test Folder"
    assert folder.project_id == test_project.id
    assert folder.parent_id is None


@pytest.mark.asyncio
async def test_create_subfolder(db_session: AsyncSession, test_project):
    """Test creating a subfolder."""
    service = InterfaceService(db_session)

    # Create parent folder
    parent = InterfaceFolder(project_id=test_project.id, name="Parent")
    db_session.add(parent)
    await db_session.flush()

    # Create child folder
    folder_in = InterfaceFolderCreate(
        project_id=test_project.id, name="Child", parent_id=parent.id
    )

    folder = await service.create_folder(folder_in)

    assert folder.parent_id == parent.id


@pytest.mark.asyncio
async def test_create_interface(db_session: AsyncSession, test_project):
    """Test creating a new interface."""
    service = InterfaceService(db_session)

    interface_in = InterfaceCreate(
        project_id=test_project.id,
        name="Create User",
        method="POST",
        path="/users",
        headers={"Content-Type": "application/json"},
        params={},
        body={"name": "test"},
        body_type="json",
    )

    interface = await service.create_interface(interface_in)

    assert interface.id is not None
    assert interface.name == "Create User"
    assert interface.method == "POST"
    assert interface.path == "/users"
    assert interface.headers == {"Content-Type": "application/json"}
    assert interface.body_type == "json"


@pytest.mark.asyncio
async def test_update_interface(db_session: AsyncSession, test_project):
    """Test updating an interface."""
    service = InterfaceService(db_session)

    # Create interface
    interface = Interface(
        project_id=test_project.id,
        name="Old Name",
        method="GET",
        path="/old",
    )
    db_session.add(interface)
    await db_session.flush()

    # Update interface
    update_data = InterfaceUpdate(name="New Name", path="/new")
    updated = await service.update_interface(interface.id, update_data)

    assert updated is not None
    assert updated.name == "New Name"
    assert updated.path == "/new"
    assert updated.method == "GET"  # Unchanged


@pytest.mark.asyncio
async def test_delete_interface(db_session: AsyncSession, test_project):
    """Test deleting an interface."""
    service = InterfaceService(db_session)

    # Create interface
    interface = Interface(
        project_id=test_project.id,
        name="To Delete",
        method="GET",
        path="/delete",
    )
    db_session.add(interface)
    await db_session.flush()
    interface_id = interface.id

    # Delete interface
    success = await service.delete_interface(interface_id)

    assert success is True

    # Verify it's deleted
    result = await service.get_interface_by_id(interface_id)
    assert result is None


@pytest.mark.asyncio
async def test_import_from_curl_post(db_session: AsyncSession, test_project):
    """Test importing interface from cURL (POST request)."""
    service = InterfaceService(db_session)

    curl_command = """curl -X POST https://api.example.com/users \\
      -H "Content-Type: application/json" \\
      -d '{"name":"test","email":"test@example.com"}'"""

    curl_in = CurlImportRequest(
        curl=curl_command, project_id=test_project.id, folder_id=None
    )

    interface = await service.import_from_curl(curl_in)

    assert interface.method == "POST"
    assert interface.path == "/users"
    assert interface.headers.get("Content-Type") == "application/json"
    assert interface.body.get("name") == "test"
    assert interface.body.get("email") == "test@example.com"
    assert interface.body_type == "json"


@pytest.mark.asyncio
async def test_import_from_curl_get(db_session: AsyncSession, test_project):
    """Test importing interface from cURL (GET request)."""
    service = InterfaceService(db_session)

    curl_command = """curl 'https://api.example.com/users?page=1&limit=10' \\
      -H 'Authorization: Bearer token123'"""

    curl_in = CurlImportRequest(
        curl=curl_command, project_id=test_project.id, folder_id=None
    )

    interface = await service.import_from_curl(curl_in)

    assert interface.method == "GET"
    assert interface.path == "/users"
    assert interface.params.get("page") == "1"
    assert interface.params.get("limit") == "10"
    assert interface.headers.get("Authorization") == "Bearer token123"


@pytest.mark.asyncio
async def test_import_from_curl_invalid(db_session: AsyncSession, test_project):
    """Test importing invalid cURL command."""
    service = InterfaceService(db_session)

    curl_in = CurlImportRequest(
        curl="not a curl command", project_id=test_project.id, folder_id=None
    )

    with pytest.raises(ValueError, match="Invalid cURL command"):
        await service.import_from_curl(curl_in)


@pytest.mark.asyncio
async def test_batch_reorder(db_session: AsyncSession, test_project):
    """Test batch reordering interfaces and folders."""
    service = InterfaceService(db_session)

    # Create interfaces
    interface1 = Interface(
        project_id=test_project.id, name="Interface 1", method="GET", path="/1"
    )
    interface2 = Interface(
        project_id=test_project.id, name="Interface 2", method="GET", path="/2"
    )
    db_session.add_all([interface1, interface2])
    await db_session.flush()

    # Batch reorder
    reorder_request = InterfaceReorderRequest(
        updates=[
            {"id": interface1.id, "sort_order": 10},
            {"id": interface2.id, "sort_order": 20},
        ]
    )

    result = await service.batch_reorder(reorder_request)

    assert result["updated_count"] == 2

    # Refresh and verify
    await db_session.refresh(interface1)
    await db_session.refresh(interface2)

    assert interface1.sort_order == 10
    assert interface2.sort_order == 20
