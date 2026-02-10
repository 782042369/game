"""
Pytest 配置和共享 fixture
"""
import pytest
from app.api.schemas import PlayerState
from app.core.constants import INITIAL_PLAYER_STATE


@pytest.fixture
def sample_player_state():
    """提供示例玩家状态"""
    return PlayerState(**INITIAL_PLAYER_STATE)


@pytest.fixture
def sample_ai_choice():
    """提供示例 AI 选项"""
    from app.api.schemas import AIChoice

    return AIChoice(
        id="test_choice",
        text="测试选项",
        category="work",
        effects={"energy": -10, "progress": 10},
    )
