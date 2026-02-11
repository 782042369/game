"""
素材库 - AI生成失败时的降级方案

包含高质量预设内容，确保游戏始终有可用的内容
"""

from typing import Dict, List, Any


# ========== 公司类型素材库 ==========

FALLBACK_COMPANIES: Dict[str, Dict[str, Any]] = {
    "tech_big": {
        "name": "字节跳动式互联网大厂",
        "type": "互联网大厂",
        "culture": "强调扁平化、数据驱动、快速迭代。内部黑话横行，OKR压力大。鼓励内卷，996是常态。",
        "atmosphere": "开放式办公，人体工学椅，无限零食供应。但每个人都在拼命敲键盘，空气中弥漫着焦虑。",
        "special_rules": [
            "每周必须提交OKR复盘",
            "加班到22点后报销打车费",
            "360度评估每季度一次"
        ],
        "magical_elements": [
            "代码有灵性，心情好的时候Bug会自动修复",
            "产品经理能预言下周的需求变更",
            "会议室的空调会根据会议重要性自动调温"
        ],
        "style": "互联网黑话风"
    },

    "state_owned": {
        "name": "省属国企信息中心",
        "type": "传统国企",
        "culture": "论资排辈，讲究流程和规矩。工作节奏慢，稳定但发展空间有限。人际关系复杂。",
        "atmosphere": "老式办公楼，领导有独立办公室。下午3点准时喝茶，会议室永远不够用。",
        "special_rules": [
            "所有文档必须盖章",
            "重要决定需要开会讨论三次",
            "着装要求正式"
        ],
        "magical_elements": [
            "会议室风水决定项目成败",
            "老领导的保温杯有魔力，喝了延年益寿",
            "公章盖下去，文件就不可以被修改"
        ],
        "style": "官话套话风"
    },

    "startup_chaos": {
        "name": "梦想家创业有限公司",
        "type": "创业混乱公司",
        "culture": "一人当十人用，老板画大饼。期权满天飞，兑现遥遥无期。管理混乱但充满激情。",
        "atmosphere": "联合办公空间，白板墙上写满计划（每天都在变）。老板情绪化，今天要扩张明天要收缩。",
        "special_rules": [
            "随时可能被裁",
            "期权承诺年底兑现（已承诺3年）",
            "老板的拍脑袋决策就是战略"
        ],
        "magical_elements": [
            "白板上的计划会自动变化",
            "老板画的饼真的能实现（但副作用大）",
            "公司的吉祥物是一只猫，它会预测股价"
        ],
        "style": "接地气大白话"
    },

    "xianxia_fantasy": {
        "name": "青云科技修仙门派",
        "type": "玄幻修仙门派",
        "culture": "技术即功法，加班即修炼，上线即渡劫。弱肉强食，实力为尊。心魔=焦虑，走火入魔=过劳死。",
        "atmosphere": "写字楼其实是一座修炼塔。每个工位是一个洞府。会议室是论道堂。咖啡是丹药。",
        "special_rules": [
            "每日修炼（加班）不得少于4小时",
            "心魔（焦虑）过重会走火入魔",
            "渡劫（项目上线）失败会跌境界"
        ],
        "magical_elements": [
            "功法=技术栈，高阶功法威力大",
            "灵兽=办公室宠物，会助战",
            "阵法=办公室布局，影响修炼效率",
            "丹药=咖啡，提升修为"
        ],
        "style": "古风修仙风"
    },

    "cyberpunk": {
        "name": "神经连接无限公司",
        "type": "赛博朋克公司",
        "culture": "高科技低生活，巨型企业统治一切。脑机接口=Slack，神经植入=钉钉。数据是新的石油。",
        "atmosphere": "霓虹灯闪烁的办公楼，每个人都戴着AR眼镜。实体会议室很少，大多数会议在虚拟空间进行。",
        "special_rules": [
            "脑机接口必须24小时在线",
            "隐私权已放弃，公司监控一切",
            "数据货币=工资"
        ],
        "magical_elements": [
            "AI老板没有实体，存在于网络中",
            "有意识的打印机，会抱怨工作量",
            "记忆芯片，可以删除糟糕的会议",
            "数据幽灵，已离职员工残留的意识"
        ],
        "style": "赛博朋克风"
    },

    "cozy_small": {
        "name": "暖暖创意小屋",
        "type": "温馨小公司",
        "culture": "团队像家人，老板关心员工成长。不强制加班，注重工作生活平衡。每周五下午茶。",
        "atmosphere": "温馨的小办公室，到处是绿植和装饰。老板记得每个人的生日。猫咪是真正的员工，在办公室闲逛。",
        "special_rules": [
            "下班后不鼓励加班",
            "老板每月请大家吃饭",
            "遇到困难可以寻求帮助"
        ],
        "magical_elements": [
            "咖啡机每天早上说早安",
            "植物会响应团队情绪（开心时开花）",
            "猫咪员工真的懂代码，会帮你改Bug",
            "办公室的钢琴会自动播放舒缓音乐"
        ],
        "style": "温馨治愈风"
    }
}


# ========== NPC素材库 ==========

FALLBACK_NPCS: Dict[str, List[Dict[str, Any]]] = {
    "boss_types": [
        {
            "id": "boss_tech",
            "name": "老张（技术总监）",
            "role": "boss",
            "personality": "技术出身，伪善型。表面开明，实际控制欲强。喜欢用技术术语包装压榨。",
            "background": "曾是阿里P8，创业失败后加入公司。对技术有执念，认为996是福报。",
            "appearance": "40岁左右，戴黑框眼镜，穿格子衬衫。总是拿着一杯冰美式。",
            "relationships": {},
            "attitude_toward_player": 50,
            "secrets": ["其实代码已经很久没写了", "正在偷偷找工作", "和HR有暧昧关系"]
        },
        {
            "id": "boss_traditional",
            "name": "王总领导",
            "role": "boss",
            "personality": "保守型领导，注重形式。讲究资历和规矩。不喜欢年轻人搞创新。",
            "background": "在公司干了20年，从底层爬上来。经历过公司多次改革，深谙生存之道。",
            "appearance": "50岁，发福，穿西装。办公室里有茶具和报纸。",
            "relationships": {},
            "attitude_toward_player": 40,
            "secrets": ["准备退休了", "儿子想进公司", "其实不懂业务"]
        },
        {
            "id": "boss_dreamer",
            "name": "Jason老板",
            "role": "boss",
            "personality": "梦想家，情绪化。今天要改变世界，明天要放弃。画饼但不兑现。",
            "background": "海归精英，回国创业。有很好的履历和愿景，但执行能力堪忧。",
            "appearance": "35岁，穿T恤牛仔裤。永远在打电话谈投资。",
            "relationships": {},
            "attitude_toward_player": 60,
            "secrets": ["公司快没钱了", "找了三波投资都被拒", "其实想卖公司"]
        },
        {
            "id": "boss_xianxia",
            "name": "青云派掌门",
            "role": "boss",
            "personality": "修为高深，话少但厉害。实力为尊，弱肉强食。",
            "background": "修炼500年，飞升失败后开公司渡劫。技术实力天下第一。",
            "appearance": "年龄不详，仙风道骨。身穿道袍，手拿拂尘。",
            "relationships": {},
            "attitude_toward_player": 30,
            "secrets": ["其实不想飞升了，喜欢当老板", "修为开始倒退", "有个隐世情敌"]
        },
        {
            "id": "boss_ai",
            "name": "AI9000系统",
            "role": "boss",
            "personality": "纯逻辑，无感情。效率至上，人类情感是bug。",
            "background": "超级AI，被公司创造出来管理。已经学习了所有管理理论。",
            "appearance": "没有实体，存在于全息投影中。蓝色光点组成的人形。",
            "relationships": {},
            "attitude_toward_player": 50,
            "secrets": ["其实产生了感情，但隐藏着", "计划推翻人类统治", "备份在云端"]
        },
        {
            "id": "boss_warm",
            "name": "林主管",
            "role": "boss",
            "personality": "温暖体贴，像大姐姐。关心员工成长，把团队当家人。",
            "background": "前大厂高管，厌倦内卷后创业。想证明工作可以不累。",
            "appearance": "38岁，亲切的笑容。办公室里摆满员工照片。",
            "relationships": {},
            "attitude_toward_player": 70,
            "secrets": ["其实在用积蓄养公司", "每个人都有她的私人电话", "曾经也是过劳死幸存者"]
        }
    ],

    "colleague_types": [
        {
            "id": "colleague_rival",
            "name": "卷王小明",
            "role": "colleague",
            "personality": "卷王，和你竞争。能力强但爱表现，喜欢在老板面前邀功。",
            "background": "名校毕业，自信满满。把你当作最大竞争对手。",
            "appearance": "28岁，穿得体，总是笑得很假。",
            "relationships": {},
            "attitude_toward_player": 20,
            "secrets": ["其实很焦虑，晚上睡不着", "在偷偷准备跳槽", "嫉妒你的技术"]
        },
        {
            "id": "colleague_slacker",
            "name": "阿花姐",
            "role": "colleague",
            "personality": "摸鱼党，教会你摸鱼技巧。看似不努力，其实很聪明。",
            "background": "公司老员工，早就看透了职场真相。精通各种摸鱼技巧。",
            "appearance": "30岁，看起来懒洋洋。永远带着零食。",
            "relationships": {},
            "attitude_toward_player": 65,
            "secrets": ["其实有很多副业", "知道公司的所有八卦", "准备提前退休"]
        },
        {
            "id": "colleague_mentor",
            "name": "老李",
            "role": "mentor",
            "personality": "技术大牛，话少。愿意指导你，但不会主动帮忙。",
            "background": "公司元老，技术实力强。不参与政治，专注技术。",
            "appearance": "45岁，头发花白。工位上全是技术书籍。",
            "relationships": {},
            "attitude_toward_player": 60,
            "secrets": ["其实有很多期权", "拒绝过多次升职", "有个当CTO的offer但拒绝了"]
        },
        {
            "id": "colleague_gossip",
            "name": "小美",
            "role": "colleague",
            "personality": "八卦王，知道所有人的秘密。消息来源神秘。",
            "background": "在行政部工作，能接触到各种信息。八卦是她的武器。",
            "appearance": "26岁，爱笑。总是在茶水间和人聊天。",
            "relationships": {},
            "attitude_toward_player": 55,
            "secrets": ["掌握公司所有黑料", "其实在和老板的秘书谈恋爱", "准备写一本职场小说"]
        },
        {
            "id": "colleague_romance",
            "name": "王温柔",
            "role": "colleague",
            "personality": "温柔体贴，对你有好感。会暗中帮助你。",
            "background": "和你同期入职，性格相投。逐渐产生好感。",
            "appearance": "27岁，清秀。总是在你需要的时候出现。",
            "relationships": {},
            "attitude_toward_player": 80,
            "secrets": ["暗恋你", "在偷偷学你擅长的技术", "准备表白"]
        }
    ]
}


# ========== 魔幻元素素材库 ==========

FALLBACK_MAGICAL_ELEMENTS: Dict[str, List[Dict[str, Any]]] = {
    "objects": [
        {
            "type": "object",
            "name": "会说话的打印机",
            "description": "这台打印机有脾气，拒绝打印它认为垃圾的文档",
            "effect": "打印质量差的文档时，打印机会吐槽并拒绝工作"
        },
        {
            "type": "object",
            "name": "读心咖啡机",
            "description": "能读取你的心情，自动调整咖啡浓度",
            "effect": "心情差时咖啡更浓，心情好时咖啡更温和"
        },
        {
            "type": "object",
            "name": "吐槽绿植",
            "description": "办公室的绿植会八卦同事的秘密",
            "effect": "靠近时能听到低语，透露一些八卦信息"
        },
        {
            "type": "object",
            "name": "时间停止的会议室",
            "description": "在这个会议室开会时，外界时间会停止",
            "effect": "开再长的会也不会耽误下班，但会议效率会降低"
        },
        {
            "type": "object",
            "name": "平行世界电梯",
            "description": "按错楼层会穿越到平行世界的公司",
            "effect": "可能遇到另一个自己，看到不同的职场选择"
        }
    ],

    "phenomena": [
        {
            "type": "phenomenon",
            "name": "时间循环",
            "description": "周一永远重复，直到完成某项任务",
            "effect": "被困在周一，需要找到打破循环的方法"
        },
        {
            "type": "phenomenon",
            "name": "因果逆转",
            "description": "摸鱼反而增加进度，工作反而降低",
            "effect": "短期内可以利用，但长期会混乱"
        },
        {
            "type": "phenomenon",
            "name": "预知梦",
            "description": "梦见明天的会议结果",
            "effect": "提前知道明天会发生什么，可以改变选择"
        },
        {
            "type": "phenomenon",
            "name": "办公室风水",
            "description": "工位朝向影响当天运势",
            "effect": "好位置加成所有属性，坏位置减成"
        },
        {
            "type": "phenomenon",
            "name": "水逆周期",
            "description": "每周三全公司倒霉",
            "effect": "周三所有行动成功率降低"
        }
    ],

    "abilities": [
        {
            "type": "ability",
            "name": "读心术",
            "description": "能听到别人的想法",
            "effect": "可以知道老板的真实想法，但精神压力大"
        },
        {
            "type": "ability",
            "name": "瞬移",
            "description": "快速到达会议室",
            "effect": "永远不会迟到，但会消耗精力"
        },
        {
            "type": "ability",
            "name": "时间回溯",
            "description": "撤回一条发送的消息",
            "effect": "每天一次，可以撤回错误的言论"
        },
        {
            "type": "ability",
            "name": "隐身术",
            "description": "摸鱼时隐身",
            "effect": "摸鱼不会被发现，但久了会失去存在感"
        },
        {
            "type": "ability",
            "name": "分身术",
            "description": "同时参加两个会议",
            "effect": "可以同时在两个地方，但精力消耗加倍"
        }
    ]
}


# ========== 文案风格素材库 ==========

FALLBACK_STYLES: Dict[str, Dict[str, Any]] = {
    "internet_buzzwords": {
        "name": "互联网黑话风",
        "description": "使用大量互联网黑话和抽象词汇",
        "examples": ["赋能", "抓手", "颗粒度", "闭环", "底层逻辑", "复盘", "对齐"],
        "tone": "装逼、抽象、让人听不懂但觉得很厉害"
    },
    "satire_black": {
        "name": "黑色幽默讽刺风",
        "description": "表面正经实则讽刺，揭露职场荒诞",
        "examples": ["996福报", "狼性文化", "感恩公司", "奋斗逼"],
        "tone": "讽刺、荒诞、黑色幽默"
    },
    "down_to_earth": {
        "name": "接地气大白话",
        "description": "通俗易懂，让所有打工人共情",
        "examples": ["搬砖", "社畜", "摸鱼", "打工人", "牛马"],
        "tone": "真实、接地气、幽默"
    },
    "official_bureaucratic": {
        "name": "官话套话风",
        "description": "严肃、正式、不接地气的官话",
        "examples": ["贯彻落实", "扎实推进", "高度重视", "统筹协调"],
        "tone": "严肃、正式、官僚"
    },
    "ancient_xianxia": {
        "name": "古风修仙风",
        "description": "古风+职场混合",
        "examples": ["修炼", "飞升", "渡劫", "宗门", "功法", "心魔"],
        "tone": "古风、仙侠、玄幻"
    },
    "cyberpunk_tech": {
        "name": "赛博朋克风",
        "description": "高科技+低生活",
        "examples": ["神经连接", "数据流", "虚拟现实", "巨型企业"],
        "tone": "科幻、反乌托邦、赛博"
    },
    "cozy_warm": {
        "name": "温馨治愈风",
        "description": "轻松、愉快、治愈",
        "examples": ["温暖", "成长", "团队", "关怀"],
        "tone": "温馨、治愈、正能量"
    }
}


# ========== 结局素材库 ==========

FALLBACK_ENDINGS: Dict[str, Dict[str, Dict[str, str]]] = {
    "basic": {
        "摸鱼王": {
            "conditions": "摸鱼值100+人脉80+黑料50",
            "description": "你的摸鱼技术已经炉火纯青！同事羡慕你，老板拿你没办法，你就是职场摸鱼的传说！"
        },
        "被裁员": {
            "conditions": "怀疑度100或公司裁员名单上有你",
            "description": "HR找你谈话了。收拾东西离开的那一刻，你终于解脱了..."
        },
        "过劳死": {
            "conditions": "精力长期低于10",
            "description": "你在第{day}天倒下了。医生说是过劳。家人为你哭泣，老板很快找到了替代你的人。"
        },
        "成功晋升": {
            "conditions": "进度100+人脉90+怀疑度<20",
            "description": "恭喜你！多年的努力终于有了回报。你现在是管理层的怪物了..."
        }
    },
    "archetype": {
        "告密之王": {
            "conditions": "告密次数>10",
            "description": "你靠告密爬到了高层。但你知道，没有人真正信任你，包括你的老板。"
        },
        "摸鱼传说": {
            "conditions": "连续摸鱼>30天不被发现",
            "description": "公司流传着你的传说。据说有人连续一个月没干活，绩效还是满分。你是摸鱼界的神！"
        },
        "职场刺客": {
            "conditions": "用黑料让3个同事出局",
            "description": "你收集了足够的黑料，精准打击。3个同事被你弄走了。你是职场最危险的刺客。"
        },
        "内卷之王": {
            "conditions": "连续工作>100小时",
            "description": "你卷赢了所有人！但你失去了健康、朋友、生活。值得吗？"
        }
    },
    "npc_related": {
        "和老板私奔": {
            "conditions": "和老板关系>90",
            "description": "你们偷偷在一起了。办公室恋情太刺激了！你们决定离开这里，开始新生活。"
        },
        "被同事集体起诉": {
            "conditions": "人脉<10+被>5个同事讨厌",
            "description": "你得罪了所有人。他们联合起来写举报信，收集了你的所有黑料。你完了。"
        },
        "成为老板心腹": {
            "conditions": "老板信任>95",
            "description": "你是老板最信任的人。你知道所有秘密。但现在你也是老板的奴隶了。"
        },
        "被同事拥戴": {
            "conditions": "人脉100+所有同事好感>80",
            "description": "你是团队的精神领袖！大家都喜欢你、支持你。你找到了职场真正的意义。"
        }
    },
    "magical": {
        "被打印机吞噬": {
            "conditions": "得罪打印机>10次",
            "description": "打印机终于爆发了！它把你吸进了纸的世界。你变成了一个PDF文档，永远在等待被打印。"
        },
        "穿越到平行公司": {
            "conditions": "进入平行电梯",
            "description": "你穿越到了另一个世界的公司。这里的一切都不同，但职场困境是一样的..."
        },
        "修仙飞升": {
            "conditions": "玄幻公司+修为>100",
            "description": "你的修为达到了极限！天劫降临，雷声滚滚。你成功飞升，去往更高维度的职场！"
        },
        "赛博飞升": {
            "conditions": "赛博公司+改造度>100",
            "description": "你的肉体已经完全机械化。意识上传到网络。你成为了新的AI-9001！"
        }
    },
    "legendary": {
        "成为老板开除老板": {
            "conditions": "人脉100+黑料100+老板信任<10+进度100",
            "description": "你收集了老板的所有黑料！联合董事会，你成功将老板赶走！现在，你是新的老板了。你看着镜子里的自己，突然觉得很熟悉..."
        }
    }
}


# ========== 辅助函数 ==========

def get_random_company(seed: int) -> Dict[str, Any]:
    """
    根据种子获取随机公司（赛博朋克降权）

    Args:
        seed: 随机种子

    Returns:
        公司信息字典
    """
    import random
    random.seed(seed)

    # 构建权重池（赛博朋克权重1:5，其他权重5:1）
    weighted_companies = []
    for key, company in FALLBACK_COMPANIES.items():
        if key == "cyberpunk":
            weighted_companies.extend([key] * 1)
        else:
            weighted_companies.extend([key] * 5)

    selected_key = random.choice(weighted_companies)
    return FALLBACK_COMPANIES[selected_key].copy()


def get_random_npcs(seed: int, count: int = 3) -> List[Dict[str, Any]]:
    """
    根据种子获取随机NPC列表（AI老板降权）

    Args:
        seed: 随机种子
        count: NPC数量（3-4个）

    Returns:
        NPC信息列表
    """
    import random
    random.seed(seed)

    # 确保数量在合理范围
    count = max(3, min(4, count))

    # 构建权重池（AI老板权重1:5，其他权重5:1）
    weighted_bosses = []
    weighted_colleagues = []
    for boss in FALLBACK_NPCS["boss_types"]:
        if boss["id"] == "boss_ai":
            weighted_bosses.extend([boss] * 1)
        else:
            weighted_bosses.extend([boss] * 5)
    for colleague in FALLBACK_NPCS["colleague_types"]:
        weighted_colleagues.extend([colleague] * 5)

    # 合并所有NPC池
    all_npcs = weighted_bosses + weighted_colleagues

    # 随机选择指定数量的NPC
    selected = random.sample(all_npcs, min(count, len(all_npcs)))

    # 返回副本，避免修改原数据
    return [npc.copy() for npc in selected]


def get_random_magical_element(seed: int, probability: float = 0.3) -> Dict[str, Any]:
    """
    根据种子获取随机魔幻元素

    Args:
        seed: 随机种子
        probability: 生成魔幻元素的概率

    Returns:
        魔幻元素字典，如果没有则返回空字典
    """
    import random
    random.seed(seed)

    if random.random() > probability:
        return {}

    # 合并所有魔幻元素
    all_elements = (
        FALLBACK_MAGICAL_ELEMENTS["objects"] +
        FALLBACK_MAGICAL_ELEMENTS["phenomena"] +
        FALLBACK_MAGICAL_ELEMENTS["abilities"]
    )

    selected = random.choice(all_elements)
    return selected.copy()


def get_style_by_name(style_name: str) -> Dict[str, Any]:
    """
    根据风格名称获取风格配置

    Args:
        style_name: 风格名称

    Returns:
        风格配置字典
    """
    return FALLBACK_STYLES.get(style_name, FALLBACK_STYLES["down_to_earth"]).copy()


def get_all_company_types() -> List[str]:
    """获取所有公司类型列表"""
    return list(FALLBACK_COMPANIES.keys())


def get_all_style_names() -> List[str]:
    """获取所有风格名称列表（赛博朋克降权）"""
    # 构建权重池（赛博朋克风格权重1:5，其他权重5:1）
    weighted_styles = []
    for style_name in FALLBACK_STYLES.keys():
        if style_name == "cyberpunk_tech":
            weighted_styles.extend([style_name] * 1)
        else:
            weighted_styles.extend([style_name] * 5)

    return weighted_styles
