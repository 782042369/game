"""
AI 服务 - OpenAI API 集成

负责调用 OpenAI API 生成游戏选项，处理错误和降级方案
"""
import json
import random
from typing import Literal
from openai import AsyncOpenAI
from loguru import logger

from app.api.schemas import AIChoice
from app.core.config import settings
from app.prompts.system_prompt import (
    SYSTEM_PROMPT,
    build_user_prompt,
    FALLBACK_CHOICES,
    get_story_context,
)


class AIService:
    """AI 服务类，封装 OpenAI API 调用"""

    def __init__(self):
        """初始化 AI 服务"""
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "sk-proj-xxxxx":
            logger.warning("⚠️ OPENAI_API_KEY 未配置，将使用预设选项")

        # 使用配置中的 base_url 和 model
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None
        ) if settings.OPENAI_API_KEY else None
        self.model = settings.OPENAI_MODEL  # 使用配置的模型

    async def generate_choices(
        self,
        player_state: dict,
        history: list[dict],
    ) -> tuple[str, list[AIChoice]]:
        """
        生成 AI 游戏选项

        Args:
            player_state: 玩家当前状态
            history: 最近的行动历史

        Returns:
            (剧情上下文, 选项列表)

        Raises:
            Exception: AI 调用失败时抛出异常
        """
        # 如果没有配置 API Key，直接使用预设选项
        if not self.client:
            logger.info("使用预设选项（未配置 OPENAI_API_KEY）")
            return self._get_fallback_response(player_state)

        try:
            # 构建 Prompt
            system_prompt = SYSTEM_PROMPT
            user_prompt = build_user_prompt(player_state, history)

            # 调用 OpenAI API
            logger.info(f"🤖 调用 AI 生成选项 - Day: {player_state.get('day')}, Turn: {player_state.get('turn')}")

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,  # 稍高的温度以增加创造性
                max_tokens=1500,  # 足够生成5个选项
                timeout=10.0,  # 10秒超时
            )

            # 解析响应
            content = response.choices[0].message.content

            if not content:
                raise ValueError("AI 返回了空响应")

            # 提取 JSON（可能包含 markdown 代码块）
            json_str = self._extract_json(content)

            # 解析 JSON
            data = json.loads(json_str)

            # 验证和转换选项
            choices = self._parse_choices(data.get("choices", []))
            story_context = data.get("story_context", get_story_context(player_state))

            logger.success(f"✅ AI 成功生成 {len(choices)} 个选项")

            return story_context, choices

        except Exception as e:
            logger.error(f"❌ AI 调用失败: {e}")
            logger.info("🔄 降级到预设选项")
            return self._get_fallback_response(player_state)

    def _extract_json(self, content: str) -> str:
        """
        从 AI 响应中提取 JSON 字符串

        Args:
            content: AI 返回的原始内容

        Returns:
            纯净的 JSON 字符串
        """
        # 移除可能的 markdown 代码块标记
        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]  # 移除 ```json
        elif content.startswith("```"):
            content = content[3:]  # 移除 ```

        if content.endswith("```"):
            content = content[:-3]  # 移除结尾的 ```

        return content.strip()

    def _parse_choices(self, choices_data: list[dict]) -> list[AIChoice]:
        """
        解析和验证 AI 生成的选项

        Args:
            choices_data: AI 返回的选项数据

        Returns:
            验证后的 AIChoice 对象列表
        """
        choices = []

        for choice_data in choices_data:
            try:
                # 验证必填字段
                if not all(key in choice_data for key in ["id", "text", "category", "effects"]):
                    logger.warning(f"⚠️ 选项缺少必填字段: {choice_data}")
                    continue

                # 验证 category
                valid_categories = ["work", "slack", "skill", "social", "growth"]
                if choice_data["category"] not in valid_categories:
                    logger.warning(f"⚠️ 无效的 category: {choice_data['category']}")
                    continue

                # 验证 effects
                effects = choice_data["effects"]
                if not isinstance(effects, dict):
                    logger.warning(f"⚠️ effects 必须是字典: {effects}")
                    continue

                # 创建 AIChoice 对象
                choice = AIChoice(
                    id=choice_data["id"],
                    text=choice_data["text"],
                    category=choice_data["category"],
                    effects=effects,
                )

                choices.append(choice)

            except Exception as e:
                logger.warning(f"⚠️ 解析选项失败: {e}, 数据: {choice_data}")
                continue

        # 如果解析后的选项不足5个，用预设选项补充
        if len(choices) < 5:
            logger.warning(f"⚠️ AI 生成的选项不足5个，当前: {len(choices)}，补充预设选项")

            existing_ids = {choice.id for choice in choices}
            for fallback_choice in FALLBACK_CHOICES:
                if fallback_choice["id"] not in existing_ids and len(choices) < 5:
                    choices.append(
                        AIChoice(
                            id=fallback_choice["id"],
                            text=fallback_choice["text"],
                            category=fallback_choice["category"],
                            effects=fallback_choice["effects"],
                        )
                    )

        # 如果还是不足5个，直接使用预设选项
        if len(choices) < 5:
            logger.warning("⚠️ 选项解析失败过多，使用全部预设选项")
            return [
                AIChoice(
                    id=c["id"],
                    text=c["text"],
                    category=c["category"],
                    effects=c["effects"],
                )
                for c in FALLBACK_CHOICES[:5]
            ]

        return choices

    def _get_fallback_response(self, player_state: dict) -> tuple[str, list[AIChoice]]:
        """
        获取降级响应（预设选项）

        Args:
            player_state: 玩家当前状态

        Returns:
            (剧情上下文, 预设选项列表)
        """
        story_context = get_story_context(player_state)

        choices = [
            AIChoice(
                id=c["id"],
                text=c["text"],
                category=c["category"],
                effects=c["effects"],
            )
            for c in FALLBACK_CHOICES
        ]

        return story_context, choices
