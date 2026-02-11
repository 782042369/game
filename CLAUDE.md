# 摸鱼大作战 (Slack Master 2026) - AI 开发导航

> 像素风程序员职场生存模拟游戏 | Vue 3 + FastAPI + AI 驱动

最后更新: 2026-02-11

---

## 项目快照

这是一款**2D文字冒险/RPG游戏**，玩家扮演程序员在职场中通过"工作"与"摸鱼"的平衡策略生存30天。

**技术栈**:
- **前端**: Vue 3.5 + TypeScript 5.7 + Vite 8 + Pinia + UnoCSS
- **后端**: FastAPI + SQLAlchemy + OpenAI API + SQLite/PostgreSQL
- **AI驱动**: 动态生成游戏选项与剧情上下文

**核心机制**:
- 回合制行动系统（每天8小时/回合）
- 四维属性管理：精力(Energy)、摸鱼值(Chill)、进度(Progress)、怀疑度(Suspicion)
- AI动态生成选项：根据玩家状态和历史生成个性化游戏选项
- 事件系统（老板巡逻、需求变更等）

---

## 模块导航

### 架构总览

```mermaid
graph TD
    A["摸鱼大作战 (根)"] --> B["web/ 前端"];
    A --> C["backend/ 后端"];

    B --> D["src/components/ UI组件"];
    B --> E["src/stores/ Pinia状态"];
    B --> F["src/game/ 游戏核心"];
    B --> G["src/api/ API客户端"];

    C --> H["app/api/ API端点"];
    C --> I["app/core/ 游戏引擎"];
    C --> J["app/services/ AI服务"];
    C --> K["app/models/ 数据模型"];
    C --> L["app/repositories/ 数据访问"];

    click D "#web-srccomponents" "查看 UI组件模块"
    click E "#web-srcstores" "查看状态管理模块"
    click F "#web-srcgame" "查看游戏核心模块"
    click G "#web-srcapi" "查看 API客户端模块"
    click H "#backend-appapi" "查看后端API模块"
    click I "#backend-appcore" "查看后端游戏引擎"
    click J "#backend-appservices" "查看AI服务模块"
```

### 模块索引

| 模块路径 | 职责 | 关键文件/命令 | 现有文档 |
|---------|------|--------------|---------|
| **web/src/components/** | UI组件层 | HUD.vue, ActionPanel.vue, EventArea.vue | @web/src/components/CLAUDE.md |
| **web/src/stores/** | Pinia状态管理 | game.ts, player.ts, ui.ts | @web/src/stores/CLAUDE.md |
| **web/src/game/** | 游戏核心逻辑 | types/, core/engine.ts, data/ | @web/src/game/CLAUDE.md |
| **web/src/api/** | 后端API客户端 | game.ts (axios封装) | - |
| **backend/app/api/** | FastAPI路由 | endpoints.py, schemas.py | @backend/README.md |
| **backend/app/core/** | 后端游戏引擎 | game_engine.py, constants.py | @backend/README.md |
| **backend/app/services/** | 业务服务层 | ai_service.py, session_service.py | @backend/README.md |
| **backend/app/models/** | 数据库模型 | database.py | @backend/README.md |
| **backend/app/repositories/** | 数据访问层 | database.py | @backend/README.md |

---

## 快速启动

### 前端 (Vue 3)
```bash
cd web
pnpm install
pnpm dev          # 开发服务器 http://localhost:5173
pnpm build        # 构建生产版本
pnpm type-check   # TypeScript类型检查
pnpm lint         # ESLint代码检查
```

### 后端 (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # 配置环境变量
uvicorn app.main:app --reload --port 8000
```

### 数据库配置
- **开发环境**: SQLite (`sqlite+aiosqlite:///./game.db`)
- **生产环境**: PostgreSQL (`postgresql+asyncpg://user:pass@host:port/db`)

---

## 关键技术决策

### 1. 前后端分离架构
- **前端**: Vue 3 + Pinia 响应式状态管理，专注UI渲染
- **后端**: FastAPI 异步框架，处理游戏逻辑与AI集成
- **通信**: RESTful API，axios封装错误处理

### 2. AI驱动游戏设计
- **动态选项生成**: 根据玩家状态和历史上下文生成个性化选项
- **降级方案**: API失败时自动使用预设选项
- **可配置**: 支持自定义 OpenAI Base URL 和模型

### 3. 数据持久化
- **会话管理**: SQLAlchemy 异步ORM
- **历史记录**: 存储玩家行动历史供AI上下文使用
- **数据库**: 开发用SQLite，生产用PostgreSQL

---

## 参考文档

### 前端模块
- **UI组件**: @web/src/components/CLAUDE.md
- **状态管理**: @web/src/stores/CLAUDE.md
- **游戏核心**: @web/src/game/CLAUDE.md
- **前端配置**: @web/package.json, @web/vite.config.ts

### 后端模块
- **后端文档**: @backend/README.md
- **依赖配置**: @backend/requirements.txt
- **环境配置**: @backend/.env.example

---

## 开发规范摘要

### 代码风格
- **前端**: kebab-case文件名, PascalCase组件名, camelCase变量
- **后端**: PEP 8, 类型注解, async/await异步模式

### Git工作流
```bash
feat: 新功能
fix: Bug修复
refactor: 重构
docs: 文档更新
test: 测试相关
```

---

## 当前开发阶段

**Phase 3 已完成**:
- 前后端分离架构
- FastAPI后端服务
- AI选项生成系统
- 数据库持久化
- API客户端封装

**规划中**:
- 技能系统实现
- 丰富随机事件
- 存档系统
- 多结局系统

---

## 测试策略

- **前端**: Vitest单元测试, Vue组件测试
- **后端**: pytest + pytest-asyncio, 覆盖率>80%
- **E2E**: 核心游戏流程测试

---

## 变更记录 (Changelog)

### 2026-02-11
- 添加后端模块 (FastAPI + AI集成)
- 更新架构图，包含前后端分离结构
- 添加API客户端模块文档
- 更新快速启动指南（含后端启动）

### 2026-02-10
- 初始化AI上下文文档
- 生成前端模块导航

---

**文档维护**: 本文档随项目进展持续更新。
