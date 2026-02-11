"""
内容质量验证器

检查AI生成的内容是否满足最低质量要求
"""
from typing import Dict, List, Optional, Tuple
from loguru import logger


class ContentValidator:
    """内容验证器"""

    # 最小要求配置
    MIN_NPCS: int = 3
    MAX_NPCS: int = 10
    MIN_CHOICES: int = 3
    MAX_CHOICES: int = 6

    # 禁止词汇列表（政治相关）
    FORBIDDEN_WORDS: List[str] = [
        "政治", "政府", "政党", "选举", "主席", "总统",
        "政治局", "常委", "人大", "政协", "中纪委"
    ]

    # 最小长度要求（根据用户要求，已禁用字数验证）
    MIN_COMPANY_NAME_LENGTH: int = 1  # 不再强制公司名长度
    MIN_STORY_CONTEXT_LENGTH: int = 1  # 不再强制剧情长度

    @staticmethod
    def validate_initial_response(ai_response: Dict) -> Tuple[bool, List[str]]:
        """
        验证初始响应的质量

        Args:
            ai_response: AI生成的响应字典

        Returns:
            (is_valid, error_messages) - 是否有效和错误消息列表
        """
        errors: List[str] = []

        # 1. 检查必要字段
        required_fields = [
            "game_meta", "company_info", "npcs",
            "player_state", "story_context", "choices"
        ]
        for field in required_fields:
            if field not in ai_response:
                errors.append(f"缺少必要字段: {field}")

        # 2. 检查游戏元数据（只验证必要字段存在，不验证具体值）
        if "game_meta" in ai_response:
            game_meta = ai_response["game_meta"]
            if not isinstance(game_meta, dict):
                errors.append("game_meta 必须是字典类型")

        # 3. 检查公司信息完整性
        if "company_info" in ai_response:
            company = ai_response["company_info"]
            if not isinstance(company, dict):
                errors.append("company_info 必须是字典类型")
            else:
                required_company_fields = ["name", "type", "culture", "atmosphere"]
                for field in required_company_fields:
                    if field not in company or not company[field]:
                        errors.append(f"公司信息不完整: {field}")

        # 4. 检查NPC数量和质量
        if "npcs" in ai_response:
            npcs = ai_response["npcs"]
            if not isinstance(npcs, list):
                errors.append("npcs 必须是列表类型")
            else:
                npc_count = len(npcs)

                if npc_count < ContentValidator.MIN_NPCS:
                    errors.append(
                        f"NPC数量过少: {npc_count}，要求至少{ContentValidator.MIN_NPCS}个"
                    )

                if npc_count > ContentValidator.MAX_NPCS:
                    errors.append(
                        f"NPC数量过多: {npc_count}，要求最多{ContentValidator.MAX_NPCS}个"
                    )

                # 检查每个NPC的完整性
                for i, npc in enumerate(npcs):
                    if not isinstance(npc, dict):
                        errors.append(f"NPC #{i+1} 必须是字典类型")
                        continue

                    required_npc_fields = ["id", "name", "role", "personality"]
                    for field in required_npc_fields:
                        if field not in npc or not npc[field]:
                            errors.append(f"NPC #{i+1} 缺少字段: {field}")
        else:
            errors.append("缺少 npcs 字段")

        # 5. 检查选项数量
        if "choices" in ai_response:
            choices = ai_response["choices"]
            if not isinstance(choices, list):
                errors.append("choices 必须是列表类型")
            else:
                choice_count = len(choices)

                if choice_count < ContentValidator.MIN_CHOICES:
                    errors.append(
                        f"选项数量过少: {choice_count}，要求至少{ContentValidator.MIN_CHOICES}个"
                    )

                if choice_count > ContentValidator.MAX_CHOICES:
                    errors.append(
                        f"选项数量过多: {choice_count}，要求最多{ContentValidator.MAX_CHOICES}个"
                    )

                # 检查每个选项的完整性
                for i, choice in enumerate(choices):
                    if not isinstance(choice, dict):
                        errors.append(f"选项 #{i+1} 必须是字典类型")
                        continue

                    required_choice_fields = ["id", "text", "effects"]
                    for field in required_choice_fields:
                        if field not in choice:
                            errors.append(f"选项 #{i+1} 缺少字段: {field}")
        else:
            errors.append("缺少 choices 字段")

        # 6. 检查玩家状态
        if "player_state" in ai_response:
            player_state = ai_response["player_state"]
            if not isinstance(player_state, dict):
                errors.append("player_state 必须是字典类型")
            else:
                required_stats = [
                    "energy", "chill", "progress", "suspicion",
                    "connection", "blackmail"
                ]
                for stat in required_stats:
                    if stat not in player_state:
                        errors.append(f"玩家状态缺少: {stat}")
        else:
            errors.append("缺少 player_state 字段")

        # 7. 内容质量检查（启发式）
        content_errors = ContentValidator._check_content_quality(ai_response)
        errors.extend(content_errors)

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(f"⚠️ AI内容验证失败: {errors}")

        return is_valid, errors

    @staticmethod
    def _check_content_quality(ai_response: Dict) -> List[str]:
        """
        检查内容质量（启发式规则）

        Args:
            ai_response: AI生成的响应字典

        Returns:
            错误列表
        """
        errors: List[str] = []

        # 检查公司名称（仅验证禁止词汇，不验证长度）
        if "company_info" in ai_response:
            company_info = ai_response["company_info"]
            if isinstance(company_info, dict):
                company_name = company_info.get("name", "")

                # 检查是否使用了禁止的政治词汇
                for word in ContentValidator.FORBIDDEN_WORDS:
                    if word in company_name:
                        errors.append(f"公司名称包含禁止词汇: {word}")

        # 检查剧情描述（仅验证不为空，不验证长度）
        if "story_context" in ai_response:
            story = ai_response.get("story_context", "")
            if isinstance(story, str) and len(story.strip()) == 0:
                errors.append("剧情描述不能为空")

        # 检查NPC名称是否重复
        if "npcs" in ai_response:
            npcs = ai_response["npcs"]
            if isinstance(npcs, list):
                npc_names: List[str] = []
                for npc in npcs:
                    if isinstance(npc, dict) and "name" in npc:
                        npc_names.append(npc["name"])

                # 检查重复
                unique_names = set(npc_names)
                if len(unique_names) != len(npc_names):
                    errors.append("NPC名称重复")

        # 检查选项文本是否为空
        if "choices" in ai_response:
            choices = ai_response["choices"]
            if isinstance(choices, list):
                for i, choice in enumerate(choices):
                    if isinstance(choice, dict):
                        choice_text = choice.get("text", "")
                        if not choice_text or len(choice_text.strip()) == 0:
                            errors.append(f"选项 #{i+1} 文本为空")

                        # 检查选项文本是否包含禁止词汇
                        if isinstance(choice_text, str):
                            for word in ContentValidator.FORBIDDEN_WORDS:
                                if word in choice_text:
                                    errors.append(f"选项 #{i+1} 包含禁止词汇: {word}")

        return errors

    @staticmethod
    def validate_turn_response(ai_response: Dict) -> Tuple[bool, List[str]]:
        """
        验证回合响应的质量

        Args:
            ai_response: AI生成的响应字典

        Returns:
            (is_valid, error_messages) - 是否有效和错误消息列表
        """
        errors: List[str] = []

        # 检查必要字段
        required_fields = ["story_context", "player_state", "choices"]
        for field in required_fields:
            if field not in ai_response:
                errors.append(f"缺少必要字段: {field}")

        # 检查选项数量
        if "choices" in ai_response:
            choices = ai_response["choices"]
            if not isinstance(choices, list):
                errors.append("choices 必须是列表类型")
            else:
                choice_count = len(choices)

                if choice_count < ContentValidator.MIN_CHOICES:
                    errors.append(
                        f"选项数量过少: {choice_count}，"
                        f"要求至少{ContentValidator.MIN_CHOICES}个"
                    )

                if choice_count > ContentValidator.MAX_CHOICES:
                    errors.append(
                        f"选项数量过多: {choice_count}，"
                        f"要求最多{ContentValidator.MAX_CHOICES}个"
                    )

                # 检查每个选项的完整性
                for i, choice in enumerate(choices):
                    if not isinstance(choice, dict):
                        errors.append(f"选项 #{i+1} 必须是字典类型")
                        continue

                    required_choice_fields = ["id", "text", "effects"]
                    for field in required_choice_fields:
                        if field not in choice:
                            errors.append(f"选项 #{i+1} 缺少字段: {field}")
        else:
            errors.append("缺少 choices 字段")

        # 检查玩家状态
        if "player_state" in ai_response:
            player_state = ai_response["player_state"]
            if not isinstance(player_state, dict):
                errors.append("player_state 必须是字典类型")
            else:
                required_stats = [
                    "energy", "chill", "progress", "suspicion",
                    "connection", "blackmail"
                ]
                for stat in required_stats:
                    if stat not in player_state:
                        errors.append(f"玩家状态缺少: {stat}")
        else:
            errors.append("缺少 player_state 字段")

        # 检查剧情描述（仅验证不为空，不验证长度）
        if "story_context" in ai_response:
            story = ai_response.get("story_context", "")
            if isinstance(story, str) and len(story.strip()) == 0:
                errors.append("剧情描述不能为空")

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(f"⚠️ AI回合内容验证失败: {errors}")

        return is_valid, errors


# 便捷函数

def validate_ai_response(
    ai_response: Dict,
    is_initial: bool = True
) -> Tuple[bool, List[str]]:
    """
    验证AI响应的便捷函数

    Args:
        ai_response: AI生成的响应字典
        is_initial: 是否为初始响应（True）或回合响应（False）

    Returns:
        (is_valid, error_messages) - 是否有效和错误消息列表
    """
    validator = ContentValidator()

    if is_initial:
        return validator.validate_initial_response(ai_response)
    else:
        return validator.validate_turn_response(ai_response)
