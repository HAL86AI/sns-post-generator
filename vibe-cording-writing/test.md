# Gemini CLI エラーまとめ (Windows環境)

## よくあるエラーと解決策

1. **WSL2環境でのlocalhost問題**
   - 現象: 認証時に「このサイトにアクセスできません」エラー
   - 原因: WSL2とWindowsでlocalhostの参照先が異なる
   - 解決策: ポートフォワーディングの設定が必要

2. **環境変数エラー**
   - `GOOGLE_CLOUD_PROJECT`が未設定
   - 解決策: 正しいプロジェクトIDを設定

3. **認証トークン問題**
   - トークンの有効期限切れ
   - 解決策: `gcloud auth login`で再認証

4. **環境差による問題**
   - Python/Node.jsのバージョン不一致
   - プロキシ設定の違い

## 詳細技術情報

### 1. システム要件
- **Node.js**: バージョン18以上必須
- **Python**: 3.8以上推奨 (一部機能で必要)
- **WSL2**: メモリ割り当て4GB以上推奨

### 2. ネットワーク設定
```bash
# プロキシ設定確認
netsh winhttp show proxy

# ローカルポート開放 (管理者権限)
netsh advfirewall firewall add rule name="Gemini CLI" dir=in action=allow protocol=TCP localport=8080
```

### 3. 詳細ログ取得
```bash
gemini --log-level=DEBUG
```

### 4. 環境検証コマンド
```bash
# 依存関係チェック
gemini doctor

# 認証状態確認
gcloud auth list
```

## 具体的な解決手順

### 1. WSL2 localhost問題の解決
```bash
# WSL2側で実行 (ポートフォワーディング設定)
echo "Forwarding port 8080 to Windows..."
wsl --shutdown
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$(hostname).local

# Windowsのhostsファイルに追記 (管理者権限)
127.0.0.1	localhost $(hostname).local
```

### 2. 環境変数の永続的設定
```powershell
# システム全体に設定
[System.Environment]::SetEnvironmentVariable('GOOGLE_CLOUD_PROJECT','YOUR_PROJECT_ID','Machine')

# 現在のセッションのみに設定
$env:GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
```

### 3. 認証トークン更新
```bash
# 既存の認証をクリア
gcloud auth revoke

# 新しい認証フロー開始
gcloud auth login --no-launch-browser

# 表示されたURLを手動で開き、コードを入力
```

### 4. バージョン管理
```bash
# Node.jsバージョン切り替え (nvm使用)
nvm install 18.17.1
nvm use 18.17.1

# Python仮想環境作成
python -m venv .venv
.venv\\Scripts\\activate
```

## 参考リンク
- [WSL2でGemini CLIを試す（Qiita）](https://qiita.com/ryu-ki/items/bb1a0619e05431c05447)
- [Gemini CLI初期設定のトラブル（Future Core Partners）](https://futurecorepartners.jp/gemini-cli/)
- [Windowsセットアップ徹底解説(Qiita)](https://qiita.com/automation2025/items/1345a68a3a0c3ee51f15)
- [公式トラブルシューティングガイド](https://cloud.google.com/gemini/docs/troubleshooting)