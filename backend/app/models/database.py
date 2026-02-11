"""
AI驱动游戏 - 数据库模型 v2.0

完全重构以支持AI驱动的游戏架构：
- 会话管理（sessions）
- 消息历史（messages）
- 上下文摘要（summaries）
- 关键事件（key_events）
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Float,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ============================================================================
# 会话管理
# ============================================================================

class Session(Base):
    """
    游戏会话表

    存储游戏实例的基本信息和元数据
    """
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, index=True)  # UUID

    # 会话元数据
    seed = Column(Integer, nullable=False, default=0)  # 随机种子（保证AI输出一致性）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 会话状态
    status = Column(String(20), nullable=False, default="active")  # active, completed, abandoned

    # 扩展字段（JSON格式，存储自定义配置）
    meta_data = Column(JSON, nullable=True)  # 例如：{"difficulty": "normal", "player_name": "xxx"}

    # 关联关系
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    summaries = relationship("Summary", back_populates="session", cascade="all, delete-orphan")
    key_events = relationship("KeyEvent", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id={self.id}, status={self.status}, created_at={self.created_at})>"


# ============================================================================
# 消息历史（AI对话）
# ============================================================================

class Message(Base):
    """
    消息表

    存储AI对话的完整历史，用于：
    1. 上下文重建
    2. 调试和分析
    3. 会话恢复
    """
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # 消息内容
    role = Column(String(20), nullable=False)  # system, user, assistant
    content = Column(Text, nullable=False)     # 消息文本

    # Token统计
    tokens = Column(Integer, nullable=True)    # 估算的token数量

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    session = relationship("Session", back_populates="messages")

    # 索引
    __table_args__ = (
        Index("idx_session_messages", "session_id", "created_at"),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


# ============================================================================
# 上下文摘要
# ============================================================================

class Summary(Base):
    """
    摘要表

    当上下文接近token限制时，AI自动生成摘要：
    1. 压缩历史消息
    2. 保留关键信息
    3. 释放token空间
    """
    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # 摘要内容
    summary_text = Column(Text, nullable=False)  # AI生成的摘要文本
    message_count = Column(Integer, nullable=False)  # 被摘要的消息数量

    # 摘要类型
    summary_type = Column(String(20), nullable=False, default="auto")  # auto, manual

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    session = relationship("Session", back_populates="summaries")

    # 索引
    __table_args__ = (
        Index("idx_session_summaries", "session_id", "created_at"),
    )

    def __repr__(self):
        return f"<Summary(id={self.id}, session_id={self.session_id}, message_count={self.message_count})>"


# ============================================================================
# 关键事件快照
# ============================================================================

class KeyEvent(Base):
    """
    关键事件表

    结构化存储游戏中的重要事件：
    1. 行动选择（action_choice）
    2. 里程碑（milestone）
    3. 检查点（checkpoint）

    用于：
    - 会话恢复时重建状态
    - 数据分析和游戏平衡
    - 调试和回放
    """
    __tablename__ = "key_events"

    id = Column(String(36), primary_key=True, index=True)  # UUID
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)

    # 事件类型
    event_type = Column(String(50), nullable=False)  # action_choice, milestone, checkpoint, game_over

    # 事件数据（JSON格式，结构化存储）
    event_data = Column(JSON, nullable=False)
    # 示例：
    # {
    #   "choice_id": "work_1",
    #   "choice_text": "绝命冲刺",
    #   "state_snapshot": {
    #     "day": 1,
    #     "turn": 2,
    #     "energy": 80,
    #     "progress": 15,
    #     ...
    #   },
    #   "ai_response": {
    #     "story": "...",
    #     "choices": [...]
    #   }
    # }

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关联关系
    session = relationship("Session", back_populates="key_events")

    # 索引
    __table_args__ = (
        Index("idx_session_events", "session_id", "created_at"),
        Index("idx_event_type", "event_type"),
    )

    def __repr__(self):
        return f"<KeyEvent(id={self.id}, event_type={self.event_type}, session_id={self.session_id})>"


# ============================================================================
# 辅助函数
# ============================================================================

def calculate_tokens(text: str) -> int:
    """
    估算文本的token数量

    粗略估算：中文约1字符=1token，英文约4字符=1token

    Args:
        text: 待估算的文本

    Returns:
        估算的token数量
    """
    # 简单估算：字符数 / 2（假设中英文混合）
    return len(text) // 2


# ============================================================================
# 数据库初始化
# ============================================================================

async def create_tables(engine):
    """
    创建所有表

    Args:
        engine: SQLAlchemy异步引擎
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine):
    """
    删除所有表（谨慎使用！）

    Args:
        engine: SQLAlchemy异步引擎
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
