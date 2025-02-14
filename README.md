# タスク管理エージェント

このプロジェクトは、タスク管理とGoogle Calendarとの連携を行うエージェントです。

## セットアップ

### 必要条件
- Python 3.13以上
- Poetry（依存関係管理ツール）

### 主要な依存関係
- google-api-python-client: Google Calendar APIクライアント
- pydantic: データバリデーション
- pyyaml: YAML処理
- google-auth-oauthlib: Google認証
- google-auth-httplib2: Google認証

### インストール手順

1. リポジトリをクローンします：
```bash
git clone [repository-url]
cd TaskManageerAgent
```

2. Poetryを使用して依存関係をインストールします：
```bash
poetry install
```

3. 仮想環境を有効化します：
```bash
poetry shell
```

### Google Calendar APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセスし、新しいプロジェクトを作成します。

2. Google Calendar APIを有効化します：
   - APIとサービス > ライブラリから「Google Calendar API」を検索し、有効化します。

3. 認証情報を作成します：
   - APIとサービス > 認証情報から「認証情報を作成」をクリックします。
   - OAuth 2.0 クライアントIDを選択します。
   - アプリケーションの種類を「デスクトップアプリケーション」に設定します。
   - 作成された`credentials.json`をプロジェクトのルートディレクトリに配置します。

4. 初回実行時に、ブラウザが開いてGoogle認証が要求されます。認証後、`token.pickle`が自動的に生成されます。

##プロンプトサンプル
###タスクの登録
```
リポジトリ整理作業
フロント，バックエンド，インフラと別れてるリポジトリをまとめて管理しやすいようにする
期限は今日中，優先度高め，カテゴリはhogehoge
```
###スケジュール作成
```
今日の予定を作成
13:00から22:00で
```
 スケジュールの登録
```
カレンダー追加しといて
```
