"""
AI 服务 v2.0 - 混合模式（AI生成 + 素材库降级）

核心策略：
1. 优先使用AI生成内容
2. 验证AI生成内容质量
3. 不合格则使用素材库降级
4. 确保游戏始终有高质量内容

配置：
- model: gpt-4o-mini
- temperature: 0.85（高创意度）
- max_tokens: 16000（大量输出）
"""
import json
import random
import re
from typing import Literal, Optional
from openai import AsyncOpenAI
from loguru import logger

from app.core.config import settings
from app.prompts.fallback_library import (
    get_random_company,
    get_random_npcs,
    get_random_magical_element,
    get_style_by_name,
    FALLBACK_STYLES,
)
from app.services.content_validator import ContentValidator


class AIServiceV2:
    """
    AI服务类（v2 - 混合模式）

    职责：
    - 调用OpenAI API
    - 验证AI生成内容
    - 素材库降级
    - 响应解析
    """

    # 模型配置
    MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.85
    MAX_TOKENS: int = 16000

    def __init__(self):
        """初始化AI服务"""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未配置")

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None
        )

        # 使用配置中的模型（如果有），否则使用默认
        self.model = settings.OPENAI_MODEL if hasattr(settings, 'OPENAI_MODEL') else self.MODEL
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', self.TEMPERATURE)
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', self.MAX_TOKENS)

        # 初始化验证器
        self.validator = ContentValidator()

        logger.info(f"🤖 AI服务初始化 - 模型: {self.model}, 温度: {self.temperature}, 最大输出: {self.max_tokens}")

    async def generate_initial_turn(
        self,
        player_name: str,
        difficulty: str,
        seed: int
    ) -> dict:
        """
        生成初始回合内容（混合策略：AI生成 → 验证 → 降级）

        Args:
            player_name: 玩家名称
            difficulty: 难度
            seed: 随机种子

        Returns:
            AI生成的内容或素材库降级内容
        """
        # 设置随机种子（保证同一会话内输出一致）
        random.seed(seed)

        system_prompt = self._get_system_prompt()
        user_prompt = self._build_initial_prompt(player_name, difficulty, seed)

        # 策略1: 尝试AI生成
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=60.0,  # 增加超时时间
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("AI返回了空响应")

            # 解析JSON响应
            result = self._parse_ai_response(content)

            # 验证AI生成的内容质量
            is_valid, errors = self.validator.validate_initial_response(result)

            if is_valid:
                logger.success(f"✅ AI生成初始内容成功 - Seed: {seed}")
                return result
            else:
                logger.warning(f"⚠️ AI内容质量不合格，使用素材库降级: {errors}")
                return self._generate_fallback_initial(seed, player_name)

        except Exception as e:
            logger.warning(f"⚠️ AI调用失败，使用素材库降级: {e}")
            return self._generate_fallback_initial(seed, player_name)

    async def generate_next_turn(
        self,
        context: list[dict],
        user_action: str,
        seed: int
    ) -> dict:
        """
        生成下一回合内容

        Args:
            context: 对话上下文（messages + summaries）
            user_action: 玩家行动
            seed: 随机种子

        Returns:
            AI生成的内容

        Raises:
            Exception: AI调用失败时抛出异常
        """
        # 设置随机种子
        random.seed(seed)

        system_prompt = self._get_system_prompt()

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(context)
        messages.append({
            "role": "user",
            "content": f"玩家选择了: {user_action}\n请根据这个选择生成后续剧情和新的选项。"
        })

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=30.0,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("AI返回了空响应")

            # 解析JSON响应
            result = self._parse_ai_response(content)

            logger.success(f"✅ AI生成新回合 - Seed: {seed}")

            return result

        except Exception as e:
            logger.error(f"❌ AI调用失败: {e}")
            raise  # 不降级，直接抛出异常

    async def create_summary(self, messages_text: str) -> str:
        """
        生成摘要（用于上下文压缩）

        Args:
            messages_text: 需要摘要的消息文本

        Returns:
            摘要文本

        Raises:
            Exception: AI调用失败时抛出异常
        """
        system_prompt = """你是一个游戏摘要专家。
请将以下游戏对话历史浓缩为一个简洁的摘要，保留：
1. 关键情节
2. 玩家的主要选择
3. 当前状态

摘要应该简洁但信息完整，用于后续AI重建上下文。"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请摘要以下对话：\n\n{messages_text}"},
                ],
                temperature=0.3,  # 摘要使用较低温度
                max_tokens=500,
                timeout=15.0,
            )

            summary = response.choices[0].message.content
            if not summary:
                raise ValueError("AI返回了空摘要")

            logger.info(f"✅ AI生成摘要完成")

            return summary

        except Exception as e:
            logger.error(f"❌ 摘要生成失败: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """
        获取系统提示词

        Returns:
            系统提示词
        """
        from app.prompts.system_prompt import SYSTEM_PROMPT
        return SYSTEM_PROMPT

    def _build_initial_prompt(self, player_name: str, difficulty: str, seed: int) -> str:
        """
        构建初始提示词

        Args:
            player_name: 玩家名称
            difficulty: 难度
            seed: 随机种子

        Returns:
            用户提示词
        """
        return f"""请为《摸鱼大作战》生成初始剧情和选项。

玩家信息：
- 姓名：{player_name}
- 难度：{difficulty}
- 随机种子：{seed}

**重要提示**：
- 使用种子 {seed} 来保证随机性的一致性
- 请根据种子创造一个**独一无二**的公司世界
- 公司类型、NPC、魔幻元素、文案风格，全部由你自由创造
- 让玩家体验一个从未见过的职场世界！

请生成完整的初始游戏内容，严格按照JSON格式返回。"""

    def _parse_ai_response(self, content: str) -> dict:
        """
        解析AI响应（提取JSON）

        Args:
            content: AI返回的原始内容

        Returns:
            解析后的字典

        Raises:
            ValueError: JSON解析失败
        """
        # 提取JSON（可能包含markdown代码块）
        json_str = self._extract_json(content)

        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON解析失败: {e}\n内容: {json_str}")
            raise ValueError(f"AI响应格式错误: {e}")

    def _extract_json(self, content: str) -> str:
        """
        从AI响应中提取JSON字符串

        Args:
            content: AI返回的原始内容

        Returns:
            纯净的JSON字符串
        """
        # 移除markdown代码块标记
        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # 修复AI可能产生的非标准JSON语法
        # 例如: "progress": +30 -> "progress": 30
        content = re.sub(r':\s*\+(\d+)', r': \1', content)
        content = re.sub(r':\s*\-(\d+)', r': -\1', content)

        return content

    def _generate_fallback_initial(self, seed: int, player_name: str) -> dict:
        """
        使用素材库生成初始内容（降级方案）

        Args:
            seed: 随机种子
            player_name: 玩家名称

        Returns:
            素材库生成的游戏初始内容
        """
        logger.info(f"📦 使用素材库生成初始内容 - Seed: {seed}")

        # 获取随机公司、NPC、魔幻元素
        company = get_random_company(seed)
        npcs = get_random_npcs(seed + 1, count=4)
        magical_element = get_random_magical_element(seed + 2, probability=0.5)
        style = get_style_by_name(company.get("style", "down_to_earth"))

        # 构建游戏元数据（magical_level使用数字映射）
        magical_level_map = {0: "none", 1: "light", 2: "medium", 3: "heavy"}
        game_meta = {
            "company_type": company.get("type", "未知"),
            "style_type": style.get("name", "接地气大白话"),
            "magical_level": magical_level_map.get(3 if magical_element else 0, 0),
            "seed_used": seed
        }

        # 构建公司信息（包含style字段）
        company_style = get_style_by_name(company.get("style", "down_to_earth"))
        company_info = {
            "name": company.get("name", "某公司"),
            "type": company.get("type", "unknown"),
            "culture": company.get("culture", "普通公司文化"),
            "atmosphere": company.get("atmosphere", "普通办公氛围"),
            "special_rules": company.get("special_rules", []),
            "magical_elements": company.get("magical_elements", []),
            "style": company_style.get("name", "接地气大白话")
        }

        # 如果有魔幻元素，添加到公司信息
        if magical_element:
            company_info["magical_elements"].append(magical_element.get("name", "未知魔幻元素"))

        # 构建NPC列表（直接使用fallback库返回的完整数据）
        npcs_list = list(npcs)  # fallback_library已经返回完整NPC对象

        # 构建初始玩家状态
        player_state = {
            "energy": 100,
            "chill": 50,
            "progress": 0,
            "suspicion": 0,
            "connection": 0,
            "blackmail": 0,
            "salary": 5000,
            "reputation": 0,
            "day": 1,
            "week": 1,
            "turn": 0
        }

        # 构建欢迎剧情
        story_context = f"""欢迎来到{company_info['name']}！

{company_info['culture']}

今天是你的第一天，你来到了工位。{company_info['atmosphere']}

作为一名新员工，你需要在这里生存下去。在这个充满挑战的职场中，你会遇到各种各样的人和事。

{f"注意：这里似乎有{magical_element.get('name', '一些奇怪')}的东西..." if magical_element else ""}

现在，你准备做什么？"""

        # 构建初始选项
        choices = [
            {
                "id": f"choice_work_{seed}",
                "text": "开始工作，给老板留下好印象",
                "category": "work",
                "effects": {
                    "energy": -10,
                    "chill": 0,
                    "progress": 15,
                    "suspicion": -5,
                    "connection": 5,
                    "blackmail": 0
                },
                "hint": "努力工作，提升进度和好感"
            },
            {
                "id": f"choice_slack_{seed}",
                "text": "先熟悉环境，观察一下同事",
                "category": "slack",
                "effects": {
                    "energy": -5,
                    "chill": 10,
                    "progress": 0,
                    "suspicion": 0,
                    "connection": 10,
                    "blackmail": 0
                },
                "hint": "摸鱼观察，提升人脉"
            },
            {
                "id": f"choice_social_{seed}",
                "text": "主动和同事打招呼，建立关系",
                "category": "social",
                "effects": {
                    "energy": -5,
                    "chill": 5,
                    "progress": 0,
                    "suspicion": 0,
                    "connection": 15,
                    "blackmail": 0
                },
                "hint": "社交互动，快速建立人脉"
            }
        ]

        # 返回完整的初始内容（同时提供 story 和 story_context 字段以兼容）
        return {
            "game_meta": game_meta,
            "company_info": company_info,
            "npcs": npcs_list,
            "player_state": player_state,
            "story": story_context,  # 添加 story 字段兼容 endpoints.py
            "story_context": story_context,
            "choices": choices,
            "active_magical_element": magical_element if magical_element else None
        }
