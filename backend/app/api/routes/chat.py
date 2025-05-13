import json
from typing import List, Optional

from app.agent.core import AgentManager
from app.api.dependencies import get_llm_config
from app.models.chat import ChatResponse, FileUploadResponse
from app.services.file_service import save_uploaded_file
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from loguru import logger

router = APIRouter()

# AgentManagerインスタンスを保持
agent_manager: Optional[AgentManager] = None


@router.post("/message", response_model=ChatResponse)
async def process_message(
    message: str = Form(...),
    files: Optional[List[UploadFile]] = File(None),
    session_id: Optional[str] = Form(None),
    request: Request = None,
):
    """
    チャットメッセージを処理する

    Args:
        message: ユーザーメッセージ
        files: 添付ファイルリスト（オプション）
        session_id: セッションID（オプション）
        request: リクエスト情報

    Returns:
        ChatResponse: 処理結果
    """
    global agent_manager

    try:
        # リクエスト情報をログに記録
        client_ip = request.client.host if request and request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        logger.info(
            f"メッセージ処理開始 - IP: {client_ip}, セッションID: {session_id}, UA: {user_agent}"
        )
        logger.debug(
            f"受信メッセージ: {message[:100]}..."
            if len(message) > 100
            else f"受信メッセージ: {message}"
        )

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

        # 結果をログに記録
        logger.info(f"メッセージ処理完了 - セッションID: {response['session_id']}")
        logger.debug(f"思考プロセス: {response.get('thought_process', '')[:200]}...")

        # ツール呼び出しがある場合はログに記録
        if response.get("tool_calls"):
            logger.debug(
                f"ツール呼び出し: {json.dumps(response.get('tool_calls', [])[:3], ensure_ascii=False)}"
            )

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
