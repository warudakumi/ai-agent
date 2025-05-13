import json
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from loguru import logger


# 状態の型定義
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    current_thought: str
    tool_calls: List[Dict[str, Any]]
    tools_output: List[Dict[str, Any]]
    final_response: Optional[str]
    error: Optional[str]


def create_workflow(agent, tools):
    """エージェントワークフローを作成する"""

    # 状態グラフの作成
    workflow = StateGraph(AgentState)

    # ステップ1: 入力処理
    def process_input(state: AgentState) -> AgentState:
        """
        ユーザー入力を処理するノード

        入力メッセージを解析し、状態を初期化する。
        """
        logger.info("ステップ1: 入力処理")
        try:
            # 最新のユーザーメッセージを取得
            last_user_message = None
            for msg in reversed(state["messages"]):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break

            if not last_user_message:
                raise ValueError("ユーザーメッセージが見つかりません")

            # 入力処理ログ
            logger.debug(f"入力メッセージ: {last_user_message[:100]}...")

            # 状態の初期化
            state["current_thought"] = ""
            state["tool_calls"] = []
            state["tools_output"] = []
            state["final_response"] = None
            state["error"] = None

            return state

        except Exception as e:
            logger.error(f"入力処理エラー: {str(e)}")
            state["error"] = f"入力処理中にエラーが発生しました: {str(e)}"
            return state

    # ステップ2: 思考生成
    def generate_thought(state: AgentState) -> AgentState:
        """
        エージェントの思考を生成するノード

        LLMを使用して、ユーザーの質問に対する思考過程を生成する。
        """
        logger.info("ステップ2: 思考生成")

        if state.get("error"):
            return state

        try:
            # メッセージ履歴からプロンプトを構築
            prompt_messages = []

            # システムメッセージ
            system_content = """あなたはAIエージェントです。
            ユーザーからの質問に丁寧に回答し、必要に応じて適切なツールを使用してください。
            ユーザーの意図を理解し、段階的に考えて最適な解決策を提供してください。
            
            使用可能なツール:
            1. web_search - ウェブ上で情報を検索します
            2. file_processor - アップロードされたファイルを処理します
            3. document_checker - アップロードされたドキュメントをチェックします
            
            問題解決の手順:
            1. 問題を明確に理解する
            2. 必要な情報が何かを特定する
            3. 適切なツールを選択して使用する
            4. 結果を分析して最終的な回答を作成する
            
            考え方を詳細に説明し、ユーザーが理解しやすいように情報を整理してください。
            """

            prompt_messages.append(SystemMessage(content=system_content))

            # 会話履歴を追加
            for msg in state["messages"]:
                if msg["role"] == "user":
                    prompt_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    prompt_messages.append(AIMessage(content=msg["content"]))
                elif msg["role"] == "system":
                    prompt_messages.append(SystemMessage(content=msg["content"]))

            # 思考生成用の追加指示
            think_instruction = """
            以下の質問について考えてみましょう。回答する前に、段階的に考えを整理してください。
            必要に応じて、利用可能なツールを使用することを検討してください。
            """

            prompt_messages.append(SystemMessage(content=think_instruction))

            # LLMで思考生成
            thought_response = agent.invoke(prompt_messages)

            # 思考を状態に保存
            state["current_thought"] = thought_response.content

            # 思考内容のログを記録
            logger.debug(f"生成された思考:\n{thought_response.content}")

            return state

        except Exception as e:
            logger.error(f"思考生成エラー: {str(e)}")
            state["error"] = f"思考生成中にエラーが発生しました: {str(e)}"
            return state

    # ステップ3: ツール選択と実行
    def execute_tools(state: AgentState) -> AgentState:
        """
        必要なツールを選択して実行するノード

        思考に基づいて適切なツールを選択・実行し、結果を記録する。
        """
        logger.info("ステップ3: ツール選択と実行")

        if state.get("error"):
            return state

        if not state.get("current_thought"):
            state["error"] = "思考が生成されていません"
            return state

        try:
            # ツール呼び出し判断用のプロンプト
            tool_selection_prompt = [
                SystemMessage(
                    content=f"""
                あなたは思考を分析し、必要なツールを特定します。
                
                利用可能なツール:
                {json.dumps([{"name": tool.name, "description": tool.description} for tool in tools], ensure_ascii=False)}
                
                もしツールを使用する必要があれば、以下の形式でJSONを出力してください:
                ```json
                [
                  {{
                    "tool": "ツール名",
                    "input": "ツールへの入力",
                    "reason": "このツールを使用する理由"
                  }},
                  ...
                ]
                ```
                
                ツールを使用する必要がなければ、空の配列を返してください: []
                """
                ),
                HumanMessage(
                    content=f"""
                ユーザーの質問:
                {state["messages"][-1]["content"]}
                
                私の思考:
                {state["current_thought"]}
                
                必要なツールを特定し、JSONフォーマットで出力してください。
                """
                ),
            ]

            # ツール選択の応答
            tool_selection_response = agent.invoke(tool_selection_prompt)
            tool_selection_text = tool_selection_response.content

            # ツール選択のログを記録
            logger.debug(f"ツール選択応答:\n{tool_selection_text}")

            # JSON部分を抽出
            json_start = tool_selection_text.find("```json")
            json_end = tool_selection_text.rfind("```")

            tool_calls = []

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_str = tool_selection_text[json_start + 7 : json_end].strip()
                try:
                    tool_calls = json.loads(json_str)
                except json.JSONDecodeError:
                    logger.warning(f"JSONパースエラー: {json_str}")
                    tool_calls = []
            else:
                # JSON部分がない場合は、テキスト全体をパースしてみる
                try:
                    tool_calls = json.loads(tool_selection_text)
                except json.JSONDecodeError:
                    logger.warning(
                        f"テキスト全体のJSONパースエラー: {tool_selection_text}"
                    )
                    tool_calls = []

            # ツールの実行
            tools_output = []

            if tool_calls and isinstance(tool_calls, list):
                state["tool_calls"] = tool_calls
                logger.debug(
                    f"選択されたツール: {json.dumps(tool_calls, ensure_ascii=False)}"
                )

                for tool_call in tool_calls:
                    tool_name = tool_call.get("tool")
                    tool_input = tool_call.get("input")

                    # ツールを探す
                    tool = next((t for t in tools if t.name == tool_name), None)

                    if tool and tool_input:
                        try:
                            logger.debug(f"ツール実行: {tool_name}, 入力: {tool_input}")
                            # ツールを実行
                            tool_output = tool._run(tool_input)

                            # 結果を記録
                            tools_output.append(
                                {
                                    "tool": tool_name,
                                    "input": tool_input,
                                    "output": tool_output,
                                }
                            )

                            logger.debug(
                                f"ツール実行結果: {tool_name} -> {tool_output[:200]}..."
                            )

                        except Exception as e:
                            logger.error(f"ツール実行エラー: {str(e)}")
                            tools_output.append(
                                {
                                    "tool": tool_name,
                                    "input": tool_input,
                                    "output": f"エラー: {str(e)}",
                                }
                            )

            state["tools_output"] = tools_output

            return state

        except Exception as e:
            logger.error(f"ツール実行エラー: {str(e)}")
            state["error"] = f"ツール実行中にエラーが発生しました: {str(e)}"
            return state

    # ステップ4: 最終応答生成
    def generate_response(state: AgentState) -> AgentState:
        """
        最終的な応答を生成するノード

        思考プロセスとツール実行結果を使用して、ユーザーへの最終応答を生成する。
        """
        logger.info("ステップ4: 最終応答生成")

        if state.get("error"):
            return state

        try:
            # 応答生成用のプロンプト
            response_prompt = [
                SystemMessage(
                    content="""
                あなたはAIエージェントです。
                これまでの思考過程とツール実行結果を踏まえて、ユーザーへの最終的な回答を作成してください。
                
                回答は以下の特徴を持つものにしてください：
                - 簡潔明瞭で理解しやすい
                - ユーザーの質問に直接答える
                - 重要な情報を整理して提示する
                - 専門用語がある場合は適切に説明する
                - 丁寧かつフレンドリーな口調
                
                ツールの実行結果がある場合は、それを適切に要約・解釈して回答に含めてください。
                """
                ),
                HumanMessage(
                    content=f"""
                ユーザーの質問:
                {state["messages"][-1]["content"]}
                
                私の思考過程:
                {state["current_thought"]}
                
                ツール実行結果:
                {json.dumps(state["tools_output"], ensure_ascii=False, indent=2) if state["tools_output"] else "ツールは使用されませんでした"}
                
                以上を踏まえて、最終的な回答を作成してください。
                """
                ),
            ]

            # 最終応答の生成
            response = agent.invoke(response_prompt)

            # 応答内容のログを記録
            logger.debug(f"生成された最終応答:\n{response.content}")

            # 応答を状態に保存
            state["final_response"] = response.content

            return state

        except Exception as e:
            logger.error(f"応答生成エラー: {str(e)}")
            state["error"] = f"応答生成中にエラーが発生しました: {str(e)}"
            return state

    # ノードの追加
    workflow.add_node("process_input", process_input)
    workflow.add_node("generate_thought", generate_thought)
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("generate_response", generate_response)

    # エッジの定義
    workflow.add_edge(START, "process_input")
    workflow.add_edge("process_input", "generate_thought")
    workflow.add_edge("generate_thought", "execute_tools")
    workflow.add_edge("execute_tools", "generate_response")
    workflow.add_edge("generate_response", END)

    # コンパイル
    return workflow.compile()
