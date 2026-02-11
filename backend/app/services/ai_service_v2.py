"""
AI 服务 v2.1 - 性能优化版

核心策略：
1. 优先使用AI生成内容
2. 验证AI生成内容质量
3. 不合格则使用素材库降级
4. 确保游戏始终有高质量内容

性能优化：
- 降低max_tokens（初始2048，回合1024）
- 降低temperature（0.7）提升速度
- 缓存机制（相同请求直接返回）
- 缩短timeout（20秒）

配置：
- model: gemini-2.0-flash-lite
- temperature: 0.7（平衡创意和速度）
- max_tokens: 2048（初始）/ 1024（回合）
"""
import json
import random
import re
import time
from functools import wraps
from typing import Literal, Optional
from openai import AsyncOpenAI
from loguru import logger
from hashlib import md5

from app.core.config import settings
from app.prompts.fallback_library import (
    get_random_company,
    get_random_npcs,
    get_random_magical_element,
    get_style_by_name,
    FALLBACK_STYLES,
)
from app.prompts.system_prompt import build_user_prompt
from app.services.content_validator import ContentValidator


# 简单的内存缓存（生产环境建议用Redis）
_cache: dict[str, dict] = {}
_CACHE_MAX_SIZE = 100
_CACHE_TTL = 3600  # 1小时缓存


# 性能监控装饰器
def log_execution_time(func_name: str):
    """装饰器：记录函数执行时间"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"⏱️ {func_name} 耗时: {elapsed:.3f}秒")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ {func_name} 失败 (耗时{elapsed:.3f}秒): {e}")
                raise
        return wrapper
    return decorator


class AIServiceV2:
    """
    AI服务类（v2 - 混合模式）

    职责：
    - 调用OpenAI API
    - 验证AI生成内容
    - 素材库降级
    - 响应解析
    """

    # 模型配置（性能优化版）
    MODEL: str = "gemini-2.0-flash-lite"
    TEMPERATURE: float = 0.7  # 降低温度提升速度（0.7足够创意）
    MAX_TOKENS_INITIAL: int = 2048  # 初始生成用2048够用（原来8192太SB了）
    MAX_TOKENS_TURN: int = 1024  # 后续回合用1024够用

    # 单例实例（性能优化：避免重复创建client）
    _instance: Optional['AIServiceV2'] = None
    _client: Optional[AsyncOpenAI] = None

    def __new__(cls):
        """单例模式：全局只创建一个AIService实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("🤖 AI服务单例创建")
        return cls._instance

    def __init__(self):
        """初始化AI服务（单例模式，只会初始化一次）"""
        # 避免重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未配置")

        # 全局共享的client实例（性能优化）
        if AIServiceV2._client is None:
            AIServiceV2._client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL if settings.OPENAI_BASE_URL else None
            )

        self.client = AIServiceV2._client

        # 使用配置中的模型（如果有），否则使用默认
        self.model = getattr(settings, 'OPENAI_MODEL', self.MODEL)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', self.TEMPERATURE)

        # 初始化验证器
        self.validator = ContentValidator()

        self._initialized = True
        logger.info(f"🚀 AI服务初始化 - 模型: {self.model}, 温度: {self.temperature}")

    @staticmethod
    def _make_cache_key(*args) -> str:
        """生成缓存键"""
        key_str = "|".join(str(arg) for arg in args)
        return md5(key_str.encode()).hexdigest()

    @staticmethod
    def _get_cache(key: str) -> Optional[dict]:
        """获取缓存"""
        return _cache.get(key)

    @staticmethod
    def _set_cache(key: str, value: dict) -> None:
        """设置缓存（LRU策略）"""
        global _cache
        # 超过最大缓存数，删除最早的
        if len(_cache) >= _CACHE_MAX_SIZE:
            oldest_key = next(iter(_cache))
            del _cache[oldest_key]
        _cache[key] = value

    @log_execution_time("AI生成初始回合")
    async def generate_initial_turn(
        self,
        player_name: str,
        difficulty: str,
        seed: int
    ) -> dict:
        """
        生成初始回合内容（混合策略：AI生成 → 验证 → 降级）

        性能优化：
        1. 缓存相同请求
        2. 降低max_tokens（2048）
        3. 降低temperature（0.7）
        4. 缩短timeout（20秒）

        Args:
            player_name: 玩家名称
            difficulty: 难度
            seed: 随机种子

        Returns:
            AI生成的内容或素材库降级内容
        """
        # 检查缓存（性能优化）
        cache_key = self._make_cache_key("initial", player_name, difficulty, seed)
        cached_result = self._get_cache(cache_key)
        if cached_result:
            logger.info(f"💾 命中缓存 - Seed: {seed}")
            return cached_result

        # 设置随机种子（保证同一会话内输出一致）
        random.seed(seed)
        system_prompt = self._get_system_prompt()
        user_prompt = build_user_prompt(
            player_name=player_name,
            difficulty=difficulty,
            seed=seed,
            is_initial=True
        )

        # 策略1: 尝试AI生成（优化参数）
        try:
            api_start = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.MAX_TOKENS_INITIAL,  # 使用优化后的2048
                timeout=20.0,  # 缩短超时时间（原来60秒太SB）
            )
            api_time = time.time() - api_start
            logger.info(f"⚡ API调用耗时: {api_time:.3f}秒")

            content = response.choices[0].message.content
            if not content:
                raise ValueError("AI返回了空响应")

            # 解析JSON响应
            parse_start = time.time()
            result = self._parse_ai_response(content)
            parse_time = time.time() - parse_start
            logger.info(f"🔍 JSON解析耗时: {parse_time:.3f}秒")

            # 验证AI生成的内容质量
            validate_start = time.time()
            is_valid, errors = self.validator.validate_initial_response(result)
            validate_time = time.time() - validate_start
            logger.info(f"✅ 内容验证耗时: {validate_time:.3f}秒")

            if is_valid:
                logger.success(f"✅ AI生成初始内容成功 - Seed: {seed}")
                # 缓存结果
                self._set_cache(cache_key, result)
                return result
            else:
                logger.warning(f"⚠️ AI内容质量不合格，使用素材库降级: {errors}")
                return self._generate_fallback_initial(seed, player_name)

        except Exception as e:
            logger.warning(f"⚠️ AI调用失败，使用素材库降级: {e}")
            return self._generate_fallback_initial(seed, player_name)

    @log_execution_time("AI生成下一回合")
    async def generate_next_turn(
        self,
        context: list[dict],
        user_action: str,
        seed: int
    ) -> dict:
        """
        生成下一回合内容（性能优化版）

        性能优化：
        1. 降低max_tokens（1024）
        2. 缩短timeout（20秒）

        Args:
            context: 对话上下文（messages + summaries）
            user_action: 玩家行动
            seed: 随机种子

        Returns:
            AI生成的内容
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
            api_start = time.time()
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.MAX_TOKENS_TURN,  # 使用优化后的1024
                timeout=20.0,  # 缩短超时时间
            )
            api_time = time.time() - api_start
            logger.info(f"⚡ API调用耗时: {api_time:.3f}秒")

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

    @log_execution_time("AI生成摘要")
    async def create_summary(self, messages_text: str) -> str:
        """
        生成摘要（用于上下文压缩）

        Args:
            messages_text: 需要摘要的消息文本

        Returns:
            摘要文本
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
        # 例如1: "progress": +30 -> "progress": 30
        # 例如2: choice_id: "slack_off" -> choice_id: "slack_off"
        # 修复裸字符串（没有引号的字符串）
        content = re.sub(r'^\s*([^:]+)\s*:\s*"?([^"]+)"?$', r'\1: "\2"', content, flags=re.MULTILINE)
        # 修复数字前的加号（如: "progress": +30）
        content = re.sub(r':\s*\+(\d+)', r': \1', content)
        # 修复数字前的减号（如: "progress": -30）
        content = re.sub(r':\s*\-(\d+)', r': -\1', content)
        # 修复多余的引号和冒号组合（如: "progress": "value"）
        content = re.sub(r'"\s*:', '":', content)
        # 额外清理：移除可能的markdown残留
        content = re.sub(r'```\w*', '', content)

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

        # 构建NPC列表（直接使用fallback_library返回的完整NPC对象）
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
{company_info['atmosphere']}
今天是你的第一天，你来到了工位。作为一名新员工，你需要在这里生存下去。在这个充满挑战的职场中，你会遇到各种各样的人和事。
{f"注意：这里似乎有{magical_element.get('name', '一些奇怪')}的东西..." if magical_element else ""}
现在，你准备做什么？"""

        # 构建初始选项（必须包含choice_id）
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

        # 返回完整的初始内容
        return {
            "game_meta": game_meta,
            "company_info": company_info,
            "npcs": npcs_list,
            "player_state": player_state,
            "story": story_context,
            "story_context": story_context,  # 添加 story 字段兼容 endpoints.py
            "choices": choices,
            "active_magical_element": magical_element if magical_element else None
        }
