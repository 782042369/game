"""
FastAPI 应用入口

配置 CORS、路由注册、中间件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api.endpoints import router
from app.core.constants import MAX_DAYS, MAX_TURNS_PER_DAY
from app.repositories.database import init_database, close_database

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 职场摸鱼大作战 API 服务启动中...")

    # 初始化数据库
    await init_database()

    yield

    # 关闭数据库连接
    await close_database()
    logger.info("👋 职场摸鱼大作战 API 服务已停止")


# 创建 FastAPI 应用
app = FastAPI(
    title="职场摸鱼大作战 API",
    description="AI 驱动的职场模拟游戏后端服务",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 开发服务器
        "http://localhost:3000",  # 备用端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/game", tags=["game"])


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "职场摸鱼大作战 API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "slack-master-2026-api",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
