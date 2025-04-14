from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """チャットリクエストモデル"""

    message: str
    session_id: Optional[str] = None
    file_ids: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """チャットレスポンスモデル"""

    message: str
    session_id: str
    thought_process: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class FileInfo(BaseModel):
    """ファイル情報モデル"""

    file_id: str
    filename: str
    file_path: str
    file_size: int
    file_type: str


class FileUploadResponse(BaseModel):
    """ファイルアップロードレスポンスモデル"""

    success: bool
    file_info: Optional[FileInfo] = None
    error: Optional[str] = None
