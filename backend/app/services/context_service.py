"""
上下文管理服务

负责：
1. 管理对话历史（messages表）
2. Token计数和预警
3. 自动触发摘要（接近token限制时）
4. 重建会话上下文（messages + summaries）
5. 混合摘要策略（结构化 + AI摘要）
"""
import json
import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.database import Message, Summary, KeyEvent, calculate_tokens
from app.services.ai_service_v2 import AIServiceV2


class ContextService:
    """
    上下文管理服务

    负责管理AI对话的上下文，包括消息历史、摘要、会话恢复等
    """

    def __init__(self, db_session: AsyncSession, ai_service: AIServiceV2):
        """
        初始化上下文服务

        Args:
            db_session: 数据库会话
            ai_service: AI服务实例
        """
        self.db = db_session
        self.ai = ai_service

    # ========================================================================
    # 消息管理
    # ========================================================================

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tokens: Optional[int] = None
    ) -> str:
        """
        添加消息到历史

        Args:
            session_id: 会话ID
            role: 消息角色（system, user, assistant）
            content: 消息内容
            tokens: Token数量（可选，自动估算）

        Returns:
            消息ID
        """
        message_id = str(uuid.uuid4())

        # 估算token数量
        if tokens is None:
            tokens = calculate_tokens(content)

        # 创建消息记录
        message = Message(
            id=message_id,
            session_id=session_id,
            role=role,
            content=content,
            tokens=tokens,
        )

        self.db.add(message)
        await self.db.commit()

        logger.info(f"✅ 添加消息 - Session: {session_id}, Role: {role}, Tokens: {tokens}")

        return message_id

    async def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取会话的消息历史

        Args:
            session_id: 会话ID
            limit: 最大返回数量（None=全部）

        Returns:
            消息列表（按时间排序）
        """
        query = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        messages = result.scalars().all()

        return list(messages)

    async def get_context_for_ai(
        self,
        session_id: str,
        token_limit: int = 12000
    ) -> List[dict]:
        """
        获取用于AI调用的上下文（自动处理摘要）

        Args:
            session_id: 会话ID
            token_limit: Token限制（默认12000）

        Returns:
            消息列表（适合传给OpenAI API）
        """
        # 1. 获取所有摘要
        summaries = await self.get_summaries(session_id)

        # 2. 获取最近的未摘要消息
        recent_messages = await self.get_messages(session_id, limit=100)

        # 3. 计算当前token数量
        total_tokens = sum(m.tokens or 0 for m in recent_messages)

        # 4. 如果接近限制，触发摘要
        if total_tokens > token_limit * 0.8:
            logger.warning(f"⚠️ 上下文接近限制 - Session: {session_id}, Tokens: {total_tokens}")
            await self._auto_summarize(session_id)

            # 重新获取消息
            recent_messages = await self.get_messages(session_id, limit=50)

        # 5. 构建上下文（摘要 + 最近消息）
        context = []

        # 添加摘要
        for summary in summaries:
            context.append({
                "role": "system",
                "content": f"[历史摘要] {summary.summary_text}"
            })

        # 添加最近消息
        for message in recent_messages:
            context.append({
                "role": message.role,
                "content": message.content
            })

        logger.info(f"📝 构建上下文 - Session: {session_id}, Messages: {len(context)}, Tokens: ~{total_tokens}")

        return context

    # ========================================================================
    # 摘要管理
    # ========================================================================

    async def get_summaries(self, session_id: str) -> List[Summary]:
        """
        获取会话的所有摘要

        Args:
            session_id: 会话ID

        Returns:
            摘要列表（按时间排序）
        """
        query = select(Summary).where(
            Summary.session_id == session_id
        ).order_by(Summary.created_at)

        result = await self.db.execute(query)
        summaries = result.scalars().all()

        return list(summaries)

    async def create_summary(
        self,
        session_id: str,
        messages_to_summarize: List[Message]
    ) -> Summary:
        """
        创建摘要（混合策略：结构化 + AI）

        Args:
            session_id: 会话ID
            messages_to_summarize: 需要摘要的消息列表

        Returns:
            创建的摘要对象
        """
        logger.info(f"🔄 开始摘要 - Session: {session_id}, Messages: {len(messages_to_summarize)}")

        # 1. 提取关键事件（结构化）
        key_events = await self._extract_key_events(session_id, messages_to_summarize)

        # 2. 调用AI生成叙事摘要
        messages_text = "\n".join([
            f"{m.role}: {m.content}" for m in messages_to_summarize
        ])

        ai_summary = await self.ai.create_summary(messages_text)

        # 3. 组合摘要
        combined_summary = self._format_summary(key_events, ai_summary)

        # 4. 保存摘要
        summary = Summary(
            id=str(uuid.uuid4()),
            session_id=session_id,
            summary_text=combined_summary,
            message_count=len(messages_to_summarize),
            summary_type="auto"
        )

        self.db.add(summary)
        await self.db.commit()

        logger.success(f"✅ 摘要完成 - Session: {session_id}, Messages: {len(messages_to_summarize)}")

        return summary

    async def _auto_summarize(self, session_id: str):
        """
        自动摘要（当接近token限制时）

        Args:
            session_id: 会话ID
        """
        # 获取所有未摘要的消息
        messages = await self.get_messages(session_id)

        if len(messages) < 5:  # 至少5条消息才摘要
            return

        # 摘要前50%的消息
        messages_to_summarize = messages[:len(messages) // 2]

        await self.create_summary(session_id, messages_to_summarize)

        # 删除已摘要的消息（可选）
        # for msg in messages_to_summarize:
        #     await self.db.delete(msg)
        # await self.db.commit()

    async def _extract_key_events(
        self,
        session_id: str,
        messages: List[Message]
    ) -> List[dict]:
        """
        从消息中提取关键事件

        Args:
            session_id: 会话ID
            messages: 消息列表

        Returns:
            关键事件列表
        """
        # 从key_events表查询
        query = select(KeyEvent).where(
            and_(
                KeyEvent.session_id == session_id,
                KeyEvent.event_type == "action_choice"
            )
        ).order_by(KeyEvent.created_at)

        result = await self.db.execute(query)
        events = result.scalars().all()

        return [
            {
                "choice": e.event_data.get("choice_text"),
                "state": e.event_data.get("state_snapshot")
            }
            for e in events
        ]

    def _format_summary(self, key_events: List[dict], ai_summary: str) -> str:
        """
        格式化摘要（组合结构化事件和AI摘要）

        Args:
            key_events: 关键事件列表
            ai_summary: AI生成的摘要

        Returns:
            格式化的摘要文本
        """
        parts = []

        # 关键事件
        if key_events:
            parts.append("【关键事件】")
            for event in key_events:
                parts.append(f"- {event.get('choice', 'Unknown')}")

        # AI摘要
        parts.append(f"\n【剧情摘要】\n{ai_summary}")

        return "\n".join(parts)

    # ========================================================================
    # 会话恢复
    # ========================================================================

    async def rebuild_context(self, session_id: str) -> List[dict]:
        """
        重建会话上下文（从messages和summaries）

        Args:
            session_id: 会话ID

        Returns:
            完整的上下文列表
        """
        logger.info(f"🔄 重建上下文 - Session: {session_id}")

        # 获取摘要
        summaries = await self.get_summaries(session_id)

        # 获取所有消息
        messages = await self.get_messages(session_id)

        # 构建上下文
        context = []

        # 添加摘要作为系统消息
        for summary in summaries:
            context.append({
                "role": "system",
                "content": f"[会话摘要] {summary.summary_text}"
            })

        # 添加所有消息
        for message in messages:
            context.append({
                "role": message.role,
                "content": message.content
            })

        logger.info(f"✅ 上下文重建完成 - Summaries: {len(summaries)}, Messages: {len(messages)}")

        return context

    # ========================================================================
    # Token统计
    # ========================================================================

    async def get_token_stats(self, session_id: str) -> dict:
        """
        获取会话的token统计

        Args:
            session_id: 会话ID

        Returns:
            Token统计信息
        """
        messages = await self.get_messages(session_id)

        total_tokens = sum(m.tokens or 0 for m in messages)

        return {
            "total_messages": len(messages),
            "total_tokens": total_tokens,
            "avg_tokens_per_message": total_tokens / len(messages) if messages else 0,
            "estimated_cost_usd": total_tokens * 0.00001,  # 粗略估算
        }
