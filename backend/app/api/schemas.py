"""
Pydantic 数据模型定义

从前端 TypeScript 类型迁移，确保前后端类型一致性

兼容 Python 3.9+
"""
from typing import Literal, Optional, List, Dict
from pydantic import BaseModel, Field
from enum import IntEnum


class PlayerLevel(IntEnum):
    """职场等级枚举"""
    INTERN = 0
    JUNIOR = 1
    SENIOR = 2
    LEAD = 3
    CTO = 4


# ========== 新增：职位和NPC相关模型 ==========


class PositionInfo(BaseModel):
    """职位信息"""
    level: PlayerLevel = Field(..., description="职位等级")
    title: str = Field(..., description="职位名称，如'实习生'、'初级工程师'等")
    description: str = Field(..., description="职位描述")


class NPCInfo(BaseModel):
    """NPC信息（老板/领导）- 简化版"""
    name: str = Field(..., description="NPC姓名")
    role: str = Field(..., description="角色类型（放宽为任意字符串）")  # 放宽限制
    personality: str = Field(..., description="性格特点")
    description: str = Field(..., description="外貌/行为描述")


# ========== 新增：游戏元数据和素材库相关模型 ==========


class GameMeta(BaseModel):
    """游戏元数据"""
    company_type: str = Field(..., description="公司类型（如'互联网大厂'、'传统国企'等）")
    style_type: str = Field(..., description="文案风格（如'互联网黑话风'、'官话套话风'等）")
    magical_level: Optional[str] = Field(None, description="魔幻程度：无/轻度/中度/重度（完全禁用验证，默认值 None）")
    seed_used: Optional[int] = Field(None, description="使用的随机种子")


class CompanyProfile(BaseModel):
    """公司详细档案"""
    name: str = Field(..., min_length=2, description="公司名称")  # 降低最小长度要求
    type: str = Field(..., description="公司类型")
    culture: str = Field(..., description="公司文化")
    atmosphere: str = Field(..., description="办公氛围")
    special_rules: List[str] = Field(
        default_factory=list, description="公司特殊规则"
    )
    magical_elements: List[str] = Field(
        default_factory=list, description="公司关联的魔幻元素"
    )
    style: Optional[str] = Field(None, description="文案风格")  # 改为可选字段，放宽验证


class NPCProfile(BaseModel):
    """NPC详细档案"""
    id: str = Field(..., description="NPC唯一标识")
    name: str = Field(..., description="NPC姓名")
    role: str = Field(..., description="角色类型（放宽为任意字符串）")  # 放宽限制
    personality: str = Field(..., description="性格特点")
    background: Optional[str] = Field(None, description="背景故事")
    appearance: Optional[str] = Field(None, description="外貌描述")
    relationships: Dict[str, str] = Field(
        default_factory=dict, description="与其他NPC的关系"
    )
    attitude_toward_player: int = Field(
        default=50, ge=0, le=100, description="对玩家好感度（0-100）"
    )
    secrets: List[str] = Field(default_factory=list, description="秘密列表")


class MagicalElement(BaseModel):
    """魔幻元素"""
    type: Literal["object", "phenomenon", "ability"] = Field(  # 恢复为枚举
        ..., description="元素类型：物品/现象/能力"
    )
    name: str = Field(..., description="元素名称")
    description: str = Field(..., description="元素描述")
    effect: str = Field(..., description="元素效果")


class NPCReaction(BaseModel):
    """NPC反应"""
    boss: Optional[str] = Field(None, description="老板的反应")
    colleagues: Optional[str] = Field(None, description="同事的反应")
    specific_npcs: Dict[str, str] = Field(
        default_factory=dict, description="特定NPC的反应 {npc_id: reaction}"
    )


class TriggeredEvent(BaseModel):
    """触发的事件"""
    id: Optional[str] = Field(None, description="事件ID（可选）")
    type: Literal["positive", "negative", "neutral", "magical", "threshold", "chain", "time", "random"] = Field(  # 恢复为枚举并扩展
        ..., description="事件类型"
    )
    message: Optional[str] = Field(None, description="事件描述")  # 改为可选
    effects: Dict[str, int] = Field(
        default_factory=dict, description="事件带来的属性影响"
    )


class CompanyInfo(BaseModel):
    """公司信息"""
    name: str = Field(..., description="公司名称")
    type: str = Field(..., description="公司类型（放宽为任意字符串）")  # 放宽限制
    culture: str = Field(..., description="公司文化描述")
    atmosphere: str = Field(..., description="办公氛围描述")


class WarmStory(BaseModel):
    """温暖剧情文本"""
    text: str = Field(..., description="温暖治愈的剧情文本")
    mood: str = Field(..., description="情绪类型（放宽为任意字符串）")  # 放宽限制


# ========== 原有模型 ==========


class ActionCost(BaseModel):
    """行动消耗"""
    energy: Optional[int] = Field(None, ge=0, le=100, description="精力消耗")
    money: Optional[int] = Field(None, ge=0, description="金钱消耗")
    chill: Optional[int] = Field(None, ge=0, le=100, description="摸鱼值消耗")


class ActionEffect(BaseModel):
    """行动效果"""
    stat: str = Field(..., description="影响的属性名")
    value: int = Field(..., description="影响数值（正负均可）")
    description: Optional[str] = Field(None, description="效果描述")


class AIChoice(BaseModel):
    """AI 生成的游戏选项"""
    id: str = Field(..., description="选项唯一标识")
    text: str = Field(..., min_length=1, max_length=100, description="选项描述（20字以内）")
    category: Optional[str] = Field(  # 改宽为任意字符串
        None, description="选项类别（放宽为任意字符串）"
    )
    effects: Dict[str, int] = Field(
        ...,
        description="属性影响字典，包含 energy/chill/progress/suspicion 等字段"
    )


class PlayerState(BaseModel):
    """玩家状态"""
    # 核心属性（前端可见）
    chill: float = Field(50, ge=0, le=100, description="摸鱼值 (0-100)")
    energy: float = Field(100, ge=0, le=100, description="精力值 (0-100)")
    connection: float = Field(0, ge=0, le=100, description="人脉值 (0-100)")
    blackmail: float = Field(0, ge=0, le=100, description="黑料值 (0-100)")

    # 隐藏属性（仅后端AI判定使用，不返回给前端）
    progress: float = Field(0, ge=0, le=100, description="工作进度 (0-100%) [隐藏]")
    suspicion: float = Field(0, ge=0, le=100, description="被怀疑度 (0-100) [隐藏]")

    # 资源属性
    salary: int = Field(5000, ge=0, description="薪水 (¥)")
    reputation: float = Field(0, ge=0, le=100, description="声望 (0-100)")

    # 进度属性
    level: PlayerLevel = Field(PlayerLevel.INTERN, description="职场等级")
    day: int = Field(1, ge=1, description="已工作天数")
    week: int = Field(1, ge=1, description="当前周数")
    turn: int = Field(0, ge=0, description="当天回合数")

    # 新增：职位信息
    position: Optional[PositionInfo] = Field(None, description="当前职位信息")

    # 解锁内容（由AI生成，无预设）
    unlocked_skills: List[str] = Field(
        default_factory=list, description="已解锁技能ID（由AI生成）"
    )
    unlocked_achievements: List[str] = Field(
        default_factory=list, description="已解锁成就ID"
    )
    seen_events: List[str] = Field(default_factory=list, description="已触发事件ID")


def filter_player_state_for_frontend(state: dict) -> dict:
    """
    过滤玩家状态，移除隐藏字段（suspicion和progress）

    Args:
        state: 完整的玩家状态字典

    Returns:
        过滤后的玩家状态（不包含suspicion和progress）
    """
    # 创建副本并移除隐藏字段
    filtered = state.copy()
    filtered.pop("suspicion", None)
    filtered.pop("progress", None)
    return filtered


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
    player_state: Dict = Field(..., description="初始玩家状态（可以是任意类型）")
    message: str = Field(..., description="欢迎消息")
    choices: List[AIChoice] = Field(default_factory=list, description="初始选项")

    # 游戏元数据（AI生成的创意设定）
    game_meta: Optional[GameMeta] = Field(None, description="游戏元数据")
    # 公司详细档案
    company_profile: Optional[CompanyProfile] = Field(None, description="公司详细档案")
    # NPC详细档案列表
    npcs: List[NPCProfile] = Field(
        default_factory=list, description="NPC详细档案列表（3-4个）"
    )
    # 当前触发的魔幻元素
    current_magical_element: Optional[MagicalElement] = Field(
        None, description="当前触发的魔幻元素"
    )


class ChoicesRequest(BaseModel):
    """获取选项请求"""
    session_id: str = Field(..., description="会话唯一标识")


class ChoicesResponse(BaseModel):
    """获取选项响应"""
    story_context: str = Field(..., description="当前剧情上下文（50字以内）")
    choices: List[AIChoice] = Field(..., min_length=1, description="AI生成的选项列表（数量由AI决定）")


class ChoiceSubmitRequest(BaseModel):
    """提交选择请求"""
    session_id: str = Field(..., description="会话唯一标识")
    choice_id: str = Field(..., description="选择的选项ID")


class ActionFeedback(BaseModel):
    """行动反馈"""
    success: str = Field(..., description="成功消息")
    flavor: List[str] = Field(default_factory=list, description="风味文字")


class ChoiceSubmitResponse(BaseModel):
    """提交选择响应"""
    success: bool = Field(..., description="是否成功")
    player_state: Dict = Field(..., description="更新后的玩家状态（可以是任意类型）")
    feedback: ActionFeedback = Field(..., description="行动反馈")
    # 触发的事件列表
    triggered_events: List[TriggeredEvent] = Field(
        default_factory=list, description="触发的事件列表"
    )
    game_over: bool = Field(False, description="游戏是否结束")
    game_over_reason: Optional[str] = Field(None, description="游戏结束原因")

    # NPC更新后的档案列表（因升职或态度变化）
    updated_npcs: List[NPCProfile] = Field(
        default_factory=list, description="NPC更新后的档案列表"
    )
    # NPC对玩家行为的反应
    npc_reaction: Optional[NPCReaction] = Field(None, description="NPC对玩家行为的反应")
    # 当前触发的魔幻元素
    current_magical_element: Optional[MagicalElement] = Field(
        None, description="当前触发的魔幻元素"
    )


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(None, description="详细错误信息")
