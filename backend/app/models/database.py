"""
数据库模型定义

使用 SQLAlchemy ORM 定义游戏相关的数据库表结构
"""
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Session(Base):
    """游戏会话表"""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)  # UUID
    player_name = Column(String(50), nullable=False)
    difficulty = Column(String(10), nullable=False)  # 'easy', 'normal', 'hard'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_game_over = Column(Boolean, default=False, nullable=False)
    game_over_reason = Column(String(500), nullable=True)

    # 关联玩家状态（一对一）
    player_state = relationship("PlayerState", back_populates="session", uselist=False)

    # 关联历史记录（一对多）
    action_history = relationship("ActionHistory", back_populates="session", cascade="all, delete-orphan")


class PlayerState(Base):
    """玩家状态表"""

    __tablename__ = "player_states"

    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True)

    # 核心属性
    chill = Column(Float, default=50, nullable=False)
    progress = Column(Float, default=0, nullable=False)
    suspicion = Column(Float, default=0, nullable=False)
    energy = Column(Float, default=100, nullable=False)

    # 资源属性
    salary = Column(Integer, default=5000, nullable=False)
    reputation = Column(Float, default=0, nullable=False)

    # 进度属性
    level = Column(Integer, default=0, nullable=False)  # PlayerLevel 枚举值
    day = Column(Integer, default=1, nullable=False)
    week = Column(Integer, default=1, nullable=False)
    turn = Column(Integer, default=0, nullable=False)

    # 解锁内容（JSON 格式存储）
    unlocked_skills = Column(JSON, default=list, nullable=False)
    unlocked_achievements = Column(JSON, default=list, nullable=False)
    seen_events = Column(JSON, default=list, nullable=False)

    # 关联会话（多对一）
    session = relationship("Session", back_populates="player_state")


class ActionHistory(Base):
    """行动历史表（用于 AI 上下文）"""

    __tablename__ = "action_history"

    id = Column(String, primary_key=True, index=True)  # UUID
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 选择的选项信息
    choice_id = Column(String(100), nullable=False)
    choice_text = Column(String(200), nullable=False)
    effects = Column(JSON, nullable=False)  # 选项的属性影响

    # 更新后的玩家状态快照（可选，用于数据分析）
    player_state_snapshot = Column(JSON, nullable=True)

    # 关联会话（多对一）
    session = relationship("Session", back_populates="action_history")
