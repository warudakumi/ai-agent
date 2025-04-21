from typing import Any, Dict, List, Optional

import requests
from langchain.llms.base import LLM
from langchain_community.chat_models import AzureChatOpenAI
from langchain_openai import ChatOpenAI
from loguru import logger


# 擬似的なローカルLLMクラス
class LocalLLM(LLM):
    """カスタムのローカルLLMクラス"""

    endpoint: str
    temperature: float

    @property
    def _llm_type(self) -> str:
        return "local_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        ローカルLLMを呼び出す

        Args:
            prompt: プロンプト文字列
            stop: 停止文字列のリスト

        Returns:
            LLMからの応答
        """
        try:
            # ローカルLLMのエンドポイントにリクエスト送信
            response = requests.post(
                self.endpoint,
                json={
                    "prompt": prompt,
                    "temperature": self.temperature,
                    "max_tokens": 2000,
                    "stop": stop,
                },
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                logger.error(
                    f"ローカルLLMエラー: ステータスコード {response.status_code}"
                )
                return f"エラー: ローカルLLMからの応答取得に失敗しました（ステータスコード: {response.status_code}）"

        except Exception as e:
            logger.error(f"ローカルLLM呼び出しエラー: {str(e)}")
            return f"エラー: ローカルLLMの呼び出しに失敗しました: {str(e)}"


def get_llm(config: Dict[str, Any]) -> LLM:
    """
    設定に基づいてLLMインスタンスを生成する

    Args:
        config: LLM設定

    Returns:
        LLMインスタンス
    """
    provider = config.get("provider", "azure")

    if provider == "azure":
        try:
            return AzureChatOpenAI(
                deployment_name=config.get("deployment_name", ""),
                openai_api_version=config.get("api_version", "2023-05-15"),
                openai_api_key=config.get("api_key", ""),
                openai_api_base=config.get("endpoint", ""),
                temperature=float(config.get("temperature", 0.7)),
            )
        except Exception as e:
            logger.error(f"Azure OpenAI初期化エラー: {str(e)}")
            raise ValueError(f"Azure OpenAIの初期化に失敗しました: {str(e)}")
    elif provider == "openai":
        try:
            return ChatOpenAI(
                model_name=config.get("model_name", "gpt-3.5-turbo"),
                openai_api_key=config.get("api_key", ""),
                temperature=float(config.get("temperature", 0.7)),
            )
        except Exception as e:
            logger.error(f"OpenAI初期化エラー: {str(e)}")
            raise ValueError(f"OpenAIの初期化に失敗しました: {str(e)}")
    else:
        # ローカルLLM
        return LocalLLM(
            endpoint=config.get("endpoint", "http://localhost:8000"),
            temperature=float(config.get("temperature", 0.7)),
        )
