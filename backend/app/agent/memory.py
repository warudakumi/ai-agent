from typing import Any, Dict, List

from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class AgentMemory:
    """エージェントのメモリクラス"""

    def __init__(self):
        self.chat_history = ChatMessageHistory()
        self.memory = ConversationBufferMemory(
            chat_memory=self.chat_history, return_messages=True
        )
        self.file_contexts = {}  # セッションごとのファイルコンテキスト

    def add_user_message(self, session_id: str, message: str) -> None:
        """ユーザーメッセージをメモリに追加"""
        key = f"conversation_{session_id}"
        self.chat_history.add_user_message(message)

    def add_ai_message(self, session_id: str, message: str) -> None:
        """AIメッセージをメモリに追加"""
        key = f"conversation_{session_id}"
        self.chat_history.add_ai_message(message)

    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """チャット履歴を取得"""
        messages = self.chat_history.messages

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
        """ファイルコンテキストを追加"""
        if session_id not in self.file_contexts:
            self.file_contexts[session_id] = {}

        self.file_contexts[session_id][file_id] = context

    def get_file_contexts(self, session_id: str) -> Dict[str, str]:
        """セッションのファイルコンテキストを取得"""
        return self.file_contexts.get(session_id, {})

    def clear_session(self, session_id: str) -> None:
        """セッションの履歴をクリア"""
        self.chat_history.clear()
        if session_id in self.file_contexts:
            del self.file_contexts[session_id]
