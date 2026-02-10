"""
API 端点集成测试

测试 FastAPI 路由的功能
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.schemas import PlayerState, PlayerLevel


client = TestClient(app)


class TestGameAPI:
    """游戏 API 测试类"""

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "running"

    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_start_game(self):
        """测试开始游戏接口"""
        request_data = {
            "player_name": "测试玩家",
            "difficulty": "normal",
        }

        response = client.post("/api/game/start", json=request_data)

        assert response.status_code == 201
        data = response.json()

        # 验证响应结构
        assert "session_id" in data
        assert "player_state" in data
        assert "message" in data

        # 验证初始玩家状态
        player_state = data["player_state"]
        assert player_state["energy"] == 100
        assert player_state["chill"] == 50
        assert player_state["progress"] == 0
        assert player_state["suspicion"] == 0
        assert player_state["day"] == 1
        assert player_state["turn"] == 0

    def test_start_game_invalid_difficulty(self):
        """测试无效的难度参数"""
        request_data = {
            "player_name": "测试玩家",
            "difficulty": "invalid",  # 无效难度
        }

        response = client.post("/api/game/start", json=request_data)

        # 应该返回422验证错误
        assert response.status_code == 422

    def test_get_choices(self):
        """测试获取选项接口"""
        # 先创建一个会话
        start_response = client.post(
            "/api/game/start",
            json={"player_name": "测试玩家", "difficulty": "normal"},
        )
        session_id = start_response.json()["session_id"]

        # 获取选项
        response = client.post(
            "/api/game/choices",
            json={"session_id": session_id},
        )

        assert response.status_code == 200
        data = response.json()

        # 验证响应结构
        assert "story_context" in data
        assert "choices" in data
        assert len(data["choices"]) == 5

        # 验证选项结构
        choice = data["choices"][0]
        assert "id" in choice
        assert "text" in choice
        assert "category" in choice
        assert "effects" in choice

    def test_get_choices_invalid_session(self):
        """测试使用无效会话ID获取选项"""
        response = client.post(
            "/api/game/choices",
            json={"session_id": "invalid-session-id"},
        )

        assert response.status_code == 404

    def test_submit_choice(self):
        """测试提交选择接口"""
        # 先创建会话并获取选项
        start_response = client.post(
            "/api/game/start",
            json={"player_name": "测试玩家", "difficulty": "normal"},
        )
        session_id = start_response.json()["session_id"]

        choices_response = client.post(
            "/api/game/choices",
            json={"session_id": session_id},
        )
        choice_id = choices_response.json()["choices"][0]["id"]

        # 提交选择
        submit_response = client.post(
            "/api/game/choice/submit",
            json={
                "session_id": session_id,
                "choice_id": choice_id,
            },
        )

        assert submit_response.status_code == 200
        data = submit_response.json()

        # 验证响应结构
        assert data["success"] is True
        assert "player_state" in data
        assert "feedback" in data

        # 验证状态更新
        player_state = data["player_state"]
        assert player_state["turn"] == 1  # 回合应该增加

    def test_submit_choice_invalid_session(self):
        """测试使用无效会话ID提交选择"""
        response = client.post(
            "/api/game/choice/submit",
            json={
                "session_id": "invalid-session-id",
                "choice_id": "some-choice",
            },
        )

        assert response.status_code == 404

    def test_submit_choice_invalid_choice(self):
        """测试使用无效选项ID提交选择"""
        # 先创建会话
        start_response = client.post(
            "/api/game/start",
            json={"player_name": "测试玩家", "difficulty": "normal"},
        )
        session_id = start_response.json()["session_id"]

        # 使用无效的选项ID
        response = client.post(
            "/api/game/choice/submit",
            json={
                "session_id": session_id,
                "choice_id": "invalid-choice-id",
            },
        )

        assert response.status_code == 400

    def test_game_flow(self):
        """测试完整的游戏流程"""
        # 1. 开始游戏
        start_response = client.post(
            "/api/game/start",
            json={"player_name": "测试玩家", "difficulty": "easy"},
        )
        assert start_response.status_code == 201
        session_id = start_response.json()["session_id"]
        initial_energy = start_response.json()["player_state"]["energy"]

        # 2. 获取选项
        choices_response = client.post(
            "/api/game/choices",
            json={"session_id": session_id},
        )
        assert choices_response.status_code == 200
        choice_id = choices_response.json()["choices"][0]["id"]

        # 3. 提交选择
        submit_response = client.post(
            "/api/game/choice/submit",
            json={
                "session_id": session_id,
                "choice_id": choice_id,
            },
        )
        assert submit_response.status_code == 200
        new_energy = submit_response.json()["player_state"]["energy"]

        # 验证精力减少
        assert new_energy < initial_energy
