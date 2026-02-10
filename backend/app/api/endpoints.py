"""
API 路由端点

实现核心游戏 API：开始游戏、获取选项、提交选择

Phase 3 更新：使用数据库存储替代临时内存存储
"""
import uuid
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
    PlayerState,
    AIChoice,
)
from app.core.game_engine import GameEngine
from app.core.constants import INITIAL_PLAYER_STATE
from app.services.ai_service import AIService
from app.services.session_service import SessionService

# 创建路由器
router = APIRouter()

# 初始化 AI 服务
ai_service = AIService()

# 当前可用的选项缓存（仅用于提交时验证，不需要持久化）
current_choices: dict[str, list[AIChoice]] = {}


# ========== 依赖注入 ==========


async def get_session_service() -> SessionService:
    """
    获取 SessionService 实例

    Returns:
        SessionService 实例
    """
    return SessionService()


# ========== API 端点 ==========


@router.post(
    "/start",
    response_model=GameStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="开始新游戏",
    description="创建新的游戏会话并返回初始玩家状态",
)
async def start_game(
    request: GameStartRequest,
    session_service: SessionService = Depends(get_session_service),
) -> GameStartResponse:
    """
    开始新游戏（使用数据库存储）

    Args:
        request: 游戏开始请求（包含玩家昵称和难度）
        session_service: 会话管理服务

    Returns:
        游戏开始响应（包含会话ID和初始状态）

    Raises:
        HTTPException 500: 服务器内部错误
    """
    try:
        # 创建初始玩家状态
        initial_state = PlayerState(**INITIAL_PLAYER_STATE)

        # 使用 SessionService 创建会话
        session_id = await session_service.create_session(
            player_name=request.player_name,
            difficulty=request.difficulty,
            initial_state=initial_state,
        )

        logger.info(f"✅ 新游戏已创建 - Session ID: {session_id}, 玩家: {request.player_name}")

        return GameStartResponse(
            session_id=session_id,
            player_state=initial_state,
            message=f"欢迎，{request.player_name}！你的职场摸鱼之旅开始了！在30天内平衡工作与摸鱼，祝你好运！",
        )

    except Exception as e:
        logger.error(f"❌ 开始游戏失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建游戏失败: {str(e)}",
        )


@router.post(
    "/choices",
    response_model=ChoicesResponse,
    summary="获取 AI 生成的选项",
    description="获取当前回合的5个 AI 生成的游戏选项",
)
async def get_choices(
    request: ChoicesRequest,
    session_service: SessionService = Depends(get_session_service),
) -> ChoicesResponse:
    """
    获取 AI 生成的游戏选项（使用数据库存储）

    Args:
        request: 获取选项请求（包含会话ID）
        session_service: 会话管理服务

    Returns:
        包含5个AI生成选项的响应

    Raises:
        HTTPException 404: 会话不存在
        HTTPException 500: 服务器内部错误
    """
    try:
        # 从数据库获取玩家状态
        current_state = await session_service.get_player_state(request.session_id)

        if current_state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {request.session_id} 不存在",
            )

        # 获取历史记录（用于 AI 上下文）
        history = await session_service.get_recent_history(request.session_id, limit=10)

        # 调用 AI 服务生成选项
        story_context, choices = await ai_service.generate_choices(
            player_state=current_state.model_dump(),
            history=history,
        )

        # 缓存当前选项（用于提交时验证）
        current_choices[request.session_id] = choices

        logger.info(f"🎮 生成选项 - Session: {request.session_id}, Day: {current_state.day}")

        return ChoicesResponse(
            story_context=story_context,
            choices=choices,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取选项失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取选项失败: {str(e)}",
        )


@router.post(
    "/choice/submit",
    response_model=ChoiceSubmitResponse,
    summary="提交玩家选择",
    description="处理玩家的选项选择并返回新的游戏状态",
)
async def submit_choice(
    request: ChoiceSubmitRequest,
    session_service: SessionService = Depends(get_session_service),
) -> ChoiceSubmitResponse:
    """
    提交玩家选择（使用数据库存储）

    Args:
        request: 提交选择请求（包含会话ID和选项ID）
        session_service: 会话管理服务

    Returns:
        包含新游戏状态、反馈和触发事件的响应

    Raises:
        HTTPException 404: 会话不存在
        HTTPException 400: 选项ID无效
        HTTPException 500: 服务器内部错误
    """
    try:
        # 从数据库获取会话信息和玩家状态
        session_info = await session_service.get_session_info(request.session_id)
        current_state = await session_service.get_player_state(request.session_id)

        if session_info is None or current_state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"会话 {request.session_id} 不存在",
            )

        # 检查游戏是否已结束
        if session_info.get("is_game_over", False):
            return ChoiceSubmitResponse(
                success=False,
                player_state=current_state,
                feedback=_get_action_feedback("游戏已结束"),
                triggered_events=[],
                game_over=True,
                game_over_reason="游戏已结束",
            )

        # 查找选项（从缓存的当前选项中查找）
        available_choices = current_choices.get(request.session_id, [])
        selected_choice = None

        for choice in available_choices:
            if choice.id == request.choice_id:
                selected_choice = choice
                break

        if selected_choice is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的选项ID: {request.choice_id}，请先获取选项",
            )

        # 计算新状态
        engine = GameEngine()
        new_state, feedback, triggered_events = engine.calculate_new_state(
            current_state, selected_choice
        )

        # 检查游戏结束
        difficulty = session_info.get("difficulty", "normal")
        is_game_over, game_over_reason = engine.check_game_over(new_state, difficulty)

        if is_game_over:
            # 标记游戏结束
            await session_service.mark_game_over(
                session_id=request.session_id,
                reason=game_over_reason,
            )
            logger.info(f"🏁 游戏结束 - Session: {request.session_id}, 原因: {game_over_reason}")

        # 保存新的玩家状态到数据库
        await session_service.save_player_state(
            session_id=request.session_id,
            state=new_state,
        )

        # 记录历史（用于 AI 上下文）
        await session_service.add_action_history(
            session_id=request.session_id,
            choice_id=selected_choice.id,
            choice_text=selected_choice.text,
            effects=selected_choice.effects,
            player_state_snapshot=new_state.model_dump(),
        )

        logger.info(
            f"✅ 选择提交成功 - Session: {request.session_id}, "
            f"Day: {new_state.day}, Turn: {new_state.turn}"
        )

        return ChoiceSubmitResponse(
            success=True,
            player_state=new_state,
            feedback=feedback,
            triggered_events=triggered_events,
            game_over=is_game_over,
            game_over_reason=game_over_reason if is_game_over else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 提交选择失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交选择失败: {str(e)}",
        )


# ========== 辅助函数 ==========


def _get_action_feedback(message: str):
    """生成简单的行动反馈"""
    from app.api.schemas import ActionFeedback

    return ActionFeedback(
        success=message,
        flavor=["行动已执行"],
    )
