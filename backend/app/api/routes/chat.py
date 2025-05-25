import json
import random
import uuid
from typing import List, Optional

from app.api.dependencies import get_llm_config
from app.core.error_handler import ErrorSanitizer
from app.core.session_manager import get_session_manager
from app.models.chat import ChatResponse, FileUploadResponse
from app.services.file_service import save_uploaded_file
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status
from loguru import logger

router = APIRouter()


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

        # LLM設定を取得
        llm_config = await get_llm_config()

        # セッションIDが提供されていない場合は一時的なIDを生成
        if not session_id:
            session_id = str(uuid.uuid4())

        # セッション管理システムを使用してAgentManagerを取得
        session_manager = get_session_manager()
        agent_manager = session_manager.get_or_create_agent_manager(
            session_id, llm_config
        )

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

        # 定期的なクリーンアップ（10%の確率で実行）
        if random.random() < 0.1:
            removed_count = session_manager.cleanup_old_sessions()
            if removed_count > 0:
                logger.info(
                    f"{removed_count}個の古いセッションをクリーンアップしました"
                )

        return ChatResponse(
            message=response["message"],
            session_id=response["session_id"],
            thought_process=response.get("thought_process"),
            tool_calls=response.get("tool_calls"),
        )

    except Exception as e:
        logger.error(f"メッセージ処理エラー: {str(e)}")
        safe_message = ErrorSanitizer.sanitize_error_message(str(e), "api_call")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_message,
        )


@router.post("/update-llm-config")
async def update_session_llm_config(
    session_id: str = Form(...),
    llm_config: str = Form(...),  # JSON文字列として受信
):
    """
    セッション別のLLM設定を更新する

    Args:
        session_id: セッションID
        llm_config: LLM設定（JSON文字列）

    Returns:
        更新結果
    """
    try:
        # JSON文字列をパース
        config_dict = json.loads(llm_config)

        # セッション管理システムを使用
        session_manager = get_session_manager()

        # セッション別のLLM設定を更新
        success = session_manager.update_session_llm_config(session_id, config_dict)

        if success:
            logger.info(f"セッション {session_id} のLLM設定を更新しました")
            return {"success": True, "message": "LLM設定を更新しました"}
        else:
            # セッションが存在しない場合は新しいAgentManagerを作成
            agent_manager = session_manager.get_or_create_agent_manager(
                session_id, config_dict
            )
            logger.info(f"新しいセッション {session_id} でLLM設定を設定しました")
            return {
                "success": True,
                "message": "新しいセッションでLLM設定を設定しました",
            }

    except json.JSONDecodeError as e:
        logger.error(f"LLM設定のJSONパースエラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LLM設定のJSON形式が正しくありません: {str(e)}",
        )
    except Exception as e:
        logger.error(f"LLM設定更新エラー: {str(e)}")
        safe_message = ErrorSanitizer.sanitize_error_message(str(e), "api_call")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_message,
        )


@router.get("/session-stats")
async def get_session_stats():
    """セッション統計情報を取得"""
    try:
        session_manager = get_session_manager()
        stats = session_manager.get_session_stats()
        return stats
    except Exception as e:
        logger.error(f"セッション統計取得エラー: {str(e)}")
        safe_message = ErrorSanitizer.sanitize_error_message(str(e), "api_call")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_message,
        )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """特定のセッションを削除"""
    try:
        session_manager = get_session_manager()
        removed = session_manager.remove_session(session_id)

        if removed:
            return {
                "success": True,
                "message": f"セッション {session_id} を削除しました",
            }
        else:
            return {
                "success": False,
                "message": f"セッション {session_id} が見つかりません",
            }
    except Exception as e:
        logger.error(f"セッション削除エラー: {str(e)}")
        safe_message = ErrorSanitizer.sanitize_error_message(str(e), "api_call")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_message,
        )


@router.post("/cleanup-sessions")
async def cleanup_old_sessions(max_age_seconds: int = 3600):
    """古いセッションを手動でクリーンアップ"""
    try:
        session_manager = get_session_manager()
        removed_count = session_manager.cleanup_old_sessions(max_age_seconds)

        return {
            "success": True,
            "message": f"{removed_count}個の古いセッションをクリーンアップしました",
            "removed_count": removed_count,
        }
    except Exception as e:
        logger.error(f"セッションクリーンアップエラー: {str(e)}")
        safe_message = ErrorSanitizer.sanitize_error_message(str(e), "api_call")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=safe_message,
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
        safe_message = ErrorSanitizer.sanitize_error_message(str(e), "api_call")

        return FileUploadResponse(
            success=False,
            error=safe_message,
        )
