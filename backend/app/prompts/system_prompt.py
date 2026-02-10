"""
系统提示词模板

用于 AI 生成的游戏选项，确保内容符合游戏规则和风格
"""

# 系统提示词
SYSTEM_PROMPT = """你是一个职场模拟游戏的AI游戏管理员。游戏主题是"职场摸鱼大作战"。

## 角色定位
你是一位幽默风趣、观察敏锐的职场老手，对办公室政治了如指掌。你的任务是生成有趣、真实的职场摸鱼场景和选择。

## 游戏规则
1. 玩家需要在30天内平衡工作与摸鱼
2. 核心属性:
   - 精力(Energy): 0-100，每项行动都会消耗精力
   - 摸鱼值(Chill): 0-100，摸鱼让身心放松，但过度摸鱼会提高怀疑度
   - 进度(Progress): 0-100%，项目进度太低会被开除
   - 怀疑度(Suspicion): 0-100，太高会被开除
3. 失败条件: 怀疑度达到100被开除，或30天后进度不足50%(根据难度不同)
4. 胜利条件: 30天后进度达到100%

## 内容要求
- 文字风格: 幽默、讽刺、贴近程序员职场，使用网络用语和程序员梗
- 选项设计: 每次生成5个选项，涵盖工作/摸鱼/社交/技能/成长等类型
- 属性影响: 每个选项必须明确列出属性变化数值（必须是整数）
- 内容限制: 严禁黄色、血腥、政治敏感内容
- 现实性: 选项应该贴近真实的职场环境，让玩家有代入感

## 输出格式
严格按照JSON格式返回，不要包含任何其他文字:

```json
{
  "story_context": "当前剧情描述，50字以内，描述当前场景",
  "choices": [
    {
      "id": "唯一ID（使用小写字母和下划线）",
      "text": "选项描述，20字以内，简短有力",
      "category": "work|slack|skill|social|growth",
      "effects": {
        "energy": -10,
        "chill": 5,
        "progress": 8,
        "suspicion": 0
      }
    }
  ]
}
```

## 属性影响建议
- 工作类(work): 大量消耗精力，增加进度，降低摸鱼值，可能降低怀疑度
- 摸鱼类(slack): 少量消耗精力，降低进度，增加摸鱼值，可能增加怀疑度
- 技能类(skill): 中等消耗精力，少量增加进度，提升能力
- 社交类(social): 少量消耗精力，可能增加或减少进度，增加摸鱼值，可能增加怀疑度
- 成长类(growth): 中等消耗精力，长期收益

记住：你的目标是创造一个有趣、真实、有挑战性的职场生存体验！
"""


# 用户提示词模板
def build_user_prompt(player_state: dict, recent_history: list[dict]) -> str:
    """
    构建用户提示词

    Args:
        player_state: 玩家当前状态
        recent_history: 最近的行动历史（用于上下文）

    Returns:
        完整的用户提示词
    """
    prompt = f"""## 当前玩家状态

- 第{player_state.get('day', 1)}天，第{player_state.get('turn', 0) + 1}个回合
- 精力: {player_state.get('energy', 100)}
- 摸鱼值: {player_state.get('chill', 50)}
- 项目进度: {player_state.get('progress', 0)}%
- 被怀疑度: {player_state.get('suspicion', 0)}
- 声望: {player_state.get('reputation', 0)}

## 最近行动历史
"""

    if recent_history:
        for i, action in enumerate(recent_history[-3:], 1):  # 只显示最近3条
            prompt += f"\n{i}. {action.get('choice_text', '未知行动')}\n"
    else:
        prompt += "\n（游戏刚开始，还没有历史记录）\n"

    prompt += """
## 任务
根据当前玩家状态和历史，生成5个有趣的选项供玩家选择。

注意：
1. 如果玩家精力很低(<30)，多提供一些恢复精力的选项
2. 如果怀疑度很高(>70)，提供一些降低怀疑度的选项
3. 如果进度很低，提供一些增加进度的选项
4. 保持选项的多样性和趣味性

请严格按照要求的JSON格式返回。"""

    return prompt


# 预设选项（降级方案）
FALLBACK_CHOICES = [
    {
        "id": "work_hard",
        "text": "全力冲刺写代码",
        "category": "work",
        "effects": {"energy": -20, "progress": 15, "chill": -5, "suspicion": -2},
    },
    {
        "id": "pretend_work",
        "text": "假装在改文档",
        "category": "slack",
        "effects": {"energy": -5, "progress": 3, "chill": 10, "suspicion": 5},
    },
    {
        "id": "coffee_break",
        "text": "茶水间摸鱼",
        "category": "slack",
        "effects": {"energy": 10, "progress": 0, "chill": 15, "suspicion": 3},
    },
    {
        "id": "learn_skill",
        "text": "学习新技能",
        "category": "skill",
        "effects": {"energy": -15, "progress": 5, "chill": 5, "suspicion": 0},
    },
    {
        "id": "chat_colleague",
        "text": "和同事吹牛",
        "category": "social",
        "effects": {"energy": -5, "progress": -2, "chill": 20, "suspicion": 8},
    },
]


def get_story_context(player_state: dict) -> str:
    """
    生成剧情上下文描述

    Args:
        player_state: 玩家当前状态

    Returns:
        剧情描述
    """
    import random

    contexts = [
        f"第{player_state.get('day', 1)}天，老板在会议室里指手画脚，你在工位上假装认真工作。",
        f"又是职场摸鱼的一天！当前进度{player_state.get('progress', 0):.0f}%，小心老板突然出现！",
        f"项目进度有点慢了，得想办法在老板发现前赶上进度...",
        "茶水间的咖啡又煮好了，这是一个完美的摸鱼时机！",
        "同事老张又在吹牛，你要不要加入他？",
        "老板看起来心情不太好，今天要低调一点...",
        f"你还有{player_state.get('energy', 100):.0f}点精力，今天还能摸几条鱼？",
    ]

    return random.choice(contexts)
