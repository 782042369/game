"""
日志配置 - Loguru轮转配置

支持：
- 按大小轮转（10MB）
- 按时间轮转（每天）
- 保留期限（30天）
- 日志压缩（zip）
- 分级别存储
"""
from loguru import logger
import sys
from pathlib import Path

# 移除默认的handler
logger.remove()

# 确保日志目录存在
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# ============================================================================
# 通用日志配置
# ============================================================================

logger.add(
    log_dir / "app_{time:YYYY-MM-DD}.log",
    rotation="10 MB",                      # 单文件最大10MB
    retention="30 days",                   # 保留30天
    level="INFO",
    encoding="utf-8",
    enqueue=True,                          # 异步写入，避免阻塞
    backtrace=True,                        # 完整回溯
    diagnose=True,                         # 诊断信息
    compression="zip",                     # 压缩旧日志
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    ),
)

# ============================================================================
# 错误日志（单独存储）
# ============================================================================

logger.add(
    log_dir / "error_{time:YYYY-MM-DD}.log",
    rotation="10 MB",
    retention="30 days",
    level="ERROR",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    compression="zip",
    format=(
        "<red>{time:YYYY-MM-DD HH:mm:ss}</red> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<red>{message}</red>\n"
        "{exception}"
    ),
)

# ============================================================================
# 控制台输出（开发环境）
# ============================================================================

logger.add(
    sys.stderr,
    level="INFO",
    format=(
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    ),
)

# ============================================================================
# 导出logger实例
# ============================================================================

__all__ = ["logger"]
