"""
API 路由端点（v2 - AI驱动架构）

完全重构为AI代理模式：
- 后端只负责AI调用和会话管理
- 所有游戏逻辑由AI处理
- 前端纯展示层
"""
import uuid
import time
from functools import wraps
from typing import Literal
from fastapi import APIRouter, HTTPException, status, Depends
from loguru import logger

from app.api.schemas import (
    GameStartRequest,
    GameStartResponse,
    ChoicesRequest,
    ChoicesResponse,
    ChoiceSubmitRequest,
    ChoiceSubmitResponse,
    ErrorResponse,
    CompanyProfile,
    ActionFeedback,
    filter_player_state_for_frontend,
)
from app.services.session_service import SessionService
from app.services.context_service import ContextService
from app.services.ai_service_v2 import AIServiceV2
from app.repositories.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession


# API性能监控装饰器
def log_api_time(func_name: str):
    """装饰器：记录API端点执行时间"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(f"⏱️ API[{func_name}] 耗时: {elapsed:.3f}秒")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"❌ API[{func_name}] 失败 (耗时{elapsed:.3f}秒): {e}")
                raise
        return wrapper
    return decorator

# 创建路由器
router = APIRouter()


# ========== 依赖注入 ==========


async def get_session_service(
    db: AsyncSession = Depends(get_db_session)
) -> SessionService:
    """获取 SessionService 实例"""
    return SessionService(db)


async def get_context_service(
    db: AsyncSession = Depends(get_db_session),
    ai_service: AIServiceV2 = Depends()
) -> ContextService:
    """获取 ContextService 实例"""
    return ContextService(db, ai_service)


async def get_ai_service() -> AIServiceV2:
    """获取 AIServiceV2 实例"""
    return AIServiceV2()


# ========== API 端点 ==========


@router.post(
    "/start",
    response_model=GameStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="开始新游戏",
    description="创建新的游戏会话并返回AI生成的初始内容",
)
@log_api_time("开始游戏")
async def start_game(
    request: GameStartRequest,
    session_service: SessionService = Depends(get_session_service),
    ai_service: AIServiceV2 = Depends(get_ai_service),
) -> GameStartResponse:
    """
    开始新游戏（AI驱动模式）

    流程：
    1. 创建新会话（生成seed）
    2. 调用AI生成初始剧情和选项
    3. 返回AI生成的内容

    Args:
        request: 游戏开始请求
        session_service: 会话服务
        ai_service: AI服务

    Returns:
        游戏开始响应（包含AI生成的初始内容）

    Raises:
        HTTPException 500: 服务器内部错误
    """
    try:
        # 1. 创建会话
        session_info = await session_service.create_game(
            player_name=request.player_name,
            difficulty=request.difficulty
        )

        session_id = session_info["session_id"]
        seed = session_info["seed"]

        # 2. 调用AI生成初始内容
        logger.info(f"🤖 调用AI生成初始内容 - Session: {session_id}")

        ai_response = await ai_service.generate_initial_turn(
            player_name=request.player_name,
            difficulty=request.difficulty,
            seed=seed
        )

        # 3. 记录初始消息（安全获取story，降级到story_context）
        context_service = ContextService(
            session_service.db,
            ai_service
        )
        story_content = ai_response.get("story") or ai_response.get("story_context", "")
        await context_service.add_message(
            session_id=session_id,
            role="assistant",
            content=story_content
        )

        logger.success(f"✅ 新游戏已创建 - Session: {session_id}")

        # 解析游戏元数据
        game_meta = None
        if ai_response.get("game_meta"):
            from app.api.schemas import GameMeta
            game_meta = GameMeta(**ai_response["game_meta"])

        # 解析公司完整档案（包含 special_rules 和 magical_elements）
        company_profile = None
        if ai_response.get("company_info"):
            company_data = ai_response["company_info"]
            logger.debug(f"🔍 公司数据调试: {company_data}")
            # 确保 magical_elements 是列表
            if "magical_elements" in company_data and isinstance(company_data["magical_elements"], dict):
                logger.warning(f"⚠️ magical_elements 是字典，转换为列表: {company_data['magical_elements']}")
                company_data["magical_elements"] = list(company_data["magical_elements"].values())
            company_profile = CompanyProfile(**company_data)

        # 解析NPC完整档案列表
        npcs = []
        if ai_response.get("npcs"):
            from app.api.schemas import NPCProfile
            for npc_data in ai_response["npcs"]:
                npcs.append(NPCProfile(**npc_data))

        # 解析魔幻元素
        current_magical_element = None
        if ai_response.get("current_magical_element"):
            from app.api.schemas import MagicalElement
            current_magical_element = MagicalElement(**ai_response["current_magical_element"])

        # 过滤玩家状态，移除隐藏字段（suspicion和progress）
        filtered_player_state = filter_player_state_for_frontend(
            ai_response.get("player_state", {})
        )

        return GameStartResponse(
            session_id=session_id,
            player_state=filtered_player_state,
            message=ai_response.get("story_context", ai_response.get("story", "欢迎来到摸鱼大作战！")),
            choices=ai_response.get("choices", []),
            game_meta=game_meta,
            company_profile=company_profile,
            npcs=npcs,
            current_magical_element=current_magical_element
        )

    except Exception as e:
        logger.error(f"❌ 开始游戏失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建游戏失败: {str(e)}",
        )


@router.post(
    "/act",
    response_model=ChoiceSubmitResponse,
    summary="提交行动",
    description="处理玩家的行动选择并返回AI生成的新内容",
)
@log_api_time("提交行动")
async def submit_action(
    request: ChoiceSubmitRequest,
    session_service: SessionService = Depends(get_session_service),
    context_service: ContextService = Depends(get_context_service),
    ai_service: AIServiceV2 = Depends(get_ai_service),
) -> ChoiceSubmitResponse:
    """
    提交行动（AI驱动模式）

    流程：
    1. 获取会话上下文（messages + summaries）
    2. 调用AI处理玩家行动
    3. AI生成新剧情、选项和状态更新
    4. 保存消息和关键事件
    5. 返回AI生成的内容

    Args:
        request: 行动提交请求
        session_service: 会话服务
        context_service: 上下文服务
        ai_service: AI服务

    Returns:
        包含AI生成新内容的响应

    Raises:
        HTTPException 404: 会话不存在
        HTTPException 500: 服务器内部错误
    """
    try:
        # 1. 验证会话
        session = await session_service.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {request.session_id} 不存在",
            )

        if session["status"] != "active":
            return ChoiceSubmitResponse(
                success=False,
                player_state={},
                feedback=ActionFeedback(
                    success="游戏已结束",
                    flavor=[]
                ),
                triggered_events=[],
                game_over=True,
                game_over_reason="游戏已结束",
                npc_reaction=None,
                current_magical_element=None
            )

        # 2. 记录玩家行动
        await context_service.add_message(
            session_id=request.session_id,
            role="user",
            content=request.choice_id  # 或完整的行动描述
        )

        # 3. 获取上下文
        context = await context_service.get_context_for_ai(request.session_id)

        # 4. 调用AI生成新内容
        logger.info(f"🤖 调用AI处理行动 - Session: {request.session_id}, Choice: {request.choice_id}")

        ai_response = await ai_service.generate_next_turn(
            context=context,
            user_action=request.choice_id,
            seed=session["seed"]
        )

        # 5. 记录AI响应（安全获取story，降级到story_context）
        story_content = ai_response.get("story") or ai_response.get("story_context", "")
        await context_service.add_message(
            session_id=request.session_id,
            role="assistant",
            content=story_content
        )

        # 6. 记录关键事件
        await session_service.record_key_event(
            session_id=request.session_id,
            event_type="action_choice",
            event_data={
                "choice_id": request.choice_id,
                "state_snapshot": ai_response.get("player_state", {}),
                "ai_response": ai_response
            }
        )

        # 7. 检查游戏结束
        is_game_over = ai_response.get("is_game_over", False)
        if is_game_over:
            await session_service.end_session(
                session_id=request.session_id,
                reason=ai_response.get("game_over_reason", "游戏结束"),
                is_victory=ai_response.get("is_victory", False)
            )

        logger.success(f"✅ 行动处理完成 - Session: {request.session_id}")

        # 解析更新后的NPC完整档案列表
        updated_npcs = []
        if ai_response.get("updated_npcs"):
            from app.api.schemas import NPCProfile
            for npc_data in ai_response["updated_npcs"]:
                updated_npcs.append(NPCProfile(**npc_data))

        # 解析NPC反应
        npc_reaction = None
        if ai_response.get("npc_reactions"):
            from app.api.schemas import NPCReaction
            reactions_data = ai_response["npc_reactions"]
            npc_reaction = NPCReaction(
                boss=reactions_data.get("boss"),
                colleagues=reactions_data.get("colleagues"),
                specific_npcs=reactions_data.get("specific_npcs", {})
            )

        # 解析魔幻元素
        # 解析魔幻元素
        current_magical_element = None
        element_data = ai_response.get("active_magical_element") or ai_response.get("current_magical_element")
        if element_data:
            from app.api.schemas import MagicalElement
            current_magical_element = MagicalElement(**element_data)

        # 过滤玩家状态，移除隐藏字段（suspicion和progress）
        filtered_player_state = filter_player_state_for_frontend(
            ai_response.get("player_state", {})
        )

        return ChoiceSubmitResponse(
            success=True,
            player_state=filtered_player_state,
            feedback=ActionFeedback(
                success=ai_response.get("story_context", ai_response.get("story", "行动完成")),
                flavor=ai_response.get("flavor_texts", [])
            ),
            triggered_events=ai_response.get("triggered_events", []),
            game_over=is_game_over,
            game_over_reason=ai_response.get("game_over_reason") if is_game_over else None,
            updated_npcs=updated_npcs,
            npc_reaction=npc_reaction,
            current_magical_element=current_magical_element
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 提交行动失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交行动失败: {str(e)}",
        )


@router.get(
    "/state",
    summary="获取当前状态",
    description="获取会话的当前状态和最近消息",
)
@log_api_time("获取状态")
async def get_state(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
    context_service: ContextService = Depends(get_context_service),
):
    """
    获取当前状态

    Args:
        session_id: 会话ID
        session_service: 会话服务
        context_service: 上下文服务

    Returns:
        会话状态和最近消息

    Raises:
        HTTPException 404: 会话不存在
    """
    try:
        # 获取会话信息
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {session_id} 不存在",
            )

        # 获取最近消息
        messages = await context_service.get_messages(session_id, limit=10)

        # 获取token统计
        token_stats = await context_service.get_token_stats(session_id)

        return {
            "session": session,
            "recent_messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ],
            "token_stats": token_stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取状态失败: {str(e)}",
        )


@router.post(
    "/resume",
    summary="恢复会话",
    description="从保存的消息和摘要恢复会话上下文",
)
async def resume_session(
    request: ChoiceSubmitRequest,  # 复用请求结构
    context_service: ContextService = Depends(get_context_service),
):
    """
    恢复会话

    Args:
        request: 包含session_id的请求
        context_service: 上下文服务

    Returns:
        重建的上下文

    Raises:
        HTTPException 404: 会话不存在
    """
    try:
        # 重建上下文
        context = await context_service.rebuild_context(request.session_id)

        logger.info(f"✅ 会话恢复完成 - Session: {request.session_id}")

        return {
            "session_id": request.session_id,
            "context": context,
            "message_count": len(context)
        }

    except Exception as e:
        logger.error(f"❌ 恢复会话失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复会话失败: {str(e)}",
        )
