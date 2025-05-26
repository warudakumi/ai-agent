from typing import Any, Dict

from app.core.settings import get_settings
from fastapi import HTTPException, status


async def get_llm_config() -> Dict[str, Any]:
    """LLM設定を取得する"""
    settings = get_settings()
    llm_config = settings.get_llm_settings()

    # 設定を検証
    await validate_llm_config(llm_config)
    return llm_config


async def validate_llm_config(llm_config: Dict[str, Any]) -> None:
    """LLM設定を検証する"""
    provider = llm_config.get("provider", "")

    if provider == "azure":
        # Azure設定の場合は必須パラメータを確認
        if (
            not llm_config.get("endpoint")
            or not llm_config.get("api_key")
            or not llm_config.get("deployment_name")
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Azure OpenAI設定が不完全です。endpoint, api_key, deployment_nameは必須です。",
            )
    elif provider == "openai":
        # OpenAI設定の場合は必須パラメータを確認
        if not llm_config.get("api_key"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI設定が不完全です。api_keyは必須です。",
            )
        if not llm_config.get("model_name"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI設定が不完全です。model_nameは必須です。",
            )
    elif provider == "local":
        # ローカルLLM設定の場合は必須パラメータを確認
        if not llm_config.get("endpoint"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ローカルLLM設定が不完全です。endpointは必須です。",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"サポートされていないLLMプロバイダーです: {provider}",
        )
