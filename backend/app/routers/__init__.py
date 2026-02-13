"""API routers."""

from app.routers import (
    auth,
    dashboard,
    db_configs,
    environments,
    global_params,
    interfaces,
    keywords,
    projects,
    reports,
    scenarios,
    test_plans,
    upload,
)

__all__ = [
    "auth",
    "projects",
    "db_configs",
    "keywords",
    "environments",
    "interfaces",
    "dashboard",
    "global_params",
    "reports",
    "scenarios",
    "test_plans",
    "upload",
]
