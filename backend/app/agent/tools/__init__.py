from typing import List

from app.agent.tools.base import BaseAgentTool
from app.agent.tools.file_processor import FileProcessorTool
from app.agent.tools.web_search import WebSearchTool


def get_tools() -> List[BaseAgentTool]:
    """利用可能なツールのリストを取得"""
    return [
        WebSearchTool(),
        FileProcessorTool(),
        # 新しいツールはここに追加
    ]
