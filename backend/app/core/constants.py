"""
游戏常量定义

从前端 TypeScript 代码迁移
"""
from app.api.schemas import PlayerState, PlayerLevel

# 游戏核心常量
MAX_TURNS_PER_DAY = 8
MAX_DAYS = 30
MAX_WEEKS = 4
PERIODS = ["morning", "afternoon", "evening", "night"]

# 初始玩家状态
INITIAL_PLAYER_STATE = {
    "chill": 50,
    "progress": 0,
    "suspicion": 0,
    "energy": 100,
    "salary": 5000,
    "reputation": 0,
    "level": PlayerLevel.INTERN,
    "day": 1,
    "week": 1,
    "turn": 0,
    "unlocked_skills": ["alt_tab_master"],
    "unlocked_achievements": [],
    "seen_events": [],
}

# 游戏结束判定条件
GAME_OVER_CONDITIONS = {
    "suspicion_max": 100,  # 怀疑度达到100被开除
    "progress_min_easy": 50,  # 简单模式：30天后进度需达到50%
    "progress_min_normal": 70,  # 普通模式：30天后进度需达到70%
    "progress_min_hard": 100,  # 困难模式：30天后进度需达到100%
}

# 胜利条件
VICTORY_CONDITIONS = {
    "progress_target": 100,  # 进度达到100%即胜利
}
