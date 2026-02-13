"""Global parameter service for business logic."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.global_param import GlobalParam
from app.schemas.global_param import GlobalParamCreate, GlobalParamUpdate
from app.utils.function_executor import (
    BUILTIN_FUNCTIONS,
    BUILTIN_PARAMS_DATA,
    FunctionExecutor,
)


class GlobalParamService:
    """Service for global parameter-related business logic."""

    def __init__(self, db: AsyncSession):
        """Initialize global parameter service.

        Args:
            db: Database session
        """
        self.db = db

    async def list_global_params(
        self,
        skip: int = 0,
        limit: int = 100,
        class_name: str | None = None,
        is_builtin: bool | None = None,
    ) -> tuple[list[GlobalParam], int]:
        """List global parameters with pagination and filtering.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            class_name: Filter by class name
            is_builtin: Filter by is_builtin flag

        Returns:
            Tuple of (global_params list, total count)
        """
        # Build base query
        query = select(GlobalParam)

        # Apply filters
        if class_name:
            query = query.where(GlobalParam.class_name == class_name)
        if is_builtin is not None:
            query = query.where(GlobalParam.is_builtin == is_builtin)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.offset(skip).limit(limit)
        query = query.order_by(GlobalParam.class_name, GlobalParam.method_name)

        result = await self.db.execute(query)
        params = result.scalars().all()

        return list(params), total

    async def get_global_param_by_id(self, param_id: int) -> GlobalParam | None:
        """Get global parameter by ID.

        Args:
            param_id: Global parameter ID

        Returns:
            GlobalParam instance or None if not found
        """
        result = await self.db.execute(
            select(GlobalParam).where(GlobalParam.id == param_id)
        )
        return result.scalar_one_or_none()

    async def create_global_param(
        self, param_in: GlobalParamCreate
    ) -> GlobalParam:
        """Create new global parameter.

        Args:
            param_in: Global parameter creation data

        Returns:
            Created global parameter instance

        Raises:
            ValueError: If class_name + method_name already exists
        """
        # Check if class_name + method_name already exists
        existing = await self.db.execute(
            select(GlobalParam).where(
                GlobalParam.class_name == param_in.class_name,
                GlobalParam.method_name == param_in.method_name,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                f"Function {param_in.class_name}.{param_in.method_name} already exists"
            )

        # Create global parameter
        param = GlobalParam(
            class_name=param_in.class_name,
            method_name=param_in.method_name,
            description=param_in.description,
            code=param_in.code,
            params_in=param_in.params_in,  # type: ignore[arg-type]
            params_out=param_in.params_out,  # type: ignore[arg-type]
            is_builtin=False,  # User-created params are never builtin
        )
        self.db.add(param)
        await self.db.flush()
        await self.db.refresh(param)
        return param

    async def update_global_param(
        self, param_id: int, param_in: GlobalParamUpdate
    ) -> GlobalParam | None:
        """Update global parameter.

        Args:
            param_id: Global parameter ID
            param_in: Global parameter update data

        Returns:
            Updated global parameter instance or None if not found

        Raises:
            ValueError: If param is builtin or class_name+method_name conflict
        """
        param = await self.get_global_param_by_id(param_id)
        if not param:
            return None

        # Check if builtin
        if param.is_builtin:
            raise ValueError("Built-in global parameters cannot be modified")

        # Check class_name+method_name uniqueness if changed
        if param_in.class_name and param_in.method_name:
            if (
                param_in.class_name != param.class_name
                or param_in.method_name != param.method_name
            ):
                existing = await self.db.execute(
                    select(GlobalParam).where(
                        GlobalParam.class_name == param_in.class_name,
                        GlobalParam.method_name == param_in.method_name,
                        GlobalParam.id != param_id,
                    )
                )
                if existing.scalar_one_or_none():
                    raise ValueError(
                        f"Function {param_in.class_name}.{param_in.method_name} already exists"
                    )

        # Update fields
        update_data = param_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["params_in", "params_out"] and value is not None:
                setattr(param, field, value)  # type: ignore[arg-type]
            elif value is not None:
                setattr(param, field, value)

        await self.db.flush()
        await self.db.refresh(param)
        return param

    async def delete_global_param(self, param_id: int) -> bool:
        """Delete global parameter.

        Args:
            param_id: Global parameter ID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If param is builtin
        """
        param = await self.get_global_param_by_id(param_id)
        if not param:
            return False

        # Check if builtin
        if param.is_builtin:
            raise ValueError("Built-in global parameters cannot be deleted")

        await self.db.delete(param)
        await self.db.flush()
        return True

    async def get_global_params_grouped(self) -> dict[str, list[GlobalParam]]:
        """Get all global parameters grouped by class name.

        Returns:
            Dictionary mapping class_name to list of global params
        """
        result = await self.db.execute(
            select(GlobalParam).order_by(GlobalParam.class_name, GlobalParam.method_name)
        )
        params = result.scalars().all()

        # Group by class_name
        grouped: dict[str, list[GlobalParam]] = {}
        for param in params:
            if param.class_name not in grouped:
                grouped[param.class_name] = []
            grouped[param.class_name].append(param)

        return grouped

    async def get_function_executor(self) -> FunctionExecutor:
        """Get function executor with all available functions.

        Returns:
            FunctionExecutor instance with all registered functions
        """
        # Get all global params
        result = await self.db.execute(select(GlobalParam))
        params = result.scalars().all()

        # Build function registry
        functions = {**BUILTIN_FUNCTIONS}  # Start with builtins

        # Add user-defined functions
        for param in params:
            func_name = param.method_name
            try:
                # Execute the code to get the function
                exec_globals = {}
                exec(param.code, exec_globals)
                if func_name in exec_globals and callable(exec_globals[func_name]):
                    functions[func_name] = exec_globals[func_name]
            except Exception:
                # Skip invalid functions
                pass

        return FunctionExecutor(functions)

    async def parse_function_calls(
        self, text: str, context: dict[str, str]
    ) -> tuple[str, list[str], bool, str | None]:
        """Parse {{function()}} calls in text and replace with actual values.

        Args:
            text: Text containing {{function()}} placeholders
            context: Execution context variables

        Returns:
            Tuple of (parsed_text, functions_called, success, error_message)
        """
        executor = await self.get_function_executor()
        return executor.parse_text(text, context)

    async def initialize_builtin_params(self) -> int:
        """Initialize built-in global parameters.

        Creates built-in parameters if they don't exist.

        Returns:
            Number of parameters created
        """
        created_count = 0

        for param_data in BUILTIN_PARAMS_DATA:
            # Check if already exists
            existing = await self.db.execute(
                select(GlobalParam).where(
                    GlobalParam.class_name == param_data["class_name"],
                    GlobalParam.method_name == param_data["method_name"],
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Create built-in param
            param = GlobalParam(
                class_name=param_data["class_name"],
                method_name=param_data["method_name"],
                description=param_data["description"],
                code=param_data["code"],
                params_in=param_data["params_in"],  # type: ignore[arg-type]
                params_out=param_data["params_out"],  # type: ignore[arg-type]
                is_builtin=param_data["is_builtin"],
            )
            self.db.add(param)
            created_count += 1

        if created_count > 0:
            await self.db.flush()

        return created_count
