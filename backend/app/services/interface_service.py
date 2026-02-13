"""Interface service for business logic."""

import shlex
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interface import Interface
from app.models.interface_folder import InterfaceFolder
from app.schemas.interface import (
    CurlImportRequest,
    InterfaceCreate,
    InterfaceFolderCreate,
    InterfaceFolderUpdate,
    InterfaceReorderRequest,
    InterfaceTreeNode,
    InterfaceUpdate,
)


class InterfaceService:
    """Service for interface-related business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize interface service.

        Args:
            db: Database session
        """
        self.db = db

    # ============== Tree Structure ==============

    async def get_interface_tree(self, project_id: int) -> List[InterfaceTreeNode]:
        """Get full interface tree for a project.

        Args:
            project_id: Project ID

        Returns:
            List of tree nodes (folders and interfaces)
        """
        # Get all folders
        folder_result = await self.db.execute(
            select(InterfaceFolder)
            .where(InterfaceFolder.project_id == project_id)
            .order_by(InterfaceFolder.sort_order, InterfaceFolder.id)
        )
        folders = folder_result.scalars().all()

        # Get all interfaces
        interface_result = await self.db.execute(
            select(Interface)
            .where(Interface.project_id == project_id)
            .order_by(Interface.sort_order, Interface.id)
        )
        interfaces = interface_result.scalars().all()

        # Build tree structure
        folder_map: Dict[int, InterfaceTreeNode] = {}
        root_nodes: List[InterfaceTreeNode] = []

        # First pass: create folder nodes
        for folder in folders:
            node = InterfaceTreeNode(
                id=folder.id,
                name=folder.name,
                type="folder",
                folder_id=None,
                parent_id=folder.parent_id,
                sort_order=folder.sort_order,
                children=[],
            )
            folder_map[folder.id] = node

        # Second pass: create interface nodes
        for interface in interfaces:
            node = InterfaceTreeNode(
                id=interface.id,
                name=interface.name,
                type="interface",
                method=interface.method,
                path=interface.path,
                folder_id=interface.folder_id,
                parent_id=interface.folder_id,
                sort_order=interface.sort_order,
                children=[],
            )
            # Add interface to parent folder or root
            if interface.folder_id and interface.folder_id in folder_map:
                folder_map[interface.folder_id].children.append(node)
            else:
                root_nodes.append(node)

        # Third pass: build folder hierarchy
        for folder in folders:
            if folder.id in folder_map:
                node = folder_map[folder.id]
                if folder.parent_id and folder.parent_id in folder_map:
                    folder_map[folder.parent_id].children.append(node)
                else:
                    root_nodes.append(node)

        return root_nodes

    # ============== Folder CRUD ==============

    async def get_folder_by_id(self, folder_id: int) -> Optional[InterfaceFolder]:
        """Get folder by ID.

        Args:
            folder_id: Folder ID

        Returns:
            Folder instance or None if not found
        """
        result = await self.db.execute(
            select(InterfaceFolder).where(InterfaceFolder.id == folder_id)
        )
        return result.scalar_one_or_none()

    async def create_folder(self, folder_in: InterfaceFolderCreate) -> InterfaceFolder:
        """Create new folder.

        Args:
            folder_in: Folder creation data

        Returns:
            Created folder instance
        """
        folder = InterfaceFolder(
            project_id=folder_in.project_id,
            name=folder_in.name,
            parent_id=folder_in.parent_id,
        )
        self.db.add(folder)
        await self.db.flush()
        await self.db.refresh(folder)
        return folder

    async def update_folder(
        self, folder_id: int, folder_in: InterfaceFolderUpdate
    ) -> Optional[InterfaceFolder]:
        """Update folder.

        Args:
            folder_id: Folder ID
            folder_in: Folder update data

        Returns:
            Updated folder instance or None if not found
        """
        folder = await self.get_folder_by_id(folder_id)
        if not folder:
            return None

        update_data = folder_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(folder, field, value)

        await self.db.flush()
        await self.db.refresh(folder)
        return folder

    async def delete_folder(self, folder_id: int) -> bool:
        """Delete folder and all its children.

        Args:
            folder_id: Folder ID

        Returns:
            True if deleted, False if not found
        """
        folder = await self.get_folder_by_id(folder_id)
        if not folder:
            return False

        # Delete folder (cascade will handle children)
        await self.db.delete(folder)
        await self.db.flush()
        return True

    # ============== Interface CRUD ==============

    async def list_interfaces(
        self, project_id: int, skip: int = 0, limit: int = 100
    ) -> tuple[List[Interface], int]:
        """List interfaces for a project.

        Args:
            project_id: Project ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (interfaces list, total count)
        """
        query = select(Interface).where(Interface.project_id == project_id)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset(skip).limit(limit).order_by(Interface.sort_order, Interface.id)
        result = await self.db.execute(query)
        interfaces = result.scalars().all()

        return list(interfaces), total

    async def get_interface_by_id(self, interface_id: int) -> Optional[Interface]:
        """Get interface by ID.

        Args:
            interface_id: Interface ID

        Returns:
            Interface instance or None if not found
        """
        result = await self.db.execute(
            select(Interface).where(Interface.id == interface_id)
        )
        return result.scalar_one_or_none()

    async def create_interface(self, interface_in: InterfaceCreate) -> Interface:
        """Create new interface.

        Args:
            interface_in: Interface creation data

        Returns:
            Created interface instance
        """
        interface = Interface(
            project_id=interface_in.project_id,
            folder_id=interface_in.folder_id,
            name=interface_in.name,
            method=interface_in.method,
            path=interface_in.path,
            headers=interface_in.headers or {},
            params=interface_in.params or {},
            body=interface_in.body or {},
            body_type=interface_in.body_type,
        )
        self.db.add(interface)
        await self.db.flush()
        await self.db.refresh(interface)
        return interface

    async def update_interface(
        self, interface_id: int, interface_in: InterfaceUpdate
    ) -> Optional[Interface]:
        """Update interface.

        Args:
            interface_id: Interface ID
            interface_in: Interface update data

        Returns:
            Updated interface instance or None if not found
        """
        interface = await self.get_interface_by_id(interface_id)
        if not interface:
            return None

        update_data = interface_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(interface, field, value)

        await self.db.flush()
        await self.db.refresh(interface)
        return interface

    async def delete_interface(self, interface_id: int) -> bool:
        """Delete interface.

        Args:
            interface_id: Interface ID

        Returns:
            True if deleted, False if not found
        """
        interface = await self.get_interface_by_id(interface_id)
        if not interface:
            return False

        await self.db.delete(interface)
        await self.db.flush()
        return True

    # ============== Batch Operations ==============

    async def batch_reorder(self, reorder_in: InterfaceReorderRequest) -> Dict[str, Any]:
        """Batch reorder interfaces and folders.

        Args:
            reorder_in: Reorder request with list of {id, sort_order}

        Returns:
            Summary of reorder operation
        """
        updated_count = 0

        for update in reorder_in.updates:
            item_id = update.get("id")
            sort_order = update.get("sort_order", 0)

            if not item_id:
                continue

            # Try interface first
            interface = await self.get_interface_by_id(item_id)
            if interface:
                interface.sort_order = sort_order
                updated_count += 1
                continue

            # Try folder
            folder = await self.get_folder_by_id(item_id)
            if folder:
                folder.sort_order = sort_order
                updated_count += 1

        await self.db.flush()
        return {"updated_count": updated_count}

    # ============== cURL Import ==============

    async def import_from_curl(self, curl_in: CurlImportRequest) -> Interface:
        """Import interface from cURL command.

        Args:
            curl_in: cURL import request

        Returns:
            Created interface instance

        Raises:
            ValueError: If cURL command is invalid
        """
        parsed = self._parse_curl(curl_in.curl)

        interface = Interface(
            project_id=curl_in.project_id,
            folder_id=curl_in.folder_id,
            name=parsed.get("name", "Imported from cURL"),
            method=parsed.get("method", "GET"),
            path=parsed.get("path", "/"),
            headers=parsed.get("headers", {}),
            params=parsed.get("params", {}),
            body=parsed.get("body", {}),
            body_type=parsed.get("body_type", "json"),
        )
        self.db.add(interface)
        await self.db.flush()
        await self.db.refresh(interface)
        return interface

    def _parse_curl(self, curl_command: str) -> Dict[str, Any]:
        """Parse cURL command into interface components.

        Args:
            curl_command: cURL command string

        Returns:
            Parsed components (method, path, headers, body, etc.)

        Raises:
            ValueError: If cURL command is invalid
        """
        result: Dict[str, Any] = {
            "method": "GET",
            "path": "/",
            "headers": {},
            "params": {},
            "body": {},
            "body_type": "json",
        }

        # Remove 'curl' prefix and split
        parts = shlex.split(curl_command)
        if not parts or parts[0] != "curl":
            raise ValueError("Invalid cURL command: must start with 'curl'")

        i = 1
        while i < len(parts):
            part = parts[i]

            if part.startswith("-X") or part.startswith("--request"):
                # HTTP method
                if part == "-X" or part == "--request":
                    i += 1
                    if i < len(parts):
                        result["method"] = parts[i].upper()
                else:
                    result["method"] = part[2:].upper()

            elif part.startswith("-H") or part.startswith("--header"):
                # Header
                if part == "-H" or part == "--header":
                    i += 1
                    if i < len(parts):
                        header = parts[i]
                    else:
                        i += 1
                        continue
                else:
                    header = part[2:] if len(part) > 2 else parts[i + 1]
                    i += 1

                if ": " in header:
                    key, value = header.split(": ", 1)
                    result["headers"][key] = value
                elif ":" in header:
                    key, value = header.split(":", 1)
                    result["headers"][key] = value

            elif part.startswith("-d") or part.startswith("--data") or part.startswith("--data-raw"):
                # Request body
                if part in ["-d", "--data", "--data-raw", "--data-urlencode"]:
                    i += 1
                    if i < len(parts):
                        body_str = parts[i]
                    else:
                        i += 1
                        continue
                else:
                    body_str = parts[i + 1] if len(part) <= 3 else parts[i]
                    i += 1

                # Try to parse as JSON
                try:
                    import json

                    result["body"] = json.loads(body_str)
                    result["body_type"] = "json"
                except json.JSONDecodeError:
                    # Not JSON, treat as raw
                    result["body"] = {"raw": body_str}
                    result["body_type"] = "raw"

                # Set method to POST if not explicitly set
                if result["method"] == "GET":
                    result["method"] = "POST"

            elif part.startswith("--data-binary"):
                # Binary data
                i += 1
                if i < len(parts):
                    result["body"] = {"binary": parts[i]}
                    result["body_type"] = "raw"
                if result["method"] == "GET":
                    result["method"] = "POST"

            elif part.startswith("-G") or part.startswith("--get"):
                # Force GET
                result["method"] = "GET"

            elif not part.startswith("-") and "://" in part:
                # URL
                url = part
                # Extract path and query params
                from urllib.parse import parse_qs, urlparse

                parsed_url = urlparse(url)
                result["path"] = parsed_url.path or "/"

                # Parse query parameters
                if parsed_url.query:
                    params = parse_qs(parsed_url.query, keep_blank_values=True)
                    # Convert list values to single values
                    result["params"] = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

            i += 1

        # Generate default name from URL
        if "name" not in result:
            result["name"] = f"{result['method']} {result['path']}"

        return result
