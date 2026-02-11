"""
数据库连接和会话管理

提供数据库连接、初始化和会话管理功能
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.models.database import Base


# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # 设置为 True 可以查看 SQL 日志
    future=True,
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session():
    """
    获取数据库会话（FastAPI依赖注入）

    FastAPI会自动调用这个generator函数并管理session的生命周期
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """
    初始化数据库

    创建所有表（如果不存在）
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ 数据库初始化完成")


async def close_database():
    """
    关闭数据库连接

    在应用关闭时调用
    """
    await engine.dispose()
    print("👋 数据库连接已关闭")
