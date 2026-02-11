"""
应用配置管理

使用 pydantic-settings 管理环境变量
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    # OpenAI API 配置
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""  # 自定义 API 地址
    OPENAI_MODEL: str = "gemini-2.0-flash-lite"  # 默认模型

    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./game.db"

    # API 配置
    API_KEY: str = "your-secret-api-key-here"
    LOG_LEVEL: str = "INFO"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS 配置
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 忽略额外的环境变量
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """将 CORS 允许的源字符串转换为列表"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# 全局配置实例
settings = Settings()
