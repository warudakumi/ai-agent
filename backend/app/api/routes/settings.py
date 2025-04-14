from app.core.settings import get_settings
from app.models.settings import LLMSettings, MSGraphSettings, SettingsResponse

# app/api/routes/settings.py
from fastapi import APIRouter, HTTPException, status
from loguru import logger

router = APIRouter()


@router.get("/llm", response_model=LLMSettings)
async def get_llm_settings():
    """
    LLM設定を取得する

    Returns:
        LLMSettings: LLM設定
    """
    try:
        settings = get_settings()
        llm_settings = settings.get_llm_settings()

        return LLMSettings(
            provider=llm_settings["provider"],
            endpoint=llm_settings["endpoint"],
            api_key=llm_settings["api_key"],
            deployment_name=llm_settings["deployment_name"],
            api_version=llm_settings["api_version"],
            temperature=llm_settings["temperature"],
        )

    except Exception as e:
        logger.error(f"LLM設定取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM設定の取得中にエラーが発生しました: {str(e)}",
        )


@router.post("/llm", response_model=SettingsResponse)
async def save_llm_settings(settings_data: LLMSettings):
    """
    LLM設定を保存する

    Args:
        settings_data: LLM設定データ

    Returns:
        SettingsResponse: 保存結果
    """
    try:
        settings = get_settings()

        # 設定を更新
        settings.update_llm_settings(settings_data.dict())

        # エージェントマネージャを再初期化する必要があることを示すフラグ
        # 実際の環境では何らかの方法でこれを管理する必要がある

        return SettingsResponse(
            success=True, message="LLM設定を保存しました", data=settings_data.dict()
        )

    except Exception as e:
        logger.error(f"LLM設定保存エラー: {str(e)}")
        return SettingsResponse(
            success=False, message=f"LLM設定の保存中にエラーが発生しました: {str(e)}"
        )


@router.get("/msgraph", response_model=MSGraphSettings)
async def get_msgraph_settings():
    """
    Microsoft Graph設定を取得する

    Returns:
        MSGraphSettings: Microsoft Graph設定
    """
    # 注: この実装は仮のものです。本番環境では適切に設定を管理してください。
    return MSGraphSettings(
        client_id="", tenant_id="", client_secret="", redirect_uri=""
    )


@router.post("/msgraph", response_model=SettingsResponse)
async def save_msgraph_settings(settings_data: MSGraphSettings):
    """
    Microsoft Graph設定を保存する

    Args:
        settings_data: Microsoft Graph設定データ

    Returns:
        SettingsResponse: 保存結果
    """
    # 注: この実装は仮のものです。本番環境では適切に設定を管理してください。
    return SettingsResponse(
        success=True,
        message="Microsoft Graph設定を保存しました",
        data=settings_data.dict(),
    )
