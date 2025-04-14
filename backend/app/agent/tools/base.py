from langchain.tools import BaseTool


class BaseAgentTool(BaseTool):
    """Agentツールの基底クラス"""

    # オーバーライドするプロパティ
    name: str = "base_tool"
    description: str = "基本ツール"

    def _run(self, query: str) -> str:
        """ツール実行ロジック（同期）"""
        raise NotImplementedError("サブクラスでオーバーライドしてください")

    async def _arun(self, query: str) -> str:
        """ツール実行ロジック（非同期）"""
        # デフォルトでは同期メソッドを呼び出す
        return self._run(query)
