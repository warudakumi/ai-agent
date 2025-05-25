"""
セッション管理を一元化するモジュール
複数ユーザーアクセス時のセッション分離を確実にする
"""

import asyncio
import uuid
from typing import Any, Dict, Optional

from app.agent.core import AgentManager
from loguru import logger


class SessionManager:
    """セッション管理クラス - シングルトンパターン"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.agent_managers: Dict[str, AgentManager] = {}
            self.session_metadata: Dict[str, Dict[str, Any]] = {}
            self._initialized = True
            logger.info("SessionManagerを初期化しました")

    def get_or_create_agent_manager(
        self, session_id: str, llm_config: Dict[str, Any]
    ) -> AgentManager:
        """セッション別のAgentManagerを取得または作成"""
        if not session_id:
            session_id = str(uuid.uuid4())

        if session_id not in self.agent_managers:
            self.agent_managers[session_id] = AgentManager(llm_config)
            self.session_metadata[session_id] = {
                "created_at": asyncio.get_event_loop().time(),
                "last_used": asyncio.get_event_loop().time(),
                "request_count": 0,
            }
            logger.info(f"セッション {session_id} 用のAgentManagerを作成しました")
        else:
            # 最終使用時間を更新
            self.session_metadata[session_id]["last_used"] = (
                asyncio.get_event_loop().time()
            )

        self.session_metadata[session_id]["request_count"] += 1
        return self.agent_managers[session_id]

    def get_agent_manager(self, session_id: str) -> Optional[AgentManager]:
        """セッションのAgentManagerを取得（存在しない場合はNone）"""
        return self.agent_managers.get(session_id)

    def update_session_llm_config(
        self, session_id: str, llm_config: Dict[str, Any]
    ) -> bool:
        """セッション別のLLM設定を更新"""
        if session_id in self.agent_managers:
            try:
                self.agent_managers[session_id].update_session_llm_config(
                    session_id, llm_config
                )
                logger.info(f"セッション {session_id} のLLM設定を更新しました")
                return True
            except Exception as e:
                logger.error(f"セッション {session_id} のLLM設定更新エラー: {str(e)}")
                return False
        return False

    def get_session_llm_config(self, session_id: str) -> Optional[Dict[str, Any]]:
        """セッション別のLLM設定を取得"""
        if session_id in self.agent_managers:
            return self.agent_managers[session_id].get_session_llm_config(session_id)
        return None

    def cleanup_old_sessions(self, max_age_seconds: int = 3600) -> int:
        """古いセッションをクリーンアップ"""
        current_time = asyncio.get_event_loop().time()
        sessions_to_remove = []

        for session_id, metadata in self.session_metadata.items():
            if current_time - metadata["last_used"] > max_age_seconds:
                sessions_to_remove.append(session_id)

        removed_count = 0
        for session_id in sessions_to_remove:
            if session_id in self.agent_managers:
                # AgentManager内のセッションもクリーンアップ
                self.agent_managers[session_id].cleanup_old_sessions(max_age_seconds)
                del self.agent_managers[session_id]
                removed_count += 1

            if session_id in self.session_metadata:
                del self.session_metadata[session_id]

            logger.info(f"古いセッション {session_id} をクリーンアップしました")

        return removed_count

    def get_session_stats(self) -> Dict[str, Any]:
        """セッション統計情報を取得"""
        total_sessions = 0
        total_memory_sessions = 0

        for manager in self.agent_managers.values():
            stats = manager.get_session_stats()
            total_sessions += stats.get("total_sessions", 0)
            total_memory_sessions += stats.get("memory_sessions", 0)

        return {
            "total_agent_managers": len(self.agent_managers),
            "total_sessions": total_sessions,
            "total_memory_sessions": total_memory_sessions,
            "session_metadata_count": len(self.session_metadata),
            "manager_details": {
                session_id: manager.get_session_stats()
                for session_id, manager in self.agent_managers.items()
            },
        }

    def remove_session(self, session_id: str) -> bool:
        """特定のセッションを削除"""
        removed = False

        if session_id in self.agent_managers:
            # AgentManager内のセッションデータをクリア
            self.agent_managers[session_id].memory.clear_session(session_id)
            del self.agent_managers[session_id]
            removed = True

        if session_id in self.session_metadata:
            del self.session_metadata[session_id]
            removed = True

        if removed:
            logger.info(f"セッション {session_id} を削除しました")

        return removed

    def get_all_session_ids(self) -> list[str]:
        """全セッションIDを取得"""
        return list(self.agent_managers.keys())


# シングルトンインスタンスを取得する関数
def get_session_manager() -> SessionManager:
    """SessionManagerのシングルトンインスタンスを取得"""
    return SessionManager()
