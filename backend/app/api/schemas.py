"""
Pydantic 数据模型定义

从前端 TypeScript 类型迁移，确保前后端类型一致性
"""
from typing import Literal
from pydantic import BaseModel, Field
from enum import IntEnum


class PlayerLevel(IntEnum):
    """职场等级枚举"""
    INTERN = 0
    JUNIOR = 1
    SENIOR = 2
    LEAD = 3
    CTO = 4


class ActionCost(BaseModel):
    """行动消耗"""
    energy: int | None = Field(None, ge=0, le=100, description="精力消耗")
    money: int | None = Field(None, ge=0, description="金钱消耗")
    chill: int | None = Field(None, ge=0, le=100, description="摸鱼值消耗")


class ActionEffect(BaseModel):
    """行动效果"""
    stat: str = Field(..., description="影响的属性名")
    value: int = Field(..., description="影响数值（正负均可）")
    description: str | None = Field(None, description="效果描述")


class AIChoice(BaseModel):
    """AI 生成的游戏选项"""
    id: str = Field(..., description="选项唯一标识")
    text: str = Field(..., min_length=1, max_length=100, description="选项描述（20字以内）")
    category: Literal["work", "slack", "skill", "social", "growth"] = Field(
        ..., description="选项类别"
    )
    effects: dict[str, int] = Field(
        ...,
        description="属性影响字典，包含 energy/chill/progress/suspicion 等字段"
    )


class PlayerState(BaseModel):
    """玩家状态"""
    # 核心属性
    chill: float = Field(50, ge=0, le=100, description="摸鱼值 (0-100)")
    progress: float = Field(0, ge=0, le=100, description="工作进度 (0-100%)")
    suspicion: float = Field(0, ge=0, le=100, description="被怀疑度 (0-100)")
    energy: float = Field(100, ge=0, le=100, description="精力值 (0-100)")

    # 资源属性
    salary: int = Field(5000, ge=0, description="薪水 ($)")
    reputation: float = Field(0, ge=0, le=100, description="声望 (0-100)")

    # 进度属性
    level: PlayerLevel = Field(PlayerLevel.INTERN, description="职场等级")
    day: int = Field(1, ge=1, le=30, description="当前天数 (1-30)")
    week: int = Field(1, ge=1, le=4, description="当前周数 (1-4)")
    turn: int = Field(0, ge=0, le=7, description="当天回合数 (0-7)")

    # 解锁内容
    unlocked_skills: list[str] = Field(
        default_factory=lambda: ["alt_tab_master"], description="已解锁技能ID"
    )
    unlocked_achievements: list[str] = Field(
        default_factory=list, description="已解锁成就ID"
    )
    seen_events: list[str] = Field(default_factory=list, description="已触发事件ID")


# ========== API 请求/响应模型 ==========


class GameStartRequest(BaseModel):
    """开始游戏请求"""
    player_name: str = Field(..., min_length=1, max_length=50, description="玩家昵称")
    difficulty: Literal["normal", "easy", "hard"] = Field(
        "normal", description="游戏难度"
    )


class GameStartResponse(BaseModel):
    """开始游戏响应"""
    session_id: str = Field(..., description="会话唯一标识")
    player_state: PlayerState = Field(..., description="初始玩家状态")
    message: str = Field(..., description="欢迎消息")


class ChoicesRequest(BaseModel):
    """获取选项请求"""
    session_id: str = Field(..., description="会话唯一标识")


class ChoicesResponse(BaseModel):
    """获取选项响应"""
    story_context: str = Field(..., description="当前剧情上下文（50字以内）")
    choices: list[AIChoice] = Field(..., min_length=5, max_length=5, description="5个AI生成的选项")


class ChoiceSubmitRequest(BaseModel):
    """提交选择请求"""
    session_id: str = Field(..., description="会话唯一标识")
    choice_id: str = Field(..., description="选择的选项ID")


class ActionFeedback(BaseModel):
    """行动反馈"""
    success: str = Field(..., description="成功消息")
    flavor: list[str] = Field(default_factory=list, description="风味文字")


class ChoiceSubmitResponse(BaseModel):
    """提交选择响应"""
    success: bool = Field(..., description="是否成功")
    player_state: PlayerState = Field(..., description="更新后的玩家状态")
    feedback: ActionFeedback = Field(..., description="行动反馈")
    triggered_events: list[str] = Field(
        default_factory=list, description="触发的随机事件ID列表"
    )
    game_over: bool = Field(False, description="游戏是否结束")
    game_over_reason: str | None = Field(None, description="游戏结束原因")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误消息")
    detail: str | None = Field(None, description="详细错误信息")
