from app.agent.tools.base import BaseAgentTool
from app.core.error_handler import ErrorSanitizer
from loguru import logger


class WebSearchTool(BaseAgentTool):
    """Web検索ツール"""

    name: str = "web_search"
    description: str = (
        "ウェブ上で情報を検索します。クエリを文字列として渡してください。"
    )

    def _run(self, query: str) -> str:
        """
        Web検索を実行する（モック実装）

        Args:
            query: 検索クエリ

        Returns:
            検索結果
        """
        logger.info(f"Web検索: {query}")

        try:
            # モック検索結果の生成
            # 実際にはここでBing APIやGoogle APIなどを呼び出す
            mock_results = [
                {
                    "title": f"検索結果1 - {query}に関する情報",
                    "snippet": f"{query}に関する詳細情報です。これは最も関連性の高い結果です。",
                    "url": f"https://example.com/result1?q={query}",
                },
                {
                    "title": f"検索結果2 - {query}の歴史",
                    "snippet": f"{query}の歴史的背景と発展について解説しています。",
                    "url": f"https://example.com/result2?q={query}",
                },
                {
                    "title": f"検索結果3 - {query}の使い方ガイド",
                    "snippet": f"{query}の基本的な使い方と応用例を紹介します。",
                    "url": f"https://example.com/result3?q={query}",
                },
            ]

            results_text = f"「{query}」の検索結果:\n\n"
            for i, result in enumerate(mock_results, 1):
                results_text += f"{i}. {result['title']}\n"
                results_text += f"   {result['snippet']}\n"
                results_text += f"   URL: {result['url']}\n\n"

            return results_text

        except Exception as e:
            logger.error(f"Web検索エラー: {str(e)}")
            safe_message = ErrorSanitizer.sanitize_error_message(
                str(e), "tool_execution"
            )
            return safe_message
