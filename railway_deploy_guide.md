# 🚀 Railway デプロイガイド

## 📋 パソコンで実行する手順

### Step 1: GitHubリポジトリ作成
1. **GitHub.com** にアクセス
2. **New repository** をクリック
3. **Repository name**: `sns-post-generator`
4. **Public** を選択
5. **Create repository** をクリック

### Step 2: ローカルファイルをGitHubにアップロード

#### 方法A: GitHub Desktop使用（推奨）
1. **GitHub Desktop** をダウンロード・インストール
2. **Clone a repository from the Internet** → **URL**
3. 作成したリポジトリのURLを入力
4. ローカルフォルダを選択
5. **Fetch origin** でクローン
6. 記事作成ツールのファイルをすべてコピー
7. **Commit** → **Push** でアップロード

#### 方法B: コマンドライン使用
```bash
# 記事作成ツールのフォルダで実行
git init
git add .
git commit -m "Initial commit: SNS post generator"
git branch -M main
git remote add origin https://github.com/[ユーザー名]/sns-post-generator.git
git push -u origin main
```

### Step 3: Railway デプロイ
1. **https://railway.app/** にアクセス
2. **「Login with GitHub」** でログイン
3. **「New Project」** をクリック
4. **「Deploy from GitHub repo」** を選択
5. **sns-post-generator** リポジトリを選択
6. **自動デプロイ開始**（3-5分）

### Step 4: URL確認
- デプロイ完了後、**Deployments** タブでURLを確認
- 例：`https://sns-post-generator-production.railway.app`

## ✅ 必要なファイル（すべて準備済み）
- ✅ `Procfile` - Railway起動設定
- ✅ `requirements.txt` - 依存関係
- ✅ `runtime.txt` - Pythonバージョン
- ✅ `web_app.py` - クラウド対応済み
- ✅ その他すべてのファイル

## 🎯 デプロイ後の確認
1. **生成されたURL**にアクセス
2. **SNS投稿生成ツール**が表示される
3. **スマホからも**同じURLでアクセス可能
4. **24時間稼働**で外出先からも利用可能

## 🔧 トラブルシューティング

### デプロイが失敗する場合
- **Logs** タブでエラーを確認
- `requirements.txt` の重いライブラリを削除
- **Redeploy** ボタンで再実行

### アクセスできない場合
- URLが正しいか確認
- **Settings** → **Domains** でカスタムドメイン設定

## 💰 料金について
- **無料枠**: 月500時間（約20日分）
- **超過**: $5/月程度
- **個人利用**: 無料枠で十分

---

**準備完了！GitHubへのアップロードから始めてください** 🚀