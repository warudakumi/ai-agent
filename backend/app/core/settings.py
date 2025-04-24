from functools import lru_cache
from typing import Any, Dict, List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 環境設定
    env: str = "development"

    # FastAPI設定
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # CORS設定
    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.3:3000",
    ]

    # デフォルトLLM設定
    default_llm_provider: str = "azure"

    # Azure OpenAI設定
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment_name: str = ""
    azure_openai_api_version: str = "2023-05-15"

    # OpenAI設定
    openai_api_key: str = ""
    openai_model_name: str = "gpt-3.5-turbo"

    # 共通LLM設定
    llm_temperature: float = 0.7

    # ファイルアップロード設定
    upload_dir: str = "app/static/uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = [
        "txt",
        "pdf",
        "docx",
        "pptx",
        "xlsx",
        "csv",
        "json",
        "md",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_llm_settings(self) -> Dict[str, Any]:
        """LLM設定を取得する"""
        if self.default_llm_provider == "azure":
            return {
                "provider": "azure",
                "endpoint": self.azure_openai_endpoint,
                "api_key": self.azure_openai_api_key,
                "deployment_name": self.azure_openai_deployment_name,
                "api_version": self.azure_openai_api_version,
                "temperature": self.llm_temperature,
            }
        elif self.default_llm_provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model_name": self.openai_model_name,
                "temperature": self.llm_temperature,
            }
        else:
            # ローカルLLM
            return {
                "provider": "local",
                "endpoint": "http://localhost:8000",
                "temperature": self.llm_temperature,
            }

    def update_llm_settings(self, settings: Dict[str, Any]) -> None:
        """LLM設定を更新する"""
        if settings.get("provider"):
            self.default_llm_provider = settings["provider"]

        # Azure OpenAI設定
        if self.default_llm_provider == "azure":
            if settings.get("endpoint"):
                self.azure_openai_endpoint = settings["endpoint"]
            if settings.get("api_key"):
                self.azure_openai_api_key = settings["api_key"]
            if settings.get("deployment_name"):
                self.azure_openai_deployment_name = settings["deployment_name"]
            if settings.get("api_version"):
                self.azure_openai_api_version = settings["api_version"]

        # OpenAI設定
        elif self.default_llm_provider == "openai":
            if settings.get("api_key"):
                self.openai_api_key = settings["api_key"]
            if settings.get("model_name"):
                self.openai_model_name = settings["model_name"]

        # 共通設定
        if settings.get("temperature") is not None:
            self.llm_temperature = float(settings["temperature"])


@lru_cache()
def get_settings() -> Settings:
    """設定インスタンスを取得する（キャッシュ付き）"""
    return Settings()
