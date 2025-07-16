# マルチプラットフォーム投稿文生成ツール

あなたの文体でnote・LinkedIn・Twitter（X）の投稿を自動生成するWebアプリケーションです。

## 🌟 特徴

- **文体学習**: あなたの文体ガイドとサンプル記事から文体を学習
- **マルチプラットフォーム対応**: note、LinkedIn、Twitterに最適化された投稿を同時生成
- **オシャレなUI**: モダンでシンプルなWebインターフェース
- **ファイルアップロード**: 文体ガイドやサンプル記事をファイルから読み込み
- **リアルタイム文字数カウント**: プラットフォーム別の文字数制限に対応
- **フォールバック機能**: APIが利用できない場合のテンプレート生成

## 🚀 使用方法

### Webアプリ版（推奨）

1. **依存関係のインストール**
   ```bash
   pip install flask flask-cors markdown
   ```

2. **Webアプリ起動**
   ```bash
   python web_app.py
   ```

3. **ブラウザでアクセス**
   ```
   http://localhost:5000
   ```

4. **投稿文生成**
   - テーマを入力
   - 文体ガイドを入力（またはファイルアップロード）
   - SNS投稿方針を入力
   - サンプル記事をアップロード（任意）
   - 「投稿文を生成する」ボタンをクリック

### CLI版

```bash
python main.py --styleguide input/haru_writing_guide.md --snsworkflow input/sns_posting_workflow.md --articles input/note_md_files/ --theme input/topic.txt
```

## 📁 ファイル構成

```
project/
├── main.py                    # CLI版メインプログラム
├── web_app.py                 # Webアプリ版メインプログラム
├── requirements.txt           # 依存関係
├── src/
│   ├── style_analyzer.py      # 文体分析モジュール
│   ├── content_generator.py   # コンテンツ生成モジュール
│   └── platform_formatter.py # プラットフォーム別フォーマット
├── templates/
│   └── index.html            # Webアプリテンプレート
├── static/
│   ├── css/style.css         # スタイルシート
│   └── js/app.js             # JavaScript
├── input/                     # 入力ファイル
│   ├── haru_writing_guide.md
│   ├── sns_posting_workflow.md
│   ├── topic.txt
│   └── note_md_files/
└── output/                    # 出力ファイル
    ├── note_draft.md
    ├── linkedin_post.txt
    └── twitter_thread.txt
```

## 🎨 UI特徴

- **グラデーション背景**: モダンな紫系グラデーション
- **ガラスモーフィズム**: 半透明でぼかし効果のあるカード
- **レスポンシブデザイン**: モバイルデバイス対応
- **リアルタイムフィードバック**: 文字数カウント、バリデーション
- **ドラッグ&ドロップ**: ファイルアップロード
- **アニメーション**: スムーズな画面遷移

## 🔧 生成モデル

1. **テンプレート（推奨）**: APIキー不要、即座に利用可能
2. **Claude API**: 高品質な生成（要APIキー）
3. **OpenAI API**: GPT-3.5/4による生成（要APIキー）
4. **ローカルモデル**: transformersライブラリ使用

## 📝 出力形式

### note記事
- 800-1500文字
- マークダウン形式
- 見出し構造付き
- 体験談重視

### LinkedIn投稿
- 300-600文字
- ビジネストーン
- ハッシュタグ付き
- 結論先出し

### Twitter投稿
- 140文字×1-3連投
- 番号付きスレッド
- エンゲージメント重視
- ハッシュタグ付き

## 🛠️ 技術スタック

- **バックエンド**: Python, Flask
- **フロントエンド**: HTML5, CSS3, JavaScript (ES6+)
- **スタイル**: CSS Grid, Flexbox, CSS Variables
- **AI**: OpenAI API, Anthropic Claude API, Transformers
- **ファイル処理**: Markdown, JSON

## 📋 必要な入力

1. **テーマ**: 投稿したい内容やキーワード
2. **文体ガイド**: あなたの執筆スタイルの説明
3. **SNS投稿方針**: プラットフォーム別の投稿戦略
4. **サンプル記事（任意）**: 過去の記事からの文体学習

## 🔒 セキュリティ

- ファイルアップロード制限（.txt, .mdのみ）
- XSS対策
- CSRF対策
- ファイルサイズ制限（16MB）
- 一時ファイルの自動削除

## 🎯 使用例

「営業の自動化」というテーマで、フレンドリーで実体験重視の文体を学習し、各プラットフォーム向けに最適化された投稿文を生成。

## 🚨 注意事項

- API使用時は適切なAPIキーの設定が必要
- 生成されたコンテンツは手動での確認・調整を推奨
- 個人情報や機密情報の入力は避ける
- 商用利用時は各プラットフォームの利用規約を確認

## 📞 サポート

問題が発生した場合は、ブラウザの開発者ツールでエラーログを確認してください。