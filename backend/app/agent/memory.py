from typing import Any, Dict, List

from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class AgentMemory:
    """エージェントのメモリクラス - セッション別に分離"""

    def __init__(self):
        # セッション別のチャット履歴を管理
        self.session_histories: Dict[str, ChatMessageHistory] = {}
        self.session_memories: Dict[str, ConversationBufferMemory] = {}
        self.file_contexts: Dict[
            str, Dict[str, str]
        ] = {}  # セッションごとのファイルコンテキスト

    def _get_or_create_session_history(self, session_id: str) -> ChatMessageHistory:
        """セッション別のチャット履歴を取得または作成"""
        if session_id not in self.session_histories:
            self.session_histories[session_id] = ChatMessageHistory()
            self.session_memories[session_id] = ConversationBufferMemory(
                chat_memory=self.session_histories[session_id], return_messages=True
            )
        return self.session_histories[session_id]

    def add_user_message(self, session_id: str, message: str) -> None:
        """ユーザーメッセージをセッション別メモリに追加"""
        chat_history = self._get_or_create_session_history(session_id)
        chat_history.add_user_message(message)

    def add_ai_message(self, session_id: str, message: str) -> None:
        """AIメッセージをセッション別メモリに追加"""
        chat_history = self._get_or_create_session_history(session_id)
        chat_history.add_ai_message(message)

    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """セッション別のチャット履歴を取得"""
        chat_history = self._get_or_create_session_history(session_id)
        messages = chat_history.messages

        history = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                history.append({"role": "system", "content": msg.content})

        return history

    def add_file_context(self, session_id: str, file_id: str, context: str) -> None:
        """ファイルコンテキストをセッション別に追加"""
        if session_id not in self.file_contexts:
            self.file_contexts[session_id] = {}
        self.file_contexts[session_id][file_id] = context

    def get_file_contexts(self, session_id: str) -> Dict[str, str]:
        """セッションのファイルコンテキストを取得"""
        return self.file_contexts.get(session_id, {})

    def clear_session(self, session_id: str) -> None:
        """セッションの履歴を完全にクリア"""
        if session_id in self.session_histories:
            del self.session_histories[session_id]
        if session_id in self.session_memories:
            del self.session_memories[session_id]
        if session_id in self.file_contexts:
            del self.file_contexts[session_id]

    def get_session_count(self) -> int:
        """アクティブなセッション数を取得"""
        return len(self.session_histories)

    def get_all_session_ids(self) -> List[str]:
        """全セッションIDを取得"""
        return list(self.session_histories.keys())
