"""
会话数据访问层

负责sessions表的CRUD操作
"""
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Session as SessionModel


class SessionRepository:
    """会话数据访问类"""

    def __init__(self, db_session: AsyncSession):
        """
        初始化仓库

        Args:
            db_session: 数据库会话
        """
        self.db = db_session

    async def create(self, seed: int, metadata: Optional[dict] = None) -> str:
        """
        创建新会话

        Args:
            seed: 随机种子
            metadata: 元数据（可选）

        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())

        session = SessionModel(
            id=session_id,
            seed=seed,
            metadata=metadata or {},
            status="active"
        )

        self.db.add(session)
        await self.db.commit()

        return session_id

    async def get(self, session_id: str) -> Optional[SessionModel]:
        """
        获取会话

        Args:
            session_id: 会话ID

        Returns:
            会话对象或None
        """
        query = select(SessionModel).where(SessionModel.id == session_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_status(self, session_id: str, status: str) -> bool:
        """
        更新会话状态

        Args:
            session_id: 会话ID
            status: 新状态（active, completed, abandoned）

        Returns:
            是否成功
        """
        session = await self.get(session_id)
        if not session:
            return False

        session.status = status
        await self.db.commit()
        return True

    async def delete(self, session_id: str) -> bool:
        """
        删除会话

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        session = await self.get(session_id)
        if not session:
            return False

        await self.db.delete(session)
        await self.db.commit()
        return True
