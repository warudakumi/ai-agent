import json

from app.core.session_manager import get_session_manager
from app.core.settings import get_settings
from app.models.settings import LLMSettings, MSGraphSettings, SettingsResponse

# app/api/routes/settings.py
from fastapi import APIRouter, Form, HTTPException, status
from loguru import logger

router = APIRouter()


@router.get("/llm", response_model=LLMSettings)
async def get_llm_settings():
    """
    デフォルトLLM設定を取得する

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
    デフォルトLLM設定を保存する（全体設定）

    Args:
        settings_data: LLM設定データ

    Returns:
        SettingsResponse: 保存結果
    """
    try:
        settings = get_settings()

        # 設定を更新
        settings.update_llm_settings(settings_data.dict())

        logger.info("デフォルトLLM設定を更新しました")

        return SettingsResponse(
            success=True,
            message="デフォルトLLM設定を保存しました",
            data=settings_data.dict(),
        )

    except Exception as e:
        logger.error(f"LLM設定保存エラー: {str(e)}")
        return SettingsResponse(
            success=False, message=f"LLM設定の保存中にエラーが発生しました: {str(e)}"
        )


@router.post("/llm/session")
async def save_session_llm_settings(
    session_id: str = Form(...),
    settings_data: str = Form(...),  # JSON文字列として受信
):
    """
    セッション別のLLM設定を保存する

    Args:
        session_id: セッションID
        settings_data: LLM設定データ（JSON文字列）

    Returns:
        保存結果
    """
    try:
        # JSON文字列をパース
        config_dict = json.loads(settings_data)

        # セッション管理システムを使用
        session_manager = get_session_manager()

        # デフォルト設定を取得
        from app.api.dependencies import get_llm_config

        default_config = await get_llm_config()

        # セッション別のAgentManagerを取得または作成
        agent_manager = session_manager.get_or_create_agent_manager(
            session_id, default_config
        )

        # セッション別のLLM設定を更新
        success = session_manager.update_session_llm_config(session_id, config_dict)

        if success:
            logger.info(f"セッション {session_id} のLLM設定を保存しました")
            return {
                "success": True,
                "message": f"セッション {session_id} のLLM設定を保存しました",
                "data": config_dict,
            }
        else:
            logger.warning(f"セッション {session_id} のLLM設定保存に失敗しました")
            return {
                "success": False,
                "message": f"セッション {session_id} のLLM設定保存に失敗しました",
            }

    except json.JSONDecodeError as e:
        logger.error(f"LLM設定のJSONパースエラー: {str(e)}")
        return {
            "success": False,
            "message": f"LLM設定のJSON形式が正しくありません: {str(e)}",
        }
    except Exception as e:
        logger.error(f"セッション別LLM設定保存エラー: {str(e)}")
        return {
            "success": False,
            "message": f"セッション別LLM設定の保存中にエラーが発生しました: {str(e)}",
        }


@router.get("/llm/session/{session_id}")
async def get_session_llm_settings(session_id: str):
    """
    セッション別のLLM設定を取得する

    Args:
        session_id: セッションID

    Returns:
        セッション別のLLM設定
    """
    try:
        session_manager = get_session_manager()

        # セッション別の設定を取得
        config = session_manager.get_session_llm_config(session_id)

        if config:
            return {"success": True, "session_id": session_id, "config": config}
        else:
            # セッションが存在しない場合はデフォルト設定を返す
            from app.api.dependencies import get_llm_config

            default_config = await get_llm_config()
            return {
                "success": True,
                "session_id": session_id,
                "config": default_config,
                "is_default": True,
            }

    except Exception as e:
        logger.error(f"セッション別LLM設定取得エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"セッション別LLM設定の取得中にエラーが発生しました: {str(e)}",
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
