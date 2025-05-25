"""
エラーハンドリングとメッセージサニタイズのユーティリティ
"""

import re
from typing import Any, Dict

from loguru import logger


class ErrorSanitizer:
    """エラーメッセージをサニタイズするクラス"""

    # 機密情報を含む可能性があるパターン
    SENSITIVE_PATTERNS = [
        r"api[_-]?key[:\s=]+[a-zA-Z0-9\-_]+",  # APIキー
        r"password[:\s=]+\S+",  # パスワード
        r"token[:\s=]+[a-zA-Z0-9\-_\.]+",  # トークン
        r"secret[:\s=]+\S+",  # シークレット
        r"connection[:\s]+.*://.*",  # 接続文字列
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # メールアドレス
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",  # IPアドレス
        r'file[:\s]+["\']?[a-zA-Z]:[\\\/].*["\']?',  # Windowsファイルパス
        r'file[:\s]+["\']?\/.*["\']?',  # Unixファイルパス
    ]

    # 一般的なエラーメッセージマッピング
    ERROR_MAPPINGS = {
        "connection": "サービスに接続できませんでした。しばらく時間をおいてから再度お試しください。",
        "timeout": "リクエストがタイムアウトしました。しばらく時間をおいてから再度お試しください。",
        "authentication": "認証に失敗しました。設定を確認してください。",
        "authorization": "アクセス権限がありません。",
        "not_found": "要求されたリソースが見つかりません。",
        "validation": "入力データに問題があります。内容を確認してください。",
        "file_not_found": "ファイルが見つかりません。",
        "permission": "ファイルまたはディレクトリへのアクセス権限がありません。",
        "disk_space": "ディスク容量が不足しています。",
        "memory": "メモリ不足が発生しました。",
        "network": "ネットワークエラーが発生しました。",
    }

    @classmethod
    def sanitize_error_message(
        cls, error_message: str, context: str = "general"
    ) -> str:
        """
        エラーメッセージをサニタイズして安全なメッセージを返す

        Args:
            error_message: 元のエラーメッセージ
            context: エラーのコンテキスト（例：'file_processing', 'llm_call'）

        Returns:
            サニタイズされたエラーメッセージ
        """
        if not error_message:
            return "予期しないエラーが発生しました。"

        # 元のメッセージをログに記録（デバッグ用）
        logger.debug(f"元のエラーメッセージ [{context}]: {error_message}")

        # 機密情報を除去
        sanitized = cls._remove_sensitive_info(error_message)

        # 一般的なエラーパターンをチェック
        user_friendly_message = cls._get_user_friendly_message(sanitized, context)

        return user_friendly_message

    @classmethod
    def _remove_sensitive_info(cls, message: str) -> str:
        """機密情報を含む可能性がある部分を除去"""
        sanitized = message

        for pattern in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, "[機密情報]", sanitized, flags=re.IGNORECASE)

        return sanitized

    @classmethod
    def _get_user_friendly_message(cls, message: str, context: str) -> str:
        """ユーザーフレンドリーなメッセージを生成"""
        message_lower = message.lower()

        # 特定のエラーパターンをチェック
        for error_type, friendly_message in cls.ERROR_MAPPINGS.items():
            if error_type in message_lower:
                return friendly_message

        # コンテキスト別のメッセージ
        context_messages = {
            "file_processing": "ファイルの処理中に問題が発生しました。ファイル形式や内容を確認してください。",
            "llm_call": "AI処理中に問題が発生しました。しばらく時間をおいてから再度お試しください。",
            "tool_execution": "ツールの実行中に問題が発生しました。入力内容を確認してください。",
            "workflow": "ワークフローの実行中に問題が発生しました。",
            "api_call": "API呼び出し中に問題が発生しました。",
        }

        if context in context_messages:
            return context_messages[context]

        # デフォルトメッセージ
        return (
            "処理中に問題が発生しました。しばらく時間をおいてから再度お試しください。"
        )


def create_safe_error_response(
    error: Exception, context: str = "general", include_error_id: bool = True
) -> Dict[str, Any]:
    """
    安全なエラーレスポンスを作成

    Args:
        error: 発生した例外
        context: エラーのコンテキスト
        include_error_id: エラーIDを含めるかどうか

    Returns:
        安全なエラーレスポンス
    """
    import uuid

    error_id = str(uuid.uuid4())[:8] if include_error_id else None

    # 元のエラーをログに記録
    logger.error(f"エラーID: {error_id}, コンテキスト: {context}, エラー: {str(error)}")

    # サニタイズされたメッセージを生成
    safe_message = ErrorSanitizer.sanitize_error_message(str(error), context)

    response = {
        "success": False,
        "message": safe_message,
    }

    if error_id:
        response["error_id"] = error_id
        response["message"] += f" (エラーID: {error_id})"

    return response
