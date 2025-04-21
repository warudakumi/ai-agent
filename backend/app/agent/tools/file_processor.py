import json
import os

import pandas as pd
from app.agent.tools.base import BaseAgentTool
from loguru import logger


class FileProcessorTool(BaseAgentTool):
    """ファイル処理ツール"""

    name: str = "file_processor"
    description: str = 'アップロードされたファイルを処理します。ファイルパスと処理タイプを指定してください。例: {"file_path": "/path/to/file.csv", "operation": "summarize"}'

    def _run(self, input_str: str) -> str:
        """
        ファイル処理を実行する

        Args:
            input_str: JSON形式の入力。ファイルパスと操作を含む

        Returns:
            処理結果
        """
        try:
            # 入力をパース
            inputs = json.loads(input_str) if isinstance(input_str, str) else input_str
            file_path = inputs.get("file_path")
            operation = inputs.get("operation", "summarize")

            if not file_path or not os.path.exists(file_path):
                return "エラー: 有効なファイルパスを指定してください"

            # ファイル拡張子の取得
            file_ext = os.path.splitext(file_path)[1].lower()
            print(file_ext)

            # ファイルタイプに応じた処理
            if file_ext == ".csv":
                return self._process_csv(file_path, operation)
            elif file_ext == ".txt":
                return self._process_text(file_path, operation)
            elif file_ext in [".xlsx", ".xls"]:
                return self._process_excel(file_path, operation)
            elif file_ext == ".json":
                return self._process_json(file_path, operation)
            else:
                return f"未対応のファイル形式です: {file_ext}"

        except Exception as e:
            logger.error(f"ファイル処理エラー: {str(e)}")
            return f"ファイル処理中にエラーが発生しました: {str(e)}"

    def _process_csv(self, file_path: str, operation: str) -> str:
        """CSVファイルを処理"""
        try:
            df = pd.read_csv(file_path)

            if operation == "summarize":
                # データの概要を生成
                summary = "CSVファイル概要:\n"
                summary += f"- レコード数: {len(df)}\n"
                summary += f"- カラム数: {len(df.columns)}\n"
                summary += f"- カラム名: {', '.join(df.columns)}\n\n"

                # サンプルデータの表示（先頭5行）
                summary += "サンプルデータ（先頭5行）:\n"
                summary += df.head(5).to_string() + "\n\n"

                # データタイプの情報
                summary += "データタイプ情報:\n"
                dtypes = df.dtypes.astype(str).to_dict()
                for col, dtype in dtypes.items():
                    summary += f"- {col}: {dtype}\n"

                return summary

            elif operation == "columns":
                # カラム情報のみを返す
                columns = ", ".join(df.columns)
                return f"CSVのカラム一覧: {columns}"

            else:
                return f"未対応の操作です: {operation}"

        except Exception as e:
            logger.error(f"CSV処理エラー: {str(e)}")
            return f"CSVファイル処理中にエラーが発生しました: {str(e)}"

    def _process_text(self, file_path: str, operation: str) -> str:
        """テキストファイルを処理"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if operation == "summarize":
                # 簡単な要約を生成
                lines = content.split("\n")
                line_count = len(lines)
                word_count = len(content.split())
                char_count = len(content)

                summary = "テキストファイル概要:\n"
                summary += f"- 行数: {line_count}\n"
                summary += f"- 単語数: {word_count}\n"
                summary += f"- 文字数: {char_count}\n\n"

                # 最初の5行を表示
                summary += "ファイル先頭（最大5行）:\n"
                preview_lines = lines[:5]
                summary += "\n".join(preview_lines)

                return summary

            elif operation == "content":
                # ファイル内容全体を返す
                if len(content) > 2000:
                    return content[:2000] + "...(以下省略)"
                return content

            else:
                return f"未対応の操作です: {operation}"

        except Exception as e:
            logger.error(f"テキスト処理エラー: {str(e)}")
            return f"テキストファイル処理中にエラーが発生しました: {str(e)}"

    def _process_excel(self, file_path: str, operation: str) -> str:
        """Excelファイルを処理"""
        try:
            excel = pd.ExcelFile(file_path)
            sheet_names = excel.sheet_names

            if operation == "summarize":
                summary = "Excelファイル概要:\n"
                summary += f"- シート数: {len(sheet_names)}\n"
                summary += f"- シート名: {', '.join(sheet_names)}\n\n"

                # 各シートの最初の数行を表示
                for sheet in sheet_names[:3]:  # 最初の3シートのみ
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    summary += f"シート「{sheet}」の概要:\n"
                    summary += f"- レコード数: {len(df)}\n"
                    summary += f"- カラム数: {len(df.columns)}\n"
                    summary += f"- カラム名: {', '.join(df.columns)}\n\n"

                    # サンプルデータ（先頭3行）
                    summary += f"シート「{sheet}」のサンプルデータ（先頭3行）:\n"
                    summary += df.head(3).to_string() + "\n\n"

                if len(sheet_names) > 3:
                    summary += f"（他 {len(sheet_names) - 3} シートは省略）\n"

                return summary

            elif operation == "sheets":
                # シート名のリストを返す
                sheets = ", ".join(sheet_names)
                return f"Excelのシート一覧: {sheets}"

            else:
                return f"未対応の操作です: {operation}"

        except Exception as e:
            logger.error(f"Excel処理エラー: {str(e)}")
            return f"Excelファイル処理中にエラーが発生しました: {str(e)}"

    def _process_json(self, file_path: str, operation: str) -> str:
        """JSONファイルを処理"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if operation == "summarize":
                # データの概要を生成
                if isinstance(data, list):
                    summary = "JSONファイル概要（配列）:\n"
                    summary += f"- 要素数: {len(data)}\n\n"

                    # サンプルデータ（先頭の要素）
                    if len(data) > 0:
                        first_item = data[0]
                        if isinstance(first_item, dict):
                            summary += (
                                "最初の要素のキー: "
                                + ", ".join(first_item.keys())
                                + "\n\n"
                            )

                            # サンプルとして最初の要素を表示
                            summary += "最初の要素のサンプル:\n"
                            summary += json.dumps(
                                first_item, indent=2, ensure_ascii=False
                            )[:500]
                            if len(json.dumps(first_item)) > 500:
                                summary += "...(以下省略)"
                        else:
                            summary += "最初の要素: " + str(first_item)[:100] + "\n"

                elif isinstance(data, dict):
                    summary = "JSONファイル概要（オブジェクト）:\n"
                    summary += f"- キー数: {len(data.keys())}\n"
                    summary += f"- キー一覧: {', '.join(list(data.keys())[:10])}"

                    if len(data.keys()) > 10:
                        summary += f" ... 他 {len(data.keys()) - 10} 個"

                    summary += "\n\n"
                    summary += "データサンプル（一部）:\n"
                    summary += json.dumps(
                        dict(list(data.items())[:5]), indent=2, ensure_ascii=False
                    )
                    if len(data.keys()) > 5:
                        summary += "\n...(以下省略)"

                else:
                    summary = "JSONファイル概要:\n"
                    summary += f"データ型: {type(data).__name__}\n"
                    summary += f"内容: {str(data)[:200]}"
                    if len(str(data)) > 200:
                        summary += "...(以下省略)"

                return summary

            elif operation == "keys":
                # キー情報を返す
                if isinstance(data, dict):
                    keys = ", ".join(data.keys())
                    return f"JSONのキー一覧: {keys}"
                elif (
                    isinstance(data, list)
                    and len(data) > 0
                    and isinstance(data[0], dict)
                ):
                    keys = ", ".join(data[0].keys())
                    return f"JSON配列の最初の要素のキー一覧: {keys}"
                else:
                    return "キー情報を取得できません（データ形式がオブジェクトではありません）"

            else:
                return f"未対応の操作です: {operation}"

        except Exception as e:
            logger.error(f"JSON処理エラー: {str(e)}")
            return f"JSONファイル処理中にエラーが発生しました: {str(e)}"
