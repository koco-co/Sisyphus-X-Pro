"""测试配置和 fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# 使用测试数据库
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """创建测试数据库引擎."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话."""
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session


# Alias for backward compatibility
db_session = db
async_session = db


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# Fixtures for dashboard tests
from app.models.user import User
from app.models.project import Project
from app.models.interface import Interface
from app.models.scenario import Scenario
from app.models.test_plan import TestPlan
from app.models.test_execution import TestExecution
from app.models.environment import Environment
from datetime import datetime


@pytest_asyncio.fixture(scope="function")
async def test_user(async_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        nickname="Test User",
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_project(async_session: AsyncSession, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="A test project",
        creator_id=test_user.id,
    )
    async_session.add(project)
    await async_session.commit()
    await async_session.refresh(project)
    return project


@pytest_asyncio.fixture(scope="function")
async def test_environment(async_session: AsyncSession, test_project: Project) -> Environment:
    """Create a test environment."""
    env = Environment(
        name="Test Environment",
        base_url="https://api.example.com",
        project_id=test_project.id,
        creator_id=test_project.creator_id,
    )
    async_session.add(env)
    await async_session.commit()
    await async_session.refresh(env)
    return env


@pytest_asyncio.fixture(scope="function")
async def test_interface(async_session: AsyncSession, test_project: Project) -> Interface:
    """Create a test interface."""
    interface = Interface(
        name="Test API",
        method="GET",
        path="/api/test",
        project_id=test_project.id,
    )
    async_session.add(interface)
    await async_session.commit()
    await async_session.refresh(interface)
    return interface


@pytest_asyncio.fixture(scope="function")
async def test_scenario(async_session: AsyncSession, test_project: Project) -> Scenario:
    """Create a test scenario."""
    scenario = Scenario(
        name="Test Scenario",
        project_id=test_project.id,
        creator_id=test_project.creator_id,
    )
    async_session.add(scenario)
    await async_session.commit()
    await async_session.refresh(scenario)
    return scenario


@pytest_asyncio.fixture(scope="function")
async def test_plan(async_session: AsyncSession, test_project: Project) -> TestPlan:
    """Create a test plan."""
    plan = TestPlan(
        name="Test Plan",
        project_id=test_project.id,
        creator_id=test_project.creator_id,
    )
    async_session.add(plan)
    await async_session.commit()
    await async_session.refresh(plan)
    return plan


@pytest_asyncio.fixture(scope="function")
async def test_execution(
    async_session: AsyncSession,
    test_plan: TestPlan,
    test_environment: Environment,
    test_user: User,
) -> TestExecution:
    """Create a test execution."""
    execution = TestExecution(
        plan_id=test_plan.id,
        environment_id=test_environment.id,
        executor_id=test_user.id,
        status="completed",
        total_scenarios=1,
        passed_scenarios=1,
        failed_scenarios=0,
        started_at=datetime.now(),
        finished_at=datetime.now(),
    )
    async_session.add(execution)
    await async_session.commit()
    await async_session.refresh(execution)
    return execution
