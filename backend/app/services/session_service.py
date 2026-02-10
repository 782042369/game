"""
会话管理服务

负责游戏会话的 CRUD 操作和玩家状态管理
"""
import uuid
from datetime import datetime
from sqlalchemy import select, desc
from loguru import logger

from app.models.database import Session, PlayerState, ActionHistory
from app.api.schemas import PlayerState as PlayerStateSchema
from app.repositories.database import get_db_session


class SessionService:
    """会话管理服务类"""

    async def create_session(
        self,
        player_name: str,
        difficulty: str,
        initial_state: PlayerStateSchema,
    ) -> str:
        """
        创建新游戏会话

        Args:
            player_name: 玩家昵称
            difficulty: 游戏难度
            initial_state: 初始玩家状态

        Returns:
            会话 ID
        """
        session_id = str(uuid.uuid4())

        async with get_db_session() as db:
            # 创建会话
            db_session = Session(
                id=session_id,
                player_name=player_name,
                difficulty=difficulty,
            )

            # 创建玩家状态
            db_player_state = PlayerState(
                session_id=session_id,
                chill=initial_state.chill,
                progress=initial_state.progress,
                suspicion=initial_state.suspicion,
                energy=initial_state.energy,
                salary=initial_state.salary,
                reputation=initial_state.reputation,
                level=initial_state.level.value,  # 枚举转整数值
                day=initial_state.day,
                week=initial_state.week,
                turn=initial_state.turn,
                unlocked_skills=initial_state.unlocked_skills,
                unlocked_achievements=initial_state.unlocked_achievements,
                seen_events=initial_state.seen_events,
            )

            db_session.player_state = db_player_state

            db.add(db_session)
            await db.commit()

            logger.info(f"✅ 创建新会话 - ID: {session_id}, 玩家: {player_name}")

        return session_id

    async def get_player_state(self, session_id: str) -> PlayerStateSchema | None:
        """
        获取玩家状态

        Args:
            session_id: 会话 ID

        Returns:
            玩家状态对象，如果会话不存在则返回 None
        """
        async with get_db_session() as db:
            result = await db.execute(
                select(PlayerState).where(PlayerState.session_id == session_id)
            )
            db_state = result.scalar_one_or_none()

            if db_state is None:
                return None

            # 转换为 Pydantic 模型
            return self._db_to_schema(db_state)

    async def save_player_state(
        self,
        session_id: str,
        state: PlayerStateSchema,
    ) -> bool:
        """
        保存玩家状态

        Args:
            session_id: 会话 ID
            state: 新的玩家状态

        Returns:
            是否成功
        """
        async with get_db_session() as db:
            result = await db.execute(
                select(PlayerState).where(PlayerState.session_id == session_id)
            )
            db_state = result.scalar_one_or_none()

            if db_state is None:
                logger.warning(f"⚠️ 会话 {session_id} 不存在，无法保存状态")
                return False

            # 更新字段
            db_state.chill = state.chill
            db_state.progress = state.progress
            db_state.suspicion = state.suspicion
            db_state.energy = state.energy
            db_state.salary = state.salary
            db_state.reputation = state.reputation
            db_state.level = state.level.value
            db_state.day = state.day
            db_state.week = state.week
            db_state.turn = state.turn
            db_state.unlocked_skills = state.unlocked_skills
            db_state.unlocked_achievements = state.unlocked_achievements
            db_state.seen_events = state.seen_events

            await db.commit()

            logger.debug(f"💾 保存玩家状态 - Session: {session_id}")

        return True

    async def get_session_info(self, session_id: str) -> dict | None:
        """
        获取会话信息

        Args:
            session_id: 会话 ID

        Returns:
            会话信息字典，如果会话不存在则返回 None
        """
        async with get_db_session() as db:
            result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            db_session = result.scalar_one_or_none()

            if db_session is None:
                return None

            return {
                "id": db_session.id,
                "player_name": db_session.player_name,
                "difficulty": db_session.difficulty,
                "created_at": db_session.created_at.isoformat(),
                "is_game_over": db_session.is_game_over,
                "game_over_reason": db_session.game_over_reason,
            }

    async def mark_game_over(
        self,
        session_id: str,
        reason: str,
    ) -> bool:
        """
        标记游戏结束

        Args:
            session_id: 会话 ID
            reason: 游戏结束原因

        Returns:
            是否成功
        """
        async with get_db_session() as db:
            result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            db_session = result.scalar_one_or_none()

            if db_session is None:
                logger.warning(f"⚠️ 会话 {session_id} 不存在，无法标记游戏结束")
                return False

            db_session.is_game_over = True
            db_session.game_over_reason = reason

            await db.commit()

            logger.info(f"🏁 游戏结束 - Session: {session_id}, 原因: {reason}")

        return True

    async def add_action_history(
        self,
        session_id: str,
        choice_id: str,
        choice_text: str,
        effects: dict,
        player_state_snapshot: dict | None = None,
    ) -> bool:
        """
        添加行动历史记录

        Args:
            session_id: 会话 ID
            choice_id: 选项 ID
            choice_text: 选项文本
            effects: 属性影响
            player_state_snapshot: 玩家状态快照（可选）

        Returns:
            是否成功
        """
        history_id = str(uuid.uuid4())

        async with get_db_session() as db:
            # 验证会话是否存在
            result = await db.execute(
                select(Session).where(Session.id == session_id)
            )
            db_session = result.scalar_one_or_none()

            if db_session is None:
                logger.warning(f"⚠️ 会话 {session_id} 不存在，无法添加历史记录")
                return False

            # 创建历史记录
            history = ActionHistory(
                id=history_id,
                session_id=session_id,
                choice_id=choice_id,
                choice_text=choice_text,
                effects=effects,
                player_state_snapshot=player_state_snapshot,
            )

            db.add(history)
            await db.commit()

            logger.debug(f"📝 添加历史记录 - Session: {session_id}, Choice: {choice_text}")

        return True

    async def get_recent_history(
        self,
        session_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """
        获取最近的行动历史

        Args:
            session_id: 会话 ID
            limit: 返回记录数量限制

        Returns:
            历史记录列表
        """
        async with get_db_session() as db:
            result = await db.execute(
                select(ActionHistory)
                .where(ActionHistory.session_id == session_id)
                .order_by(desc(ActionHistory.created_at))
                .limit(limit)
            )
            history_records = result.scalars().all()

            # 转换为字典列表
            return [
                {
                    "choice_id": record.choice_id,
                    "choice_text": record.choice_text,
                    "effects": record.effects,
                    "created_at": record.created_at.isoformat(),
                }
                for record in history_records
            ]

    def _db_to_schema(self, db_state: PlayerState) -> PlayerStateSchema:
        """
        将数据库模型转换为 Pydantic 模型

        Args:
            db_state: 数据库玩家状态对象

        Returns:
            Pydantic 玩家状态对象
        """
        from app.api.schemas import PlayerLevel

        return PlayerStateSchema(
            chill=db_state.chill,
            progress=db_state.progress,
            suspicion=db_state.suspicion,
            energy=db_state.energy,
            salary=db_state.salary,
            reputation=db_state.reputation,
            level=PlayerLevel(db_state.level),  # 整数值转枚举
            day=db_state.day,
            week=db_state.week,
            turn=db_state.turn,
            unlocked_skills=db_state.unlocked_skills or [],
            unlocked_achievements=db_state.unlocked_achievements or [],
            seen_events=db_state.seen_events or [],
        )
