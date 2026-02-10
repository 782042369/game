"""
游戏引擎核心逻辑

从前端 TypeScript (engine.ts) 迁移，负责：
- 属性计算和限制
- 回合和天数更新
- 工作日结束处理
- 随机事件触发
- 游戏结束判定
"""
import random
from typing import Literal

from app.api.schemas import PlayerState, AIChoice, ActionFeedback, PlayerLevel
from app.core.constants import (
    MAX_TURNS_PER_DAY,
    MAX_DAYS,
    GAME_OVER_CONDITIONS,
    VICTORY_CONDITIONS,
)


class GameEngine:
    """游戏引擎类，处理核心游戏逻辑"""

    def __init__(self, seed: int | None = None):
        """
        初始化游戏引擎

        Args:
            seed: 随机数种子（用于测试或可重现的游戏）
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def calculate_new_state(
        self, current_state: PlayerState, choice: AIChoice
    ) -> tuple[PlayerState, ActionFeedback, list[str]]:
        """
        计算选择后的新玩家状态

        Args:
            current_state: 当前玩家状态
            choice: AI 生成的选项

        Returns:
            (新玩家状态, 行动反馈, 触发的事件ID列表)
        """
        # 将 Pydantic 模型转换为字典以便修改
        state_dict = current_state.model_copy()

        # 应用精力消耗
        energy_cost = choice.effects.get("energy", 0)
        if energy_cost > 0:
            state_dict.energy = max(0, state_dict.energy - energy_cost)

        # 应用其他效果
        for stat, value in choice.effects.items():
            if stat == "energy":
                continue  # 已经处理过了

            current_val = getattr(state_dict, stat, 0)
            new_val = current_val + value

            # 限制属性范围
            if stat in ["chill", "progress", "suspicion", "energy", "reputation"]:
                new_val = max(0, min(100, new_val))

            setattr(state_dict, stat, new_val)

        # 更新回合
        state_dict.turn += 1

        # 检查工作日结束
        triggered_events = []
        if state_dict.turn >= MAX_TURNS_PER_DAY:
            state_dict.turn = 0
            state_dict.day += 1
            state_dict.energy = 100  # 次日体力恢复
            # 进度衰减（模拟项目变动或被同事拖累）
            state_dict.progress = max(0, state_dict.progress - 2)

            # 更新周数
            state_dict.week = (state_dict.day - 1) // 7 + 1

        # 随机事件判定
        triggered_events = self._trigger_random_events()

        # 生成行动反馈
        feedback = self._generate_feedback(choice)

        return state_dict, feedback, triggered_events

    def check_game_over(
        self, state: PlayerState, difficulty: Literal["normal", "easy", "hard"]
    ) -> tuple[bool, str | None]:
        """
        检查游戏是否结束

        Args:
            state: 当前玩家状态
            difficulty: 游戏难度

        Returns:
            (是否结束, 结束原因)
        """
        # 失败条件1：怀疑度达到100被开除
        if state.suspicion >= GAME_OVER_CONDITIONS["suspicion_max"]:
            return True, "你被老板发现了摸鱼行为，当场开除！"

        # 失败条件2：30天后进度不足
        if state.day >= MAX_DAYS:
            min_progress = GAME_OVER_CONDITIONS[f"progress_min_{difficulty}"]
            if state.progress < min_progress:
                return True, f"30天结束了，你的项目进度只有 {state.progress:.0f}%，未达到 {difficulty} 模式的 {min_progress}% 要求，被老板开了！"

        # 胜利条件：30天后进度达到目标
        if state.day >= MAX_DAYS:
            if state.progress >= VICTORY_CONDITIONS["progress_target"]:
                return True, f"恭喜！你在30天内完成了100%的项目进度，成功摸鱼并交付项目！老王我都佩服你！"

            # 普通结局：30天后进度及格但未完美
            min_progress = GAME_OVER_CONDITIONS[f"progress_min_{difficulty}"]
            if state.progress >= min_progress:
                return True, f"30天结束了，你的项目进度达到 {state.progress:.0f}%，勉强及格。老板对你还算满意。"

        return False, None

    def _trigger_random_events(self) -> list[str]:
        """
        触发随机事件

        Returns:
            触发的事件ID列表
        """
        triggered_events = []
        rand = random.random()

        # 20% 概率触发老板巡逻
        if rand < 0.2:
            triggered_events.append("boss_patrol")
        # 5% 概率触发咖啡泼洒事件
        elif rand < 0.05:
            triggered_events.append("coffee_spill")

        return triggered_events

    def _generate_feedback(self, choice: AIChoice) -> ActionFeedback:
        """
        生成行动反馈

        Args:
            choice: 玩家选择的选项

        Returns:
            行动反馈对象
        """
        flavor_texts = [
            "生活不只有眼前的 Bug，还有远方的摸鱼。",
            "只要我摸得够快，KPI 就追不上我。",
            "这就是程序员的生存智慧！",
            "老板看不见我，老板看不见我...",
            "代码写得再好，不如摸鱼摸得巧。",
        ]

        feedback = ActionFeedback(
            success=f"顺利完成了：{choice.text}",
            flavor=random.sample(flavor_texts, min(2, len(flavor_texts))),
        )

        return feedback
