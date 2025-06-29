# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

このリポジトリは「Microsoft Azure 資格勉強エージェント」というWebアプリケーションで、AWS発のOSS「Strands Agents SDK」を使用して構築されています。Microsoft Learning MCPと連携し、Azure資格取得をサポートするStreamlitベースのインターフェースを提供します。

## 一般的なコマンド

### アプリケーションの実行
```bash
# ローカルでStreamlitアプリを起動
streamlit run main.py

# デバッグモードで実行
streamlit run main.py --logger.level=debug
```

### 依存関係の管理
```bash
# 依存関係のインストール
pip install -r requirements.txt
```

### AWS認証設定
```bash
# AWS CLIで認証情報を設定
aws configure

# または環境変数で設定
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_DEFAULT_REGION="us-west-2"
```

## コードアーキテクチャと構造

### ファイル構成
- `main.py` - Streamlitアプリケーションのメインファイル
- `requirements.txt` - Python依存関係の定義
- `.github/workflows/claude.yml` - Claude Code GitHub Actionの設定

### 主要なコンポーネント

#### 1. Streamlitアプリケーション (`main.py`)
- **UI構成**:
  - メインエリア: Azure資格関連の質問選択肢と入力フィールド
  - サイドバー: Bedrockモデル選択とAzure資格情報表示
  
- **主要なクラス**:
  - `HTTPMCPClient`: Microsoft Learning MCP用HTTPクライアント
  
- **主要な関数**:
  - `create_microsoft_learning_mcp_client()`: Microsoft Learning MCPクライアントの作成
  - `create_agent_with_microsoft_mcp()`: Microsoft Learning MCPエージェントの作成
  - `stream_response()`: 非同期でレスポンスをストリーミング表示
  - `extract_tool_info()`: ツール実行情報の抽出
  - `extract_text()`: チャンクからテキストの抽出

#### 2. 技術スタック
- **フレームワーク**: Streamlit（Webインターフェース）
- **AIエージェント**: Strands Agents SDK
- **LLMプロバイダー**: AWS Bedrock（Claudeモデル）
- **MCPプロトコル**: HTTPクライアント経由でMicrosoft Learning MCPと通信
- **HTTP通信**: httpx（非同期HTTPクライアント）
- **固定MCP**: Microsoft Learning MCP (https://learn.microsoft.com/api/mcp)

#### 3. Azure資格勉強機能
- **対象資格**: AZ-900, AZ-104, AZ-204, AZ-305, AI-900, DP-900
- **利用可能ツール**:
  - `search_docs`: Microsoft Learn ドキュメント検索
  - `get_certification_info`: Azure資格認定情報取得
  - `get_learning_path`: 学習パス取得

#### 4. 認証とシークレット管理
- ローカル開発: AWS環境変数または~/.aws/credentials
- Streamlit Community Cloud: st.secretsを使用
  - AWS認証情報
  - Langfuseトレース設定（オプション）

## 重要な注意点

1. **Microsoft Learning MCP接続**: HTTPプロトコルでMicrosoft Learning MCPに固定接続
2. **非同期処理**: asyncioとhttpxを使用してストリーミングレスポンスを実装
3. **エラーハンドリング**: HTTP接続エラーやBedrock認証エラーに注意
4. **デプロイ**: Streamlit Community Cloudへのデプロイ時はシークレット設定が必須
5. **Azure資格特化**: AZ-900からAZ-305まで主要Azure資格をサポート

## GitHub Actions

Claude Code Actionが設定されており、以下のトリガーで動作:
- Issue/PRコメントに`@claude`を含む場合
- Issue本文/タイトルに`@claude`を含む場合

## 開発のヒント

1. **Microsoft Learning MCP**: https://learn.microsoft.com/api/mcp への接続は固定設定
2. **Bedrockモデル**: Claude 3.5 Sonnet、Claude 3 Haiku等の利用可能モデルから選択
3. **ツール実行の可視化**: Azure資格勉強に特化したツール実行を表示
4. **HTTPクライアント**: httpxを使用した非同期HTTP通信でパフォーマンス向上
5. **Azure資格情報**: サイドバーに主要Azure資格の一覧を表示