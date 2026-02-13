# 接口定义模块 (INTF) 文档

## 概述

接口定义模块 (FR-005) 提供了完整的 API 接口管理功能,包括目录树管理、cURL 导入、环境配置和全局变量管理。

## 已实现功能

### INTF-001: 接口目录树 ✅
- 支持树形结构组织接口
- 拖拽排序 (使用 @dnd-kit)
- 多级文件夹支持
- 接口和文件夹的增删改

**前端页面**: `/frontend/src/pages/projects/InterfacesPage.tsx`
**后端API**: `/api/v1/interfaces/tree`

### INTF-002: cURL 导入 ✅
- 解析 cURL 命令
- 自动提取请求方法、URL、请求头、参数和请求体
- 支持 GET/POST 等所有 HTTP 方法
- 支持查询参数解析

**前端组件**: `/frontend/src/components/CurlImportDialog.tsx`
**后端API**: `/api/v1/interfaces/import/curl`

### INTF-003: 手动创建接口 ✅
- 表单式接口创建
- 选择 HTTP 方法
- 配置请求路径
- 添加接口描述

**前端组件**: `/frontend/src/components/InterfaceCreateDialog.tsx`
**后端API**: `/api/v1/interfaces` (POST)

### INTF-004: 多环境配置 ✅
- 创建多个环境 (开发/测试/生产)
- 配置环境的 Base URL
- 为每个环境配置独立的变量

**前端页面**: `/frontend/src/pages/EnvironmentsPage.tsx`
**后端API**:
- `/api/v1/environments` (GET/POST)
- `/api/v1/environments/{id}/variables` (GET/POST)

### INTF-005: 全局变量管理 ✅
- 项目级全局变量
- 变量类型标识 (manual/extracted)
- 变量描述

**前端页面**: `/frontend/src/pages/GlobalVariablesPage.tsx`
**后端API**:
- `/api/v1/environments/global/variables` (GET/POST)
- `/api/v1/environments/global/variables/{id}` (DELETE)

### INTF-006: MinIO 文件上传 ✅
- 文件上传到 MinIO 对象存储
- 生成预签名 URL (7 天有效期)
- 文件删除功能
- 上传进度跟踪

**后端服务**: `/backend/app/services/upload_service.py`
**后端路由**: `/api/v1/upload` (POST/DELETE)

## 技术栈

### 后端
- **FastAPI**: REST API 框架
- **SQLAlchemy 2.0**: ORM (使用 Mapped 模式)
- **MinIO Python SDK**: 对象存储客户端
- **Pydantic**: 请求/响应验证

### 前端
- **React 18**: UI 框架
- **@dnd-kit**: 拖拽排序
- **TypeScript**: 类型安全
- **TailwindCSS v4**: 样式

## 目录结构

```
backend/
├── app/
│   ├── models/
│   │   ├── interface.py           # 接口模型
│   │   └── interface_folder.py    # 文件夹模型
│   ├── routers/
│   │   ├── interfaces.py         # 接口路由
│   │   ├── environments.py       # 环境路由
│   │   └── upload.py           # 上传路由
│   ├── services/
│   │   ├── interface_service.py  # 接口业务逻辑
│   │   └── upload_service.py    # 上传服务
│   └── schemas/
│       └── interface.py         # Pydantic 模型

frontend/
├── src/
│   ├── pages/
│   │   ├── projects/
│   │   │   └── InterfacesPage.tsx     # 接口主页
│   │   ├── EnvironmentsPage.tsx         # 环境配置页
│   │   └── GlobalVariablesPage.tsx     # 全局变量页
│   ├── components/
│   │   ├── CurlImportDialog.tsx        # cURL 导入对话框
│   │   └── InterfaceCreateDialog.tsx    # 创建接口对话框
│   └── types/
│       ├── interface.ts                # 接口类型定义
│       └── environment.ts              # 环境类型定义
```

## cURL 解析示例

### POST 请求 (JSON)
```bash
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name":"test","email":"test@example.com"}'
```

解析结果:
- method: `POST`
- path: `/users`
- headers: `{ "Content-Type": "application/json" }`
- body: `{ "name": "test", "email": "test@example.com" }`

### GET 请求 (带查询参数)
```bash
curl 'https://api.example.com/users?page=1&limit=10' \
  -H 'Authorization: Bearer token123'
```

解析结果:
- method: `GET`
- path: `/users`
- params: `{ "page": "1", "limit": "10" }`
- headers: `{ "Authorization": "Bearer token123" }`

## API 端点

### 接口管理
| 方法 | 端点 | 描述 |
|------|--------|------|
| GET | `/api/v1/interfaces/tree` | 获取接口树 |
| POST | `/api/v1/interfaces/folders` | 创建文件夹 |
| PUT | `/api/v1/interfaces/folders/{id}` | 更新文件夹 |
| DELETE | `/api/v1/interfaces/folders/{id}` | 删除文件夹 |
| POST | `/api/v1/interfaces` | 创建接口 |
| GET | `/api/v1/interfaces/{id}` | 获取接口详情 |
| PUT | `/api/v1/interfaces/{id}` | 更新接口 |
| DELETE | `/api/v1/interfaces/{id}` | 删除接口 |
| POST | `/api/v1/interfaces/import/curl` | 导入 cURL |
| POST | `/api/v1/interfaces/batch/reorder` | 批量排序 |

### 环境管理
| 方法 | 端点 | 描述 |
|------|--------|------|
| GET | `/api/v1/environments` | 环境列表 |
| POST | `/api/v1/environments` | 创建环境 |
| PUT | `/api/v1/environments/{id}` | 更新环境 |
| DELETE | `/api/v1/environments/{id}` | 删除环境 |
| GET | `/api/v1/environments/{id}/variables` | 环境变量列表 |
| POST | `/api/v1/environments/{id}/variables` | 创建环境变量 |
| DELETE | `/api/v1/environments/variables/{id}` | 删除环境变量 |

### 全局变量
| 方法 | 端点 | 描述 |
|------|--------|------|
| GET | `/api/v1/environments/global/variables` | 全局变量列表 |
| POST | `/api/v1/environments/global/variables` | 创建全局变量 |
| DELETE | `/api/v1/environments/global/variables/{id}` | 删除全局变量 |

### 文件上传
| 方法 | 端点 | 描述 |
|------|--------|------|
| POST | `/api/v1/upload` | 上传文件 |
| DELETE | `/api/v1/upload/{object_name}` | 删除文件 |

## 测试

### 单元测试
```bash
cd backend
pytest tests/test_interface_service.py -v
```

### E2E 测试
```bash
cd frontend
npm run test:e2e interfaces
```

## 使用说明

### 1. 创建接口目录树
1. 进入项目详情页 → 接口定义
2. 点击"新建目录"按钮
3. 输入目录名称
4. 可选:拖拽目录调整层级

### 2. 导入 cURL
1. 在浏览器 DevTools 或 Postman 中复制 cURL 命令
2. 点击"导入 cURL"按钮
3. 粘贴 cURL 命令
4. 点击"解析 cURL"
5. 确认解析结果后点击"导入"

### 3. 手动创建接口
1. 点击"新建接口"按钮
2. 填写接口名称、请求方法和路径
3. 点击"创建"
4. 在右侧编辑器中配置详细信息

### 4. 配置环境
1. 进入环境配置页
2. 点击"新建环境"
3. 填写环境名称和 Base URL
4. 为环境添加变量

### 5. 使用全局变量
1. 进入全局变量页
2. 点击"添加变量"
3. 填写变量名和值
4. 在接口中通过 `{{变量名}}` 引用

## 注意事项

1. **MinIO 配置**: 确保后端 `.env` 中配置了正确的 MinIO 连接信息
2. **拖拽功能**: 需要安装 `@dnd-kit` 包
3. **cURL 解析**: 支持常见的 cURL 选项,复杂命令可能需要手动调整
4. **文件上传**: 预签名 URL 默认 7 天有效期,可在 `upload_service.py` 中调整

## 未来改进

- [ ] 接口版本控制
- [ ] 接口 Mock 功能
- [ ] 接口依赖关系图
- [ ] 批量导入/导出 (Postman 格式)
- [ ] 接口测试历史记录
- [ ] 接口性能监控
