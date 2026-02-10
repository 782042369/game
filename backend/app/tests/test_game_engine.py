"""
游戏引擎单元测试

测试 GameEngine 类的核心逻辑
"""
import pytest
from app.api.schemas import PlayerState, AIChoice, PlayerLevel
from app.core.game_engine import GameEngine
from app.core.constants import INITIAL_PLAYER_STATE


class TestGameEngine:
    """游戏引擎测试类"""

    def test_calculate_new_state_basic(self):
        """测试基本的状态计算"""
        engine = GameEngine()
        initial_state = PlayerState(**INITIAL_PLAYER_STATE)

        choice = AIChoice(
            id="test_choice",
            text="测试选项",
            category="work",
            effects={"energy": -10, "progress": 10, "chill": -5, "suspicion": 0},
        )

        new_state, feedback, events = engine.calculate_new_state(initial_state, choice)

        # 验证精力消耗
        assert new_state.energy == 90  # 100 - 10
        # 验证进度增加
        assert new_state.progress == 10
        # 验证摸鱼值减少
        assert new_state.chill == 45  # 50 - 5
        # 验证回合增加
        assert new_state.turn == 1

    def test_clamp_values(self):
        """测试属性范围限制"""
        engine = GameEngine()
        initial_state = PlayerState(**INITIAL_PLAYER_STATE)

        # 创建一个会导致属性超出范围的选项
        choice = AIChoice(
            id="test_choice",
            text="测试选项",
            category="work",
            effects={"energy": -200, "progress": 150, "chill": 200, "suspicion": 50},
        )

        new_state, _, _ = engine.calculate_new_state(initial_state, choice)

        # 验证属性被限制在 0-100 范围内
        assert new_state.energy == 0  # 不应该小于0
        assert new_state.progress == 100  # 不应该大于100
        assert new_state.chill == 100  # 不应该大于100
        assert new_state.suspicion == 50

    def test_day_end_reset(self):
        """测试工作日结束时的状态重置"""
        engine = GameEngine()
        # 创建一个接近工作日结束的状态
        state_dict = INITIAL_PLAYER_STATE.copy()
        state_dict["turn"] = 7  # 最后一个回合
        initial_state = PlayerState(**state_dict)

        choice = AIChoice(
            id="test_choice",
            text="测试选项",
            category="work",
            effects={"energy": -10, "progress": 5},
        )

        new_state, _, _ = engine.calculate_new_state(initial_state, choice)

        # 验证工作日结束后的状态
        assert new_state.turn == 0  # 回合重置
        assert new_state.day == 2  # 天数增加
        assert new_state.energy == 100  # 体力恢复
        # 进度应该有衰减，但不会小于0
        assert new_state.progress >= 0

    def test_check_game_over_suspicion(self):
        """测试怀疑度达到100时的游戏结束判定"""
        engine = GameEngine()
        state_dict = INITIAL_PLAYER_STATE.copy()
        state_dict["suspicion"] = 100
        state_dict["day"] = 15
        state = PlayerState(**state_dict)

        is_over, reason = engine.check_game_over(state, "normal")

        assert is_over is True
        assert "开除" in reason

    def test_check_game_over_progress_fail(self):
        """测试30天后进度不足时的失败判定"""
        engine = GameEngine()
        state_dict = INITIAL_PLAYER_STATE.copy()
        state_dict["day"] = 30
        state_dict["progress"] = 40  # 未达到普通模式的70%要求
        state = PlayerState(**state_dict)

        is_over, reason = engine.check_game_over(state, "normal")

        assert is_over is True
        assert "未达到" in reason or "被老板开了" in reason

    def test_check_game_over_victory(self):
        """测试30天后进度达到100%的胜利判定"""
        engine = GameEngine()
        state_dict = INITIAL_PLAYER_STATE.copy()
        state_dict["day"] = 30
        state_dict["progress"] = 100
        state = PlayerState(**state_dict)

        is_over, reason = engine.check_game_over(state, "normal")

        assert is_over is True
        assert "恭喜" in reason or "成功" in reason

    def test_check_game_not_over(self):
        """测试游戏未结束的情况"""
        engine = GameEngine()
        state = PlayerState(**INITIAL_PLAYER_STATE)

        is_over, reason = engine.check_game_over(state, "normal")

        assert is_over is False
        assert reason is None

    def test_random_events(self):
        """测试随机事件触发（通过设置种子）"""
        engine = GameEngine(seed=42)  # 使用固定种子

        # 多次调用，验证随机性
        events_list = [engine._trigger_random_events() for _ in range(10)]

        # 验证有事件被触发（虽然种子固定，但至少应该触发一些事件）
        total_events = sum(len(events) for events in events_list)
        assert total_events > 0
