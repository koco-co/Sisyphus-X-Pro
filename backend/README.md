# Sisyphus-X-Pro Backend

基于 FastAPI 的现代化 API 测试平台后端服务。

## 技术栈

- **FastAPI** 0.128+ - 现代化的 Web 框架
- **SQLAlchemy** 2.0+ - ORM（异步模式）
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和会话存储
- **MinIO** - 对象存储
- **Pydantic** 2.x - 数据验证
- **Alembic** - 数据库迁移
- **uv** - 快速的 Python 包管理器

## 快速开始

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库等连接信息
```

### 3. 启动开发服务器

```bash
# 使用脚本
./scripts/dev.sh

# 或直接运行
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务器将在 http://localhost:8000 启动

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 开发指南

### 运行测试

```bash
# 使用脚本
./scripts/test.sh

# 或直接运行
uv run pytest
```

### 代码质量检查

```bash
# 代码检查
uv run ruff check app/

# 自动修复
uv run ruff check --fix app/

# 代码格式化
uv run ruff format app/
```

### 类型检查

```bash
uv run pyright app/
```

## 许可证

MIT
