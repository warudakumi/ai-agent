from typing import Any, Dict

from app.core.settings import get_settings
from fastapi import HTTPException, status


async def get_llm_config() -> Dict[str, Any]:
    """LLM設定を取得する"""
    settings = get_settings()
    llm_config = settings.get_llm_settings()

    # Azure設定の場合は必須パラメータを確認
    if llm_config["provider"] == "azure":
        if (
            not llm_config["endpoint"]
            or not llm_config["api_key"]
            or not llm_config["deployment_name"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Azure OpenAI設定が不完全です。endpoint, api_key, deployment_nameは必須です。",
            )

    return llm_config
