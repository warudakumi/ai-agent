import asyncio
import uuid
from typing import Any, Dict, List, Optional

from app.agent.graph.workflow import AgentState, create_workflow
from app.agent.memory import AgentMemory
from app.agent.tools import get_tools
from app.core.error_handler import ErrorSanitizer
from app.services.llm_service import get_llm
from loguru import logger


class AgentManager:
    """エージェントマネージャクラス - セッション別管理対応"""

    def __init__(self, llm_config: Dict[str, Any]):
        """
        AgentManagerの初期化

        Args:
            llm_config: デフォルトLLM設定
        """
        self.default_llm_config = llm_config
        self.default_llm = get_llm(llm_config)
        self.memory = AgentMemory()
        self.tools = get_tools()
        self.default_workflow = create_workflow(self.default_llm, self.tools)
        self.sessions = {}  # セッション情報
        self.session_llm_configs = {}  # セッション別LLM設定
        self.session_llms = {}  # セッション別LLMインスタンス
        self.session_workflows = {}  # セッション別ワークフロー

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """
        セッションを取得または作成する

        Args:
            session_id: セッションID（オプション）

        Returns:
            セッションID
        """
        if not session_id or session_id not in self.sessions:
            new_session_id = session_id or str(uuid.uuid4())
            current_time = asyncio.get_event_loop().time()
            self.sessions[new_session_id] = {
                "created_at": current_time,
                "last_used": current_time,
                "message_count": 0,
            }
            # セッション別のLLM設定をデフォルトで初期化
            self.session_llm_configs[new_session_id] = self.default_llm_config.copy()
            logger.info(f"新しいセッションを作成: {new_session_id}")
            return new_session_id

        # 既存セッションの最終使用時間を更新
        self.sessions[session_id]["last_used"] = asyncio.get_event_loop().time()
        return session_id

    def get_session_llm_config(self, session_id: str) -> Dict[str, Any]:
        """セッション別のLLM設定を取得"""
        return self.session_llm_configs.get(session_id, self.default_llm_config)

    def update_session_llm_config(
        self, session_id: str, llm_config: Dict[str, Any]
    ) -> None:
        """セッション別のLLM設定を更新"""
        if session_id not in self.sessions:
            self.get_or_create_session(session_id)

        self.session_llm_configs[session_id] = llm_config.copy()

        # セッション別のLLMインスタンスとワークフローを再作成
        try:
            self.session_llms[session_id] = get_llm(llm_config)
            self.session_workflows[session_id] = create_workflow(
                self.session_llms[session_id], self.tools
            )
            logger.info(f"セッション {session_id} のLLM設定を更新しました")
        except Exception as e:
            logger.error(f"セッション {session_id} のLLM設定更新エラー: {str(e)}")
            # エラー時はデフォルト設定を使用
            self.session_llm_configs[session_id] = self.default_llm_config.copy()

    def get_session_workflow(self, session_id: str):
        """セッション別のワークフローを取得"""
        if session_id in self.session_workflows:
            return self.session_workflows[session_id]

        # セッション別ワークフローが存在しない場合はデフォルトを使用
        return self.default_workflow

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        file_paths: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        メッセージを処理する

        Args:
            message: ユーザーメッセージ
            session_id: セッションID（オプション）
            file_paths: 添付ファイルのパスリスト（オプション）

        Returns:
            処理結果
        """
        try:
            # セッション管理
            session_id = self.get_or_create_session(session_id)
            self.sessions[session_id]["message_count"] += 1

            # ファイル情報の追加（存在する場合）
            if file_paths and len(file_paths) > 0:
                file_info = "\n添付ファイル:\n" + "\n".join(
                    [f"- {path}" for path in file_paths]
                )
                enriched_message = f"{message}\n\n{file_info}"
            else:
                enriched_message = message

            # メモリにユーザーメッセージを追加
            self.memory.add_user_message(session_id, enriched_message)

            # ワークフロー用の初期状態を作成
            initial_state: AgentState = {
                "messages": self.memory.get_chat_history(session_id),
                "current_thought": "",
                "tool_calls": [],
                "tools_output": [],
                "final_response": None,
                "error": None,
            }

            # セッション別のワークフローを取得して実行
            workflow = self.get_session_workflow(session_id)
            logger.info(f"ワークフロー実行開始: セッションID={session_id}")
            result_state = await asyncio.to_thread(workflow.invoke, initial_state)

            # エラー処理
            if result_state.get("error"):
                logger.error(f"ワークフローエラー: {result_state['error']}")
                response = f"申し訳ありません、処理中にエラーが発生しました: {result_state['error']}"
            else:
                response = result_state.get(
                    "final_response", "応答を生成できませんでした。"
                )

            # メモリにAIメッセージを追加
            self.memory.add_ai_message(session_id, response)

            # 応答を返す
            return {
                "message": response,
                "session_id": session_id,
                "thought_process": result_state.get("current_thought", ""),
                "tool_calls": result_state.get("tools_output", []),
            }

        except Exception as e:
            logger.error(f"メッセージ処理エラー: {str(e)}")

            # エラーメッセージをサニタイズ
            safe_message = ErrorSanitizer.sanitize_error_message(str(e), "workflow")

            return {
                "message": f"申し訳ありません、{safe_message}",
                "session_id": session_id or str(uuid.uuid4()),
                "thought_process": "",
                "tool_calls": [],
            }

    def cleanup_old_sessions(self, max_age_seconds: int = 3600) -> int:
        """
        古いセッションをクリーンアップする

        Args:
            max_age_seconds: 最大セッション有効期間（秒）

        Returns:
            削除されたセッション数
        """
        current_time = asyncio.get_event_loop().time()
        sessions_to_remove = []

        for session_id, session_info in self.sessions.items():
            if current_time - session_info["last_used"] > max_age_seconds:
                sessions_to_remove.append(session_id)

        # 古いセッションを削除
        for session_id in sessions_to_remove:
            self.memory.clear_session(session_id)
            if session_id in self.session_llm_configs:
                del self.session_llm_configs[session_id]
            if session_id in self.session_llms:
                del self.session_llms[session_id]
            if session_id in self.session_workflows:
                del self.session_workflows[session_id]
            del self.sessions[session_id]
            logger.info(f"古いセッションを削除: {session_id}")

        return len(sessions_to_remove)

    def get_session_stats(self) -> Dict[str, Any]:
        """セッション統計情報を取得"""
        return {
            "total_sessions": len(self.sessions),
            "memory_sessions": self.memory.get_session_count(),
            "llm_config_sessions": len(self.session_llm_configs),
            "active_workflows": len(self.session_workflows),
        }
