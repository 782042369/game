#!/usr/bin/env python3
"""
数据库迁移脚本

从旧数据模型迁移到新数据模型（database_v2.py）

步骤：
1. 创建新表
2. 数据迁移（如果需要保留旧数据）
3. 删除旧表（可选）
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import logger
from app.models.database import Base as OldBase
from app.models.database_v2 import Base as NewBase, create_tables, drop_tables


async def migrate_database(drop_old: bool = False):
    """
    执行数据库迁移

    Args:
        drop_old: 是否删除旧表（默认False，安全模式）
    """
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        logger.info("🔄 开始数据库迁移...")

        # 1. 创建新表
        logger.info("📝 创建新表...")
        async with engine.begin() as conn:
            await conn.run_sync(NewBase.metadata.create_all)
        logger.success("✅ 新表创建完成")

        # 2. 数据迁移（如果需要保留旧数据）
        # 注意：旧数据模型和新数据模型结构差异很大，这里只是示例
        logger.info("📦 迁移数据...")
        # async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        # async with async_session() as session:
        #     # 迁移sessions表
        #     await migrate_sessions(session)
        #     await session.commit()
        logger.info("⚠️  数据迁移需要手动实现（新旧模型差异较大）")

        # 3. 删除旧表（可选）
        if drop_old:
            logger.warning("⚠️  即将删除旧表...")
            confirm = input("确认删除旧表？(yes/no): ")
            if confirm.lower() == "yes":
                logger.info("🗑️  删除旧表...")
                async with engine.begin() as conn:
                    await conn.run_sync(OldBase.metadata.drop_all)
                logger.success("✅ 旧表已删除")
            else:
                logger.info("❌ 取消删除旧表")

        logger.success("🎉 数据库迁移完成！")

    except Exception as e:
        logger.error(f"❌ 迁移失败: {e}")
        raise
    finally:
        await engine.dispose()


async def rollback_migration():
    """
    回滚迁移（删除新表）
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=True)

    try:
        logger.warning("⚠️  回滚迁移：删除新表...")

        async with engine.begin() as conn:
            await conn.run_sync(NewBase.metadata.drop_all)

        logger.success("✅ 回滚完成")

    except Exception as e:
        logger.error(f"❌ 回滚失败: {e}")
        raise
    finally:
        await engine.dispose()


async def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "rollback":
            await rollback_migration()
            return

    # 默认执行迁移（安全模式，不删除旧表）
    drop_old = "--drop-old" in sys.argv
    await migrate_database(drop_old=drop_old)


if __name__ == "__main__":
    asyncio.run(main())
