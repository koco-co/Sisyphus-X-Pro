"""Database models package.

This package contains all SQLAlchemy models for Sisyphus-X-Pro application.
All models inherit from Base class defined in database.py.

IMPORTANT: Import order matters - User must be imported before other models
that have foreign key relationships to it.
"""

# User model FIRST - before models that reference it
# Database config and environment
from .database_config import DatabaseConfig
from .dataset import Dataset
from .env_variable import EnvVariable
from .environment import Environment
from .execution_scenario import ExecutionScenario
from .execution_step import ExecutionStep
from .global_param import GlobalParam
from .global_variable import GlobalVariable

# Interface and folder
from .interface import Interface
from .interface_folder import InterfaceFolder

# Keyword and global parameters
from .keyword import Keyword
from .plan_scenario import PlanScenario

# Project and related models
from .project import Project

# Scenario and test execution
from .scenario import Scenario
from .scenario_step import ScenarioStep
from .test_execution import TestExecution
from .test_plan import TestPlan
from .test_report import TestReport
from .user import User

__all__ = [
    "User",
    "Project",
    "DatabaseConfig",
    "Keyword",
    "InterfaceFolder",
    "Interface",
    "Environment",
    "EnvVariable",
    "GlobalVariable",
    "Scenario",
    "ScenarioStep",
    "Dataset",
    "TestPlan",
    "PlanScenario",
    "TestExecution",
    "ExecutionScenario",
    "ExecutionStep",
    "TestReport",
    "GlobalParam",
]
