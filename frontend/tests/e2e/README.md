# E2E 测试文档

## 目录结构

```
frontend/tests/e2e/
├── auth.spec.ts          # 认证模块 E2E 测试
├── pages/
│   ├── AuthPage.ts       # 登录/注册页面对象
│   └── DashboardPage.ts  # 首页面对象
└── helpers/
    └── api-helper.ts     # API 辅助函数
```

## 运行测试

### 前置条件

1. **启动后端服务** (http://localhost:8000)
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **启动前端服务** (可选,测试会自动启动)
   ```bash
   cd frontend
   npm run dev
   ```

### 运行命令

```bash
# 运行所有 E2E 测试
npm run test:e2e

# 使用 UI 模式运行
npm run test:e2e:ui

# 调试模式
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report
```

## 测试覆盖

### AUTH 模块测试

#### AUTH-001: 用户注册
- ✅ 成功注册新用户
- ✅ 拒绝重复注册相同邮箱
- ✅ 验证密码强度
- ✅ 验证邮箱格式

#### AUTH-002: 邮箱密码登录
- ✅ 成功登录并跳转到首页
- ✅ 拒绝错误密码登录
- ✅ 拒绝未注册邮箱登录
- ✅ 显示验证错误（空字段）

#### AUTH-005: 退出登录
- ✅ 成功退出并清除 token
- ✅ 退出后不能访问受保护页面

#### AUTH-007: 密码加密
- ✅ 验证密码不以明文存储
- ✅ 验证 API 响应不包含密码字段

#### AUTH-008: 账户锁定
- ✅ 5 次错误密码后锁定账户
- ✅ 正确登录重置失败计数

#### AUTH-003 & AUTH-004: OAuth 登录
- ✅ GitHub OAuth 按钮存在并可点击
- ✅ Google OAuth 按钮存在并可点击
- ⚠️  完整 OAuth 流程需要真实配置

## Page Object 模式

测试使用 Page Object 模式组织代码:

### AuthPage
- `goto()` - 导航到登录页
- `login(email, password)` - 执行登录
- `register(email, password)` - 执行注册
- `logout()` - 退出登录
- `getToken()` - 获取 localStorage 中的 token
- `waitForDashboard()` - 等待跳转到首页
- `waitForErrorMessage()` - 等待错误消息显示

### DashboardPage
- `isLoaded()` - 检查首页是否加载
- `getWelcomeText()` - 获取欢迎文本

## API 辅助函数

### ApiHelper
- `createTestUser(email, password)` - 创建测试用户
- `deleteTestUser(email, token)` - 删除测试用户
- `getUserToken(email, password)` - 获取用户 token

## 注意事项

1. **测试独立性**: 每个测试都有独立的 beforeEach/afterEach 钩子
2. **数据清理**: 测试结束后自动清理创建的测试用户
3. **并行执行**: 配置为串行执行 (`workers: 1`) 避免冲突
4. **视频录制**: 失败时自动录制视频和截图
5. **OAuth 测试**: 完整 OAuth 流程需要真实配置,当前只测试按钮存在

## 故障排查

### 测试失败
1. 检查后端服务是否运行 (http://localhost:8000)
2. 检查数据库连接是否正常
3. 查看截图和视频: `playwright-report/`
4. 使用 UI 模式调试: `npm run test:e2e:ui`

### 端口冲突
如果 3000 端口被占用,修改 `playwright.config.ts`:
```typescript
webServer: {
  command: 'npm run dev -- --port 3001',
  url: 'http://localhost:3001',
}
```

### 数据库清理
如果测试用户累积,运行清理脚本:
```bash
# 连接数据库删除所有测试用户
psql -U postgres -d sisyphus -c "DELETE FROM users WHERE email LIKE '%@example.com';"
```

## 扩展测试

添加新测试时:
1. 在 `pages/` 创建对应的 Page Object
2. 在 `*.spec.ts` 添加测试用例
3. 使用 `test.describe()` 分组
4. 添加 beforeEach/afterEach 钩子
5. 运行测试验证

## 测试覆盖率目标

- ✅ 成功路径 (Happy Path)
- ✅ 失败路径 (Error Cases)
- ✅ 边界情况 (Edge Cases)
- ✅ UI 状态验证
- ✅ localStorage 验证
- ✅ 数据库状态验证 (通过 API)
