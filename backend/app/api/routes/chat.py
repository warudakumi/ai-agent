from typing import List, Optional

from app.agent.core import AgentManager
from app.api.dependencies import get_llm_config
from app.models.chat import ChatResponse, FileUploadResponse
from app.services.file_service import save_uploaded_file
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from loguru import logger

router = APIRouter()

# AgentManagerインスタンスを保持
agent_manager: Optional[AgentManager] = None


@router.post("/message", response_model=ChatResponse)
async def process_message(
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    session_id: Optional[str] = Form(None),
):
    """
    チャットメッセージを処理する

    Args:
        message: ユーザーメッセージ
        files: 添付ファイルリスト（オプション）
        session_id: セッションID（オプション）

    Returns:
        ChatResponse: 処理結果
    """
    global agent_manager

    try:
        # AgentManagerの初期化（初回実行時）
        if agent_manager is None:
            llm_config = await get_llm_config()
            agent_manager = AgentManager(llm_config)
            logger.info("AgentManagerを初期化しました")

        # ファイル処理
        file_paths = []
        if files:
            for file in files:
                file_path = await save_uploaded_file(file)
                file_paths.append(file_path)
                logger.info(f"ファイルを保存しました: {file_path}")

        # メッセージ処理
        response = await agent_manager.process_message(message, session_id, file_paths)

        return ChatResponse(
            message=response["message"],
            session_id=response["session_id"],
            thought_process=response.get("thought_process"),
            tool_calls=response.get("tool_calls"),
        )

    except Exception as e:
        logger.error(f"メッセージ処理エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"メッセージ処理中にエラーが発生しました: {str(e)}",
        )


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    ファイルをアップロードする

    Args:
        file: アップロードファイル

    Returns:
        FileUploadResponse: アップロード結果
    """
    try:
        # ファイル保存
        file_path = await save_uploaded_file(file)

        # ファイル情報の作成
        from app.services.file_service import get_file_info

        file_info = await get_file_info(file_path)

        return FileUploadResponse(success=True, file_info=file_info)

    except HTTPException as he:
        return FileUploadResponse(success=False, error=he.detail)

    except Exception as e:
        logger.error(f"ファイルアップロードエラー: {str(e)}")
        return FileUploadResponse(
            success=False,
            error=f"ファイルアップロード中にエラーが発生しました: {str(e)}",
        )
