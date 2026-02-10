# 职场摸鱼大作战 - 后端服务

> AI 驱动的职场模拟游戏后端 API

## 技术栈

- **FastAPI** - 异步 Web 框架
- **Pydantic** - 数据验证
- **SQLAlchemy** - ORM
- **OpenAI API** - AI 内容生成
- **SQLite/PostgreSQL** - 数据库

## 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key
```

### 4. 启动服务

```bash
# 方式1：直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方式2：后台启动（日志写入 server.log）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

访问 API 文档：http://localhost:8000/docs

### 5. 运行测试

```bash
# API 集成测试
python test_api.py

# 单元测试
pytest
```

## 项目结构

```
backend/
├── app/
│   ├── api/           # API 路由和数据模型
│   ├── core/          # 游戏引擎
│   ├── services/      # 业务服务（AI、会话管理）
│   ├── models/        # 数据库模型
│   ├── repositories/  # 数据访问层
│   ├── prompts/       # AI Prompt 模板
│   └── tests/         # 单元测试
├── requirements.txt
└── README.md
```

## API 端点

- `POST /api/game/start` - 开始新游戏
- `POST /api/game/choices` - 获取 AI 生成的选项
- `POST /api/game/choice/submit` - 提交玩家选择

## 开发规范

- 遵循 PEP 8 代码风格
- 使用类型注解
- 单元测试覆盖率 > 80%
- 使用 ruff 进行代码格式化

## 数据库配置

### PostgreSQL（推荐）

```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
```

**重要提示**：
- 必须使用 `postgresql+asyncpg://` 前缀（异步驱动）
- 如果使用 `postgresql://` 会导致 `InvalidRequestError`
- 确保安装了 `asyncpg` 包

### SQLite（开发环境）

```env
DATABASE_URL=sqlite+aiosqlite:///./game.db
```

## 常见问题

### 1. ModuleNotFoundError: No module named 'psycopg2'

**解决方案**：安装 PostgreSQL 驱动
```bash
pip install asyncpg psycopg2-binary
```

### 2. InvalidRequestError: The asyncio extension requires an async driver

**原因**：使用了同步驱动而非异步驱动

**解决方案**：修改 `.env` 文件中的数据库连接字符串
```env
# 错误 ❌
DATABASE_URL=postgresql://user:pass@host:port/db

# 正确 ✅
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
```

### 3. 服务启动失败

**检查清单**：
1. 确认所有依赖已安装：`pip install -r requirements.txt`
2. 确认 `.env` 文件存在且配置正确
3. 检查数据库连接：确保数据库服务正在运行
4. 查看日志：`tail -f server.log`
