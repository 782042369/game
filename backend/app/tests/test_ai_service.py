"""
AI 服务单元测试

测试 AI 服务的核心功能，包括 API 调用、Prompt 构建、错误处理等
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.ai_service import AIService
from app.api.schemas import AIChoice


class TestAIService:
    """AI 服务测试类"""

    def test_init_without_api_key(self):
        """测试未配置 API Key 时的初始化"""
        with patch("app.services.ai_service.settings.OPENAI_API_KEY", ""):
            service = AIService()
            assert service.client is None

    def test_init_with_api_key(self):
        """测试配置 API Key 时的初始化"""
        with patch("app.services.ai_service.settings.OPENAI_API_KEY", "sk-test-key"):
            service = AIService()
            assert service.client is not None

    @pytest.mark.asyncio
    async def test_generate_choices_without_api_key(self):
        """测试未配置 API Key 时生成选项（使用降级方案）"""
        with patch("app.services.ai_service.settings.OPENAI_API_KEY", ""):
            service = AIService()

            player_state = {
                "day": 1,
                "turn": 0,
                "energy": 100,
                "chill": 50,
                "progress": 0,
                "suspicion": 0,
            }

            story_context, choices = await service.generate_choices(
                player_state=player_state,
                history=[],
            )

            # 验证返回值
            assert isinstance(story_context, str)
            assert len(story_context) > 0
            assert len(choices) == 5

            # 验证选项类型
            for choice in choices:
                assert isinstance(choice, AIChoice)
                assert choice.id in [
                    "work_hard",
                    "pretend_work",
                    "coffee_break",
                    "learn_skill",
                    "chat_colleague",
                ]

    @pytest.mark.asyncio
    async def test_generate_choices_with_api_key_success(self):
        """测试配置 API Key 时成功生成选项"""
        # Mock OpenAI API 响应
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '''```json
{
  "story_context": "第1天，老板心情不太好",
  "choices": [
    {
      "id": "work_hard",
      "text": "全力冲刺写代码",
      "category": "work",
      "effects": {"energy": -20, "progress": 15, "chill": -5, "suspicion": -2}
    },
    {
      "id": "slack_off",
      "text": "茶水间摸鱼",
      "category": "slack",
      "effects": {"energy": 10, "progress": 0, "chill": 15, "suspicion": 3}
    }
  ]
}
```'''

        with patch("app.services.ai_service.settings.OPENAI_API_KEY", "sk-test-key"):
            with patch.object(AIService, "__init__", lambda self: None):
                service = AIService()
                service.client = AsyncMock()
                service.client.chat.completions.create = AsyncMock(return_value=mock_response)
                service.model = "gpt-4o-mini"

                player_state = {
                    "day": 1,
                    "turn": 0,
                    "energy": 100,
                    "chill": 50,
                    "progress": 0,
                    "suspicion": 0,
                }

                story_context, choices = await service.generate_choices(
                    player_state=player_state,
                    history=[],
                )

                # 验证返回值
                assert story_context == "第1天，老板心情不太好"
                assert len(choices) >= 2  # AI 生成的选项 + 补充的预设选项

                # 验证 API 被调用
                service.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_choices_api_error_fallback(self):
        """测试 API 调用失败时降级到预设选项"""
        with patch("app.services.ai_service.settings.OPENAI_API_KEY", "sk-test-key"):
            with patch.object(AIService, "__init__", lambda self: None):
                service = AIService()
                service.client = AsyncMock()
                service.client.chat.completions.create = AsyncMock(side_effect=Exception("API Error"))
                service.model = "gpt-4o-mini"

                player_state = {
                    "day": 1,
                    "turn": 0,
                    "energy": 100,
                    "chill": 50,
                    "progress": 0,
                    "suspicion": 0,
                }

                story_context, choices = await service.generate_choices(
                    player_state=player_state,
                    history=[],
                )

                # 验证降级到预设选项
                assert len(choices) == 5
                assert isinstance(story_context, str)

    def test_extract_json_from_markdown(self):
        """测试从 Markdown 代码块中提取 JSON"""
        service = AIService()

        # 测试带 ```json 标记的情况
        content = '''```json
{
  "test": "value"
}
```'''
        json_str = service._extract_json(content)
        assert json_str == '{\n  "test": "value"\n}'

        # 测试带 ``` 标记的情况
        content2 = '''```
{
  "test": "value"
}
```'''
        json_str2 = service._extract_json(content2)
        assert json_str2 == '{\n  "test": "value"\n}'

        # 测试纯 JSON
        content3 = '{"test": "value"}'
        json_str3 = service._extract_json(content3)
        assert json_str3 == '{"test": "value"}'

    def test_parse_choices_valid_data(self):
        """测试解析有效的选项数据"""
        with patch.object(AIService, "__init__", lambda self: None):
            service = AIService()

            choices_data = [
                {
                    "id": "test_choice",
                    "text": "测试选项",
                    "category": "work",
                    "effects": {"energy": -10, "progress": 10},
                },
            ]

            choices = service._parse_choices(choices_data)

            assert len(choices) == 1
            assert choices[0].id == "test_choice"
            assert choices[0].text == "测试选项"
            assert choices[0].category == "work"
            assert choices[0].effects == {"energy": -10, "progress": 10}

    def test_parse_choices_invalid_data(self):
        """测试解析无效的选项数据（应跳过）"""
        with patch.object(AIService, "__init__", lambda self: None):
            service = AIService()

            # 包含无效选项的数据
            choices_data = [
                {
                    "id": "valid_choice",
                    "text": "有效选项",
                    "category": "work",
                    "effects": {"energy": -10},
                },
                {
                    "id": "invalid_choice",
                    "text": "无效选项（缺少 effects）",
                    "category": "work",
                    # 缺少 effects
                },
            ]

            choices = service._parse_choices(choices_data)

            # 应该只解析出1个有效选项，然后补充预设选项到5个
            assert len(choices) == 5
            assert choices[0].id == "valid_choice"

    def test_parse_choices_invalid_category(self):
        """测试解析包含无效 category 的选项"""
        with patch.object(AIService, "__init__", lambda self: None):
            service = AIService()

            choices_data = [
                {
                    "id": "test_choice",
                    "text": "测试选项",
                    "category": "invalid_category",  # 无效的 category
                    "effects": {"energy": -10},
                },
            ]

            choices = service._parse_choices(choices_data)

            # 应该跳过无效选项，使用预设选项
            assert len(choices) == 5
            assert all(choice.category in ["work", "slack", "skill", "social", "growth"] for choice in choices)

    def test_get_fallback_response(self):
        """测试获取降级响应"""
        with patch.object(AIService, "__init__", lambda self: None):
            service = AIService()

            player_state = {
                "day": 5,
                "turn": 3,
                "energy": 50,
                "chill": 30,
                "progress": 25,
                "suspicion": 40,
            }

            story_context, choices = service._get_fallback_response(player_state)

            # 验证返回值
            assert isinstance(story_context, str)
            assert len(story_context) > 0
            assert len(choices) == 5

            # 验证预设选项
            choice_ids = [choice.id for choice in choices]
            assert "work_hard" in choice_ids
            assert "pretend_work" in choice_ids
            assert "coffee_break" in choice_ids
            assert "learn_skill" in choice_ids
            assert "chat_colleague" in choice_ids

    def test_build_user_prompt(self):
        """测试构建用户 Prompt"""
        from app.prompts.system_prompt import build_user_prompt

        player_state = {
            "day": 3,
            "turn": 2,
            "energy": 70,
            "chill": 40,
            "progress": 20,
            "suspicion": 15,
            "reputation": 10,
        }

        history = [
            {"choice_text": "全力冲刺写代码", "effects": {"energy": -20, "progress": 15}},
            {"choice_text": "茶水间摸鱼", "effects": {"energy": 10, "chill": 15}},
        ]

        prompt = build_user_prompt(player_state, history)

        # 验证 Prompt 包含关键信息
        assert "第3天" in prompt
        assert "70" in prompt  # 精力值
        assert "40" in prompt  # 摸鱼值
        assert "20" in prompt  # 进度
        assert "15" in prompt  # 怀疑度
        assert "全力冲刺写代码" in prompt
        assert "茶水间摸鱼" in prompt

    def test_get_story_context(self):
        """测试生成剧情上下文"""
        from app.prompts.system_prompt import get_story_context

        player_state = {
            "day": 10,
            "energy": 30,
            "progress": 45,
        }

        context = get_story_context(player_state)

        # 验证返回值是字符串且不为空
        assert isinstance(context, str)
        assert len(context) > 0

        # 验证包含玩家状态信息
        assert "10" in context or "45" in context or "30" in context
