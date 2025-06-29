import asyncio
import os
import streamlit as st
import httpx
import json
from typing import List, Dict, Any
from strands import Agent
from strands.models import BedrockModel

# ページ設定
st.set_page_config(
    page_title="Microsoft Azure 資格勉強エージェント",
    page_icon="📚",
    initial_sidebar_state="expanded",
    menu_items={'About': "Microsoft Learn MCPを使ったAzure資格勉強サポートエージェントです。"}
)

# 環境変数の設定
if "aws" in st.secrets:
    os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY_ID"]
    os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_ACCESS_KEY"]
    os.environ["AWS_DEFAULT_REGION"] = st.secrets["aws"]["AWS_DEFAULT_REGION"]


class HTTPMCPClient:
    """Microsoft Learning MCP用のHTTPクライアント"""
    
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self._tools_cache = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.client.aclose())
    
    async def list_tools_async(self) -> List[Dict[str, Any]]:
        """利用可能なツールのリストを取得"""
        if self._tools_cache:
            return self._tools_cache
        
        try:
            response = await self.client.get(
                f"{self.base_url}/tools",
                headers=self.headers
            )
            response.raise_for_status()
            
            # Microsoft Learning MCPの想定されるツールを定義
            # 実際のAPIレスポンスに応じて調整が必要
            tools = [
                {
                    "name": "search_docs",
                    "description": "Microsoft Learn ドキュメントを検索します",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "検索クエリ"
                            },
                            "product": {
                                "type": "string", 
                                "description": "Azure サービス名（オプション）"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_certification_info",
                    "description": "Azure資格認定の情報を取得します",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "certification_code": {
                                "type": "string",
                                "description": "資格コード（例：AZ-900, AZ-104）"
                            }
                        },
                        "required": ["certification_code"]
                    }
                },
                {
                    "name": "get_learning_path",
                    "description": "指定した資格のラーニングパスを取得します",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "certification_code": {
                                "type": "string", 
                                "description": "資格コード"
                            }
                        },
                        "required": ["certification_code"]
                    }
                }
            ]
            
            self._tools_cache = tools
            return tools
            
        except httpx.RequestError as e:
            st.error(f"Microsoft Learning MCPとの接続に失敗しました: {e}")
            return []
        except Exception as e:
            st.error(f"ツールリストの取得に失敗しました: {e}")
            return []
    
    def list_tools_sync(self) -> List[Dict[str, Any]]:
        """同期版ツールリスト取得"""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.list_tools_async())
        finally:
            loop.close()
    
    async def call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """ツールを非同期で実行"""
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/{tool_name}",
                json={"arguments": arguments},
                headers=self.headers
            )
            response.raise_for_status()
            
            # 実際のMicrosoft Learning MCPの応答形式に応じて調整
            result = response.json()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Microsoft Learning MCP - {tool_name}の結果:\n{json.dumps(result, ensure_ascii=False, indent=2)}"
                    }
                ]
            }
            
        except httpx.RequestError as e:
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": f"エラー: Microsoft Learning MCPとの通信に失敗しました: {e}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"エラー: {e}"
                    }
                ]
            }

# メインエリア
st.title("Microsoft Azure 資格勉強エージェント 📚")
st.markdown("Microsoft Learn MCPを使用してAzure資格取得をサポートします！[Strands Agents SDK](https://aws.amazon.com/jp/blogs/news/introducing-strands-agents-an-open-source-ai-agents-sdk/) 搭載")

# サンプル質問の選択肢
sample_questions = [
    "AZ-900 Azure Fundamentalsの概要と試験範囲を教えて",
    "AZ-104 Azure Administratorに必要なスキルは何ですか？",
    "Azure Storage Accountの種類と用途を説明して", 
    "Azure Virtual Machineのサイズと価格について",
    "Azure Active Directoryとは何ですか？",
    "カスタム質問を入力"
]

selected_question = st.selectbox("質問を選択してください", sample_questions)

if selected_question == "カスタム質問を入力":
    question = st.text_area("質問を入力", "", height=80)
else:
    question = st.text_area("質問を入力", selected_question, height=80)

# サイドバー
with st.sidebar:
    st.title("Microsoft Learning MCP 設定")
    
    # Microsoft Learning MCP の固定設定
    st.info("🔗 **Microsoft Learning MCP**\nhttps://learn.microsoft.com/api/mcp")
    
    # Bedrockモデル設定
    st.title("Bedrockモデル設定")
    bedrock_model = st.selectbox(
        "使用するBedrockモデル",
        [
            "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            "us.anthropic.claude-3-haiku-20240307-v1:0"
        ],
        index=0
    )
    
    st.title("Azure資格情報")
    st.markdown("""
    **主要なAzure資格:**
    - 🟢 **AZ-900**: Azure Fundamentals
    - 🔵 **AZ-104**: Azure Administrator Associate
    - 🔵 **AZ-204**: Azure Developer Associate
    - 🔵 **AZ-305**: Azure Solutions Architect Expert
    - 🟡 **AI-900**: AI Fundamentals
    - 🟡 **DP-900**: Data Fundamentals
    """)
    
    st.text("")
    st.markdown("このアプリについて [GitHub](https://github.com/Tomodo1773/strands-mcp-agent)")


def create_microsoft_learning_mcp_client():
    """Microsoft Learning MCP HTTP クライアントを作成"""
    return HTTPMCPClient(
        base_url="https://learn.microsoft.com/api/mcp",
        headers={
            "User-Agent": "Azure-Certification-Study-Agent/1.0"
        }
    )


def create_agent_with_microsoft_mcp(bedrock_model_id: str):
    """Microsoft Learning MCPを使用してエージェントを作成"""
    client = create_microsoft_learning_mcp_client()
    
    # ツールリストを取得
    tools = client.list_tools_sync()
    
    return Agent(
        model=BedrockModel(
            model_id=bedrock_model_id,
            timeout=60
        ),
        tools=tools
    ), client


def extract_tool_info(chunk):
    """チャンクからツール情報を抽出"""
    event = chunk.get('event', {})
    if 'contentBlockStart' in event:
        tool_use = event['contentBlockStart'].get('start', {}).get('toolUse', {})
        return tool_use.get('toolUseId'), tool_use.get('name')
    return None, None


def extract_text(chunk):
    """チャンクからテキストを抽出"""
    if text := chunk.get('data'):
        return text
    elif delta := chunk.get('delta', {}).get('text'):
        return delta
    return ""


async def stream_response(agent, question, container):
    """レスポンスをストリーミング表示"""
    text_holder = container.empty()
    buffer = ""
    shown_tools = set()
    
    async for chunk in agent.stream_async(question):
        if isinstance(chunk, dict):
            # ツール実行を検出して表示
            tool_id, tool_name = extract_tool_info(chunk)
            if tool_id and tool_name and tool_id not in shown_tools:
                shown_tools.add(tool_id)
                if buffer:
                    text_holder.markdown(buffer)
                    buffer = ""
                container.info(f"🔧 **{tool_name}** ツールを実行中...")
                text_holder = container.empty()
            
            # テキストを抽出して表示
            if text := extract_text(chunk):
                buffer += text
                text_holder.markdown(buffer)
    
    # 最終表示
    if buffer:
        text_holder.markdown(buffer)


# ボタンを押したら生成開始
if st.button("🚀 Azure資格について質問する"):
    if not question.strip():
        st.error("質問を入力してください。")
    else:
        with st.spinner("Microsoft Learning MCPで調べています…"):
            try:
                # Microsoft Learning MCPクライアントとエージェントを作成
                agent, mcp_client = create_agent_with_microsoft_mcp(bedrock_model)
                container = st.container()
                
                # Azure資格勉強に特化したプロンプトを追加
                enhanced_question = f"""
あなたはMicrosoft Azure資格取得を支援する専門エージェントです。
Microsoft Learning MCPを使用して、以下の質問に回答してください。

質問: {question}

回答時の注意点:
- Azure資格（AZ-900, AZ-104等）に関連する情報を含める
- 実践的な学習方法やTipsを提供する
- 関連するMicrosoft Learnのドキュメントを参照する
- 初心者にも分かりやすく説明する
"""
                
                # 非同期実行
                loop = asyncio.new_event_loop()
                loop.run_until_complete(stream_response(agent, enhanced_question, container))
                loop.close()
                
            except asyncio.TimeoutError:
                st.error("⏰ タイムアウトエラーが発生しました。もう一度お試しください。")
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.info("💡 質問を簡潔にしてお試しください。Microsoft Learning MCPとの接続に問題がある可能性があります。")
            finally:
                # MCPクライアントを終了
                try:
                    mcp_client.__exit__(None, None, None)
                except:
                    pass