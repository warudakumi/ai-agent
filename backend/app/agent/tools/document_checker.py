import json
import os
import re
from pathlib import Path

import pandas as pd
from app.agent.tools.base import BaseAgentTool
from loguru import logger


class DocumentCheckerTool(BaseAgentTool):
    """ドキュメントチェックツール"""

    name: str = "document_checker"
    description: str = 'アップロードされたエクセルファイルの内容をチェックします。ファイルパスとチェックタイプ(content_check: 内容チェック, formal_check: 形式チェック, compliance_check: コンプライアンスチェック)を指定してください。例: {"file_path": "/path/to/file.xlsx", "operation": "content_check"}'

    # チェック用のプロンプトテンプレート
    _check_prompts = {
        "content_check": """
以下の観点で、ドキュメントの内容をチェックしてください：
1. 論理的一貫性：内容に矛盾点や論理の飛躍がないか
2. 完全性：必要な情報がすべて含まれているか
3. 明確性：内容が明確で理解しやすいか
4. 構成：情報の構成が適切か
5. 専門用語：専門用語の使用が適切か、または十分な説明があるか
""",
        "formal_check": """
以下の観点で、ドキュメントの形式をチェックしてください：
1. フォーマット：指定されたフォーマットに従っているか
2. 表記統一：用語や表記が統一されているか
3. 誤字脱字：誤字脱字がないか
4. 文法：文法的に正しいか
5. 数値確認：表内の数値が正確か、計算が合っているか
""",
        "compliance_check": """
以下の観点で、ドキュメントのコンプライアンスをチェックしてください：
1. 法令遵守：関連法令に準拠しているか
2. 情報セキュリティ：機密情報の取り扱いが適切か
3. プライバシー：個人情報の取り扱いが適切か
4. 社内規定：社内規定に従っているか
5. リスク評価：潜在的なリスクが適切に評価されているか
""",
    }

    def _run(self, input_str: str) -> str:
        """
        ドキュメントチェックを実行する

        Args:
            input_str: JSON形式の入力。ファイルパスとチェック操作を含む

        Returns:
            チェック結果
        """
        try:
            # 入力をパース
            def loads_with_windows_path(raw: str) -> dict:
                fixed = re.sub(r'(?<!\\)\\(?![\\"])', r"\\\\", raw)
                return json.loads(fixed)

            inputs = (
                loads_with_windows_path(input_str)
                if isinstance(input_str, str)
                else input_str
            )

            file_path = str(Path(inputs.get("file_path")))
            operation = inputs.get("operation", "content_check")

            if not file_path or not os.path.exists(file_path):
                return "エラー: 有効なファイルパスを指定してください"

            # ファイル拡張子の取得
            file_ext = os.path.splitext(file_path)[1].lower()

            # エクセルファイルのみ対応
            if file_ext not in [".xlsx", ".xls"]:
                return "対応していないファイル形式です。エクセルファイル(.xlsx, .xls)を指定してください。"

            # ドキュメントチェックの実行
            return self._check_document(file_path, operation)

        except Exception as e:
            logger.error(f"ドキュメントチェックエラー: {str(e)}")
            return f"ドキュメントチェック中にエラーが発生しました: {str(e)}"

    def _check_document(self, file_path: str, operation: str) -> str:
        """エクセルドキュメントをチェック"""
        try:
            # Excelファイルを読み込む
            excel = pd.ExcelFile(file_path)
            sheet_names = excel.sheet_names

            if not sheet_names:
                return "エラー: エクセルファイルにシートが存在しません"

            # 最初のシートのみを読み込む
            first_sheet = sheet_names[0]
            df = pd.read_excel(file_path, sheet_name=first_sheet)

            # 基本情報の取得
            document_info = "ドキュメント基本情報:\n"
            document_info += f"- ファイル名: {os.path.basename(file_path)}\n"
            document_info += f"- 処理シート名: {first_sheet}\n"

            # データフレームが空でないか確認
            if df.empty:
                document_info += "- シートにデータがありません\n\n"
                document_data = ""
            else:
                # シート内の全データを文字列として取得
                document_data = "シート内の全データ:\n"
                document_data += df.to_string() + "\n\n"

            # チェック種別に応じたプロンプトの取得
            if operation in self._check_prompts:
                check_prompt = self._check_prompts[operation]
                check_instructions = f"チェック指示 ({operation}):\n{check_prompt}\n\n"

                # ドキュメント情報とチェック指示を返す
                return document_info + document_data + check_instructions
            else:
                # 未対応の操作
                available_operations = ", ".join(self._check_prompts.keys())
                return f"未対応のチェック種別です: {operation}\n利用可能なチェック種別: {available_operations}"

        except Exception as e:
            logger.error(f"ドキュメントチェックエラー: {str(e)}")
            return f"ドキュメントチェック中にエラーが発生しました: {str(e)}"
