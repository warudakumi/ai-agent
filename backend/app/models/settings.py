from typing import Optional

from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    """LLM設定モデル"""

    provider: str = Field(..., description="LLMプロバイダー（azure または local）")
    endpoint: str = Field(..., description="LLMのエンドポイントURL")
    api_key: Optional[str] = Field(None, description="APIキー（Azureの場合は必須）")
    deployment_name: Optional[str] = Field(
        None, description="デプロイメント名（Azureの場合は必須）"
    )
    api_version: Optional[str] = Field(
        "2023-05-15", description="APIバージョン（Azureの場合）"
    )
    temperature: float = Field(
        0.7, description="生成時の温度パラメータ", ge=0.0, le=1.0
    )


class MSGraphSettings(BaseModel):
    """Microsoft Graph設定モデル"""

    client_id: str = Field(..., description="アプリケーション（クライアント）ID")
    tenant_id: str = Field(..., description="ディレクトリ（テナント）ID")
    client_secret: str = Field(..., description="クライアントシークレット")
    redirect_uri: str = Field(..., description="リダイレクトURI")


class SettingsResponse(BaseModel):
    """設定レスポンスモデル"""

    success: bool
    message: str
    data: Optional[dict] = None
