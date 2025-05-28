from typing import Optional

from pydantic import BaseModel, Field


class LLMSettings(BaseModel):
    """LLM設定モデル"""

    provider: str = Field(
        ..., description="LLMプロバイダー（azure、openai または local）"
    )
    endpoint: Optional[str] = Field(
        None, description="LLMのエンドポイントURL（azure または local の場合）"
    )
    api_key: Optional[str] = Field(
        None, description="APIキー（azure または openai の場合は必須）"
    )
    deployment_name: Optional[str] = Field(
        None, description="デプロイメント名（azureの場合は必須）"
    )
    model_name: Optional[str] = Field(
        None, description="モデル名（openaiの場合は必須、例: gpt-3.5-turbo, gpt-4）"
    )
    api_version: Optional[str] = Field(
        "2023-05-15", description="APIバージョン（azureの場合）"
    )
    temperature: float = Field(
        0.7, description="生成時の温度パラメータ", ge=0.0, le=1.0
    )
    model_type: Optional[str] = Field(
        "quantized", description="ローカルLLMのモデルタイプ（normal または quantized）"
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
