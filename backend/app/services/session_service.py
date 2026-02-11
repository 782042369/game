"""
会话管理服务（v2 - AI驱动架构）

负责：
- 创建新游戏会话
- 会话恢复
- 会话状态管理
- 关键事件记录
"""
import random
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.repositories.session_repo import SessionRepository
from app.repositories.message_repo import MessageRepository
from app.models.database import KeyEvent


class SessionService:
    """会话管理服务（AI驱动版本）"""

    def __init__(self, db_session: AsyncSession):
        """
        初始化服务

        Args:
            db_session: 数据库会话
        """
        self.db = db_session
        self.session_repo = SessionRepository(db_session)
        self.message_repo = MessageRepository(db_session)

    async def create_game(
        self,
        player_name: str = "玩家",
        difficulty: str = "normal"
    ) -> Dict[str, Any]:
        """
        创建新游戏会话

        Args:
            player_name: 玩家名称
            difficulty: 难度（easy, normal, hard）

        Returns:
            会话信息
        """
        # 生成随机种子（保证同一会话内AI输出一致）
        seed = random.randint(0, 999999)

        # 创建会话
        session_id = await self.session_repo.create(
            seed=seed,
            metadata={
                "player_name": player_name,
                "difficulty": difficulty,
                "created_at": datetime.now().isoformat()
            }
        )

        # 添加初始系统消息
        await self.message_repo.create(
            session_id=session_id,
            role="system",
            content=f"新游戏开始。玩家：{player_name}，难度：{difficulty}。请生成初始剧情和选项。"
        )

        logger.info(f"✅ 创建新游戏 - Session: {session_id}, Player: {player_name}, Seed: {seed}")

        return {
            "session_id": session_id,
            "seed": seed,
            "player_name": player_name,
            "difficulty": difficulty
        }

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息或None
        """
        session = await self.session_repo.get(session_id)
        if not session:
            return None

        return {
            "id": session.id,
            "seed": session.seed,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "metadata": session.meta_data
        }

    async def record_key_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> str:
        """
        记录关键事件

        Args:
            session_id: 会话ID
            event_type: 事件类型（action_choice, milestone, game_over）
            event_data: 事件数据

        Returns:
            事件ID
        """
        event = KeyEvent(
            id=str(uuid.uuid4()),
            session_id=session_id,
            event_type=event_type,
            event_data=event_data
        )

        self.db.add(event)
        await self.db.commit()

        logger.info(f"✅ 记录事件 - Session: {session_id}, Type: {event_type}")

        return event.id

    async def end_session(
        self,
        session_id: str,
        reason: str,
        is_victory: bool = False
    ) -> bool:
        """
        结束会话

        Args:
            session_id: 会话ID
            reason: 结束原因
            is_victory: 是否胜利

        Returns:
            是否成功
        """
        # 更新会话状态
        success = await self.session_repo.update_status(session_id, "completed")

        if success:
            # 记录游戏结束事件
            await self.record_key_event(
                session_id=session_id,
                event_type="game_over",
                event_data={
                    "reason": reason,
                    "is_victory": is_victory
                }
            )

            logger.info(f"🏁 游戏结束 - Session: {session_id}, Reason: {reason}")

        return success
