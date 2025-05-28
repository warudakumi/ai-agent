from typing import Any, Dict, List, Optional

import requests
from langchain_community.chat_models import AzureChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_openai import ChatOpenAI
from loguru import logger


# ローカルLLMクラス（ChatModel準拠）
class LocalLLM(BaseChatModel):
    """カスタムのローカルLLMクラス - local_llm_api.md準拠、ChatModel互換"""

    endpoint: str
    temperature: float
    model_type: str = "quantized"  # デフォルトは量子化モデル

    @property
    def _llm_type(self) -> str:
        return "local_llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        メッセージリストからレスポンスを生成する（ChatModel準拠）

        Args:
            messages: メッセージのリスト
            stop: 停止文字列のリスト（現在のAPIでは未対応）
            run_manager: 実行マネージャー（未使用）
            **kwargs: 追加のキーワード引数

        Returns:
            ChatResult: チャット結果
        """
        # メッセージを単一のプロンプトに変換
        prompt = self._messages_to_prompt(messages)

        # ローカルLLMを呼び出し
        response_text = self._call_local_llm(prompt, stop)

        # AIMessageとして返す
        message = AIMessage(content=response_text)
        generation = ChatGeneration(message=message)

        return ChatResult(generations=[generation])

    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """メッセージリストを単一のプロンプトに変換"""
        prompt_parts = []

        for message in messages:
            if isinstance(message, HumanMessage):
                prompt_parts.append(f"Human: {message.content}")
            elif isinstance(message, AIMessage):
                prompt_parts.append(f"Assistant: {message.content}")
            else:
                # SystemMessageやその他のメッセージタイプ
                prompt_parts.append(f"{message.__class__.__name__}: {message.content}")

        # 最後にAssistant:を追加して応答を促す
        prompt_parts.append("Assistant:")

        return "\n".join(prompt_parts)

    def _call_local_llm(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        ローカルLLMを呼び出す（local_llm_api.md準拠）

        Args:
            prompt: プロンプト文字列
            stop: 停止文字列のリスト（現在のAPIでは未対応）

        Returns:
            LLMからの応答
        """
        try:
            # local_llm_api.mdで定義されている/chatエンドポイントの形式に合わせる
            chat_endpoint = f"{self.endpoint.rstrip('/')}/chat"

            request_data = {"message": prompt, "model_type": self.model_type}

            logger.debug(
                f"ローカルLLMリクエスト: {chat_endpoint}, データ: {request_data}"
            )

            response = requests.post(
                chat_endpoint,
                json=request_data,
                timeout=120,  # ローカルLLMは処理時間が長い場合があるため延長
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                result = response.json()
                # レスポンス形式を確認してテキストを抽出
                if isinstance(result, dict):
                    # 一般的なレスポンス形式を想定
                    response_text = (
                        result.get("response")
                        or result.get("text")
                        or result.get("message")
                        or result.get("content")
                        or str(result)
                    )
                    logger.debug(f"ローカルLLMレスポンス: {response_text[:100]}...")
                    return response_text
                else:
                    return str(result)
            else:
                error_msg = (
                    f"ローカルLLMエラー: ステータスコード {response.status_code}"
                )
                try:
                    error_detail = response.json()
                    error_msg += f", 詳細: {error_detail}"
                except:
                    error_msg += f", レスポンス: {response.text}"

                logger.error(error_msg)
                return f"エラー: ローカルLLMからの応答取得に失敗しました（ステータスコード: {response.status_code}）"

        except requests.exceptions.Timeout:
            logger.error("ローカルLLM呼び出しタイムアウト")
            return "エラー: ローカルLLMの呼び出しがタイムアウトしました"
        except requests.exceptions.ConnectionError:
            logger.error("ローカルLLMへの接続エラー")
            return "エラー: ローカルLLMサーバーに接続できません。サーバーが起動しているか確認してください"
        except Exception as e:
            logger.error(f"ローカルLLM呼び出しエラー: {str(e)}")
            return f"エラー: ローカルLLMの呼び出しに失敗しました: {str(e)}"

    # 後方互換性のため_callメソッドも残す
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        後方互換性のためのメソッド
        """
        return self._call_local_llm(prompt, stop)


def get_llm(config: Dict[str, Any]) -> Any:
    """
    設定に基づいてLLMインスタンスを生成する

    Args:
        config: LLM設定

    Returns:
        LLMインスタンス（ChatModel互換）
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
            model_type=config.get(
                "model_type", "quantized"
            ),  # モデルタイプを設定から取得
        )
