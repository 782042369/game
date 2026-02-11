"""
消息数据访问层

负责messages表的CRUD操作
"""
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Message


class MessageRepository:
    """消息数据访问类"""

    def __init__(self, db_session: AsyncSession):
        """
        初始化仓库

        Args:
            db_session: 数据库会话
        """
        self.db = db_session

    async def create(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens: Optional[int] = None
    ) -> str:
        """
        创建消息

        Args:
            session_id: 会话ID
            role: 消息角色
            content: 消息内容
            tokens: Token数量

        Returns:
            消息ID
        """
        message_id = str(uuid.uuid4())

        message = Message(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            tokens=tokens
        )

        self.db.add(message)
        await self.db.commit()

        return message_id

    async def get_by_session(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取会话的所有消息

        Args:
            session_id: 会话ID
            limit: 最大数量

        Returns:
            消息列表
        """
        query = select(Message).where(
            Message.session_id == session_id
        ).order_by(Message.created_at)

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_tokens(self, session_id: str) -> int:
        """
        统计会话的总token数

        Args:
            session_id: 会话ID

        Returns:
            总token数
        """
        messages = await self.get_by_session(session_id)
        return sum(m.tokens or 0 for m in messages)
