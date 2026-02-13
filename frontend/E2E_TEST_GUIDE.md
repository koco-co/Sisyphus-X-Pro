# Sisyphus-X-Pro E2E 测试执行指南

## 测试覆盖模块

### 已实现的测试文件:

1. **auth.spec.ts** - 用户认证模块 (AUTH-001 至 AUTH-008)
2. **dashboard.spec.ts** - 首页仪表盘 (DASH-001 至 DASH-003)
3. **projects.spec.ts** - 项目管理 (PROJ-001 至 PROJ-006)
4. **interfaces.spec.ts** - 接口定义 (INTF-001 至 INTF-006)
5. **keywords.spec.ts** - 关键字配置 (KEYW-001 至 KEYW-005) ✨ 新增
6. **scenarios.spec.ts** - 场景编排 (SCEN-001 至 SCEN-007) ✨ 新增
7. **test-plans.spec.ts** - 测试计划 (PLAN-001 至 PLAN-009) ✨ 新增
8. **reports.spec.ts** - 测试报告 (REPT-001 至 REPT-010) ✨ 新增
9. **global-params.spec.ts** - 全局参数 (GPAR-001 至 GPAR-010) ✨ 新增

## 前置条件

### 1. 启动后端服务

```bash
cd backend

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 启动 FastAPI 服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证后端运行:
```bash
curl http://localhost:8000/api/health
```

### 2. 启动前端服务

```bash
cd frontend

# 启动开发服务器
npm run dev
```

验证前端运行:
```bash
curl http://localhost:3000
```

### 3. 确保 Docker 服务运行

```bash
# 项目根目录
docker-compose up -d

# 检查服务状态
docker-compose ps
```

## 运行测试

### 运行所有 E2E 测试

```bash
cd frontend

# 运行所有测试
npx playwright test

# 运行测试并生成报告
npx playwright test --reporter=html

# 在浏览器中查看报告
npx playwright show-report
```

### 运行特定模块测试

```bash
# AUTH 模块
npx playwright test auth.spec.ts

# Dashboard 模块
npx playwright test dashboard.spec.ts

# Projects 模块
npx playwright test projects.spec.ts

# Interfaces 模块
npx playwright test interfaces.spec.ts

# Keywords 模块
npx playwright test keywords.spec.ts

# Scenarios 模块
npx playwright test scenarios.spec.ts

# Test Plans 模块
npx playwright test test-plans.spec.ts

# Reports 模块
npx playwright test reports.spec.ts

# Global Params 模块
npx playwright test global-params.spec.ts
```

### 运行特定测试用例

```bash
# 运行包含特定描述的测试
npx playwright test --grep "应该成功登录"

# 运行特定文件中的第 N 个测试
npx playwright test auth.spec.ts:15
```

### 调试模式

```bash
# 显示浏览器窗口 (调试模式)
npx playwright test --debug

# 慢动作模式
npx playwright test --headed --slow-mo=1000

# 运行特定测试并显示浏览器
npx playwright test auth.spec.ts --headed
```

## 测试报告

### HTML 报告

```bash
# 运行测试生成 HTML 报告
npx playwright test --reporter=html

# 查看报告
npx playwright show-report
```

报告位置: `frontend/playwright-report/index.html`

### 截图和录屏

- **截图**: `frontend/test-results/`
- **录屏**: `frontend/test-results/` (仅在失败时)
- **Trace 文件**: `frontend/test-results/` (用于调试)

### 查看失败测试的 Trace

```bash
npx playwright show-trace test-results/[test-name]/trace.zip
```

## 测试数据清理

测试使用动态生成的数据,并自动清理:

- 每次测试前创建新的测试用户
- 测试后自动删除测试用户
- 使用时间戳确保数据唯一性

手动清理脚本:

```bash
# 清理所有测试用户 (需要管理员权限)
curl -X DELETE http://localhost:8000/api/users/test-cleanup \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 持续集成配置

### GitHub Actions 示例

```yaml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright Browsers
        run: |
          cd frontend
          npx playwright install --with-deps

      - name: Start Backend
        run: |
          cd backend
          python -m pip install -r requirements.txt
          uvicorn app.main:app &
          sleep 10

      - name: Run E2E Tests
        run: |
          cd frontend
          npx playwright test

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## 故障排除

### 常见问题

1. **后端未响应**
   ```bash
   # 检查后端服务
   curl http://localhost:8000/api/health

   # 查看后端日志
   cd backend && tail -f logs/app.log
   ```

2. **前端未响应**
   ```bash
   # 检查前端服务
   curl http://localhost:3000

   # 重启前端
   cd frontend && npm run dev
   ```

3. **数据库连接失败**
   ```bash
   # 检查 Docker 服务
   docker-compose ps

   # 重启数据库
   docker-compose restart postgres
   ```

4. **测试超时**
   - 增加 `playwright.config.ts` 中的超时时间
   - 检查网络连接
   - 使用 `--timeout` 参数

5. **Playwright 浏览器未安装**
   ```bash
   npx playwright install
   npx playwright install-deps
   ```

## 测试最佳实践

1. **独立性**: 每个测试独立运行,不依赖其他测试
2. **清理数据**: 测试后清理所有创建的数据
3. **等待策略**: 使用显式等待而非硬性延迟
4. **选择器优先级**:
   - `data-testid` > `aria-label` > `text` > CSS 选择器
5. **错误处理**: 使用 try-catch 捕获异常并记录

## 贡献指南

添加新测试时:

1. 创建新的测试文件或扩展现有文件
2. 使用 Page Object 模式组织代码
3. 添加详细的测试描述
4. 确保测试数据唯一性
5. 添加必要的清理逻辑
6. 更新本文档

## 联系方式

测试问题请联系:
- 项目仓库: https://github.com/your-org/Sisyphus-X-Pro
- Issue 追踪: https://github.com/your-org/Sisyphus-X-Pro/issues
