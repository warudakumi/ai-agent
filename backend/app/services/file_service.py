import os
import uuid
from pathlib import Path

import aiofiles
from app.config import UPLOAD_DIR
from app.core.settings import get_settings
from app.models.chat import FileInfo
from fastapi import HTTPException, UploadFile, status
from loguru import logger


async def save_uploaded_file(file: UploadFile) -> str:
    """
    アップロードされたファイルを保存し、ファイルパスを返す

    Args:
        file: アップロードされたファイル

    Returns:
        保存されたファイルのパス

    Raises:
        HTTPException: ファイル保存に失敗した場合
    """
    settings = get_settings()

    # ファイル拡張子の確認
    file_ext = Path(file.filename).suffix.replace(".", "").lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ファイル形式が許可されていません。許可される拡張子: {', '.join(settings.allowed_extensions)}",
        )

    # ファイルサイズの確認
    content = await file.read()
    await file.seek(0)  # ファイルポインタをリセット
    if len(content) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ファイルサイズが大きすぎます。上限: {settings.max_upload_size / (1024 * 1024)}MB",
        )

    # ユニークなファイル名の生成
    unique_filename = f"{uuid.uuid4().hex}_{Path(file.filename).name}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # ファイルを保存
        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)

        logger.info(f"ファイルを保存しました: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"ファイル保存エラー: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ファイル保存中にエラーが発生しました: {str(e)}",
        )


async def get_file_info(file_path: str) -> FileInfo:
    """
    ファイルパスからファイル情報を取得する

    Args:
        file_path: ファイルパス

    Returns:
        ファイル情報
    """
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ファイルが見つかりません"
        )

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    file_type = Path(file_path).suffix.replace(".", "").lower()
    file_id = file_name.split("_")[0]  # UUIDの部分

    return FileInfo(
        file_id=file_id,
        filename=file_name.split("_", 1)[1],  # ユニークID部分を削除
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
    )


async def delete_file(file_path: str) -> bool:
    """
    ファイルを削除する

    Args:
        file_path: ファイルパス

    Returns:
        削除成功の場合はTrue
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"ファイルを削除しました: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"ファイル削除エラー: {str(e)}")
        return False
