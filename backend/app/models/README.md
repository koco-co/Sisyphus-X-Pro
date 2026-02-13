# Database Models

本目录包含 Sisyphus-X-Pro 应用的所有数据库模型。

## 模型列表

### 核心模型 (4个)
- **User**: 用户表 - 支持邮箱和 OAuth 认证
- **Project**: 项目表 - 组织测试资源
- **DatabaseConfig**: 数据库配置表 - 测试数据库连接
- **Keyword**: 关键字表 - 可复用的测试操作

### 接口管理 (3个)
- **InterfaceFolder**: 接口目录表 - 树形结构组织接口
- **Interface**: 接口定义表 - HTTP 请求详情
- **Environment**: 环境表 - 多环境配置

### 变量管理 (3个)
- **EnvVariable**: 环境变量表 - 环境特定变量
- **GlobalVariable**: 全局变量表 - 项目级别变量
- **GlobalParam**: 全局参数表 - 内置工具函数

### 测试场景 (3个)
- **Scenario**: 场景表 - 测试场景定义
- **ScenarioStep**: 场景步骤表 - 场景中的步骤
- **Dataset**: 数据集表 - 数据驱动测试

### 测试计划 (2个)
- **TestPlan**: 测试计划表 - 组织场景执行
- **PlanScenario**: 计划场景关联表 - 场景编排

### 测试执行 (4个)
- **TestExecution**: 测试执行记录表 - 执行状态跟踪
- **ExecutionScenario**: 执行场景记录表 - 场景执行详情
- **ExecutionStep**: 执行步骤记录表 - 步骤执行详情
- **TestReport**: 测试报告表 - 聚合结果和 Allure 报告

## 使用方法

### 1. 初始化数据库表

```python
from app.database import init_db

async def create_tables():
    await init_db()
```

### 2. 导入模型

```python
from app.models import User, Project, Scenario
from app.database import async_session

async with async_session() as session:
    user = User(email="test@example.com", nickname="Test User")
    session.add(user)
    await session.commit()
```

### 3. 运行种子数据脚本

```bash
cd backend
python scripts/init_seed_data.py
```

## 数据库表关系

```
users → projects → interface_folders → interfaces
              ↓
         environments → env_variables
              ↓
         scenarios → scenario_steps
              ↓
         datasets
              ↓
         test_plans → plan_scenarios
              ↓
         test_executions → execution_scenarios → execution_steps
              ↓
         test_reports
```

## 技术栈

- **SQLAlchemy 2.0**: 异步 ORM
- **PostgreSQL**: 数据库
- **Pydantic**: 数据验证

## 注意事项

1. 所有模型继承自 `Base` 和 `TimestampMixin`（除了 TestExecution, TestReport）
2. 外键关系使用 `ON DELETE CASCADE`
3. JSON 字段使用 PostgreSQL JSONB 类型
4. TestExecution 使用 UUID 作为主键
5. Allure 报告自动 30 天后过期

## 下一步

- [ ] 实现 Repository 模式数据访问层
- [ ] 添加 Pydantic schemas 用于 API 序列化
- [ ] 配置 Alembic 数据库迁移
