# 🚀 SNS投稿ジェネレーター

📱 **どのデバイスからでもアクセス可能**なクラウド対応SNS投稿生成ツール

WritingフォルダのMarkdownファイルから各SNSプラットフォーム（Twitter、LinkedIn、note）向けの投稿を自動生成します。

## ✨ 主な機能

- 📱 **マルチデバイス対応**: PC・スマホ・タブレットからアクセス可能
- ☁️ **クラウドストレージ**: GitHubまたはローカルファイルから読み込み
- 🎯 **プラットフォーム別最適化**:
  - Twitter: 280文字制限、ハッシュタグ3個まで
  - LinkedIn: 1300文字程度、プロフェッショナルなトーン  
  - note: 導入文形式、読みやすいスタイル
- 🤖 **自動要約**: 長文コンテンツから重要ポイントを抽出
- 📊 **リアルタイムプレビュー**: 文字数カウント付き投稿プレビュー

## 🌐 クラウドデプロイ（推奨）

### Streamlit Cloud で無料デプロイ

1. **GitHubリポジトリ作成**:
   ```bash
   python setup_github.py  # WritingコンテンツをGitHub用に準備
   ```

2. **Streamlit Cloud**:
   - [Streamlit Cloud](https://streamlit.io/cloud)でアカウント作成
   - GitHubリポジトリを接続
   - `social_media_post_generator.py`を指定してデプロイ

3. **アクセス**: 生成されたURLでどこからでもアクセス可能！

## 💻 ローカルセットアップ

1. **ライブラリインストール**:
   ```bash
   pip install -r requirements.txt
   ```

2. **アプリ起動**:
   ```bash
   streamlit run social_media_post_generator.py
   ```

3. **ブラウザアクセス**: `http://localhost:8501`

## 📖 使い方

1. **データソース選択**: GitHub（クラウド）またはローカルファイル
2. **ファイル選択**: 左サイドバーでカテゴリとファイルを選択
3. **プラットフォーム選択**: 投稿を作成したいSNSを選択  
4. **投稿生成**: 自動的に最適化された投稿が生成
5. **コピー**: ボタンクリックで投稿内容をクリップボードにコピー

## 📁 対応形式

- **入力**: Markdownファイル（.md）
- **出力**: プラットフォーム別最適化テキスト
- **ストレージ**: ローカルファイル・GitHub

## ⚙️ カスタマイズ

`social_media_post_generator.py`の`platform_configs`と`github_repo`設定を編集可能。

## 🔧 GitHub設定

WritingコンテンツをGitHubで管理する場合：

1. `setup_github.py`を実行
2. GitHubで`vibe-cording-writing`リポジトリを作成  
3. 生成されたフォルダをGitHubにプッシュ
4. アプリでGitHubモードを選択

これでどこからでもコンテンツにアクセス可能になります！