import os
import streamlit as st
import re
from pathlib import Path
import hashlib
import json
import requests
from io import StringIO
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class SocialMediaPostGenerator:
    def __init__(self, writing_folder_path=None):
        self.writing_folder = Path(writing_folder_path) if writing_folder_path else None
        self.github_repo = "HAL86AI/sns-post-generator"  # GitHubリポジトリ
        self.github_branch = "main"
        self.base_github_url = f"https://api.github.com/repos/{self.github_repo}/contents"
        self.platform_configs = {
            'Twitter': {
                'max_chars': 280,
                'hashtag_limit': 3,
                'tone': 'カジュアル、親しみやすい',
                'format': 'ツイート形式'
            },
            'LinkedIn': {
                'max_chars': 1300,
                'hashtag_limit': 5,
                'tone': 'プロフェッショナル、丁寧',
                'format': 'ビジネス記事形式'
            },
            'note': {
                'max_chars': 200,
                'hashtag_limit': 5,
                'tone': '読みやすく、親しみやすい',
                'format': 'ブログ導入文'
            }
        }

    def get_github_files(self, path=""):
        """GitHubからファイル一覧を取得"""
        try:
            url = f"{self.base_github_url}/{path}"
            
            # GitHub認証ヘッダー（オプション）
            headers = {}
            if hasattr(st, 'secrets') and 'GITHUB_TOKEN' in st.secrets:
                headers['Authorization'] = f"token {st.secrets['GITHUB_TOKEN']}"
            elif 'github_token' in st.session_state:
                headers['Authorization'] = f"token {st.session_state['github_token']}"
            
            st.info(f"デバッグ: アクセス中 - {url}")
            response = requests.get(url, headers=headers)
            st.info(f"デバッグ: レスポンスステータス - {response.status_code}")
            
            if response.status_code == 200:
                files = response.json()
                st.info(f"デバッグ: 取得ファイル数 - {len(files)}")
                return files
            else:
                st.error(f"GitHub APIエラー: {response.status_code}")
                if response.status_code == 403:
                    st.warning("💡 GitHub APIレート制限に達しています。GitHubトークンを設定すると制限が緩和されます。")
            return []
        except Exception as e:
            st.error(f"GitHub API エラー: {str(e)}")
            return []

    def get_all_md_files(self):
        """GitHubまたはローカルフォルダからすべての.mdファイルを取得"""
        md_files = []
        
        if self.writing_folder and self.writing_folder.exists():
            # ローカルファイルシステムから取得
            for root, dirs, files in os.walk(self.writing_folder):
                for file in files:
                    if file.endswith('.md'):
                        file_path = Path(root) / file
                        relative_path = file_path.relative_to(self.writing_folder)
                        md_files.append({
                            'title': file[:-3],
                            'path': str(file_path),
                            'relative_path': str(relative_path),
                            'category': str(relative_path.parent),
                            'source': 'local'
                        })
        else:
            # GitHubから取得
            md_files = self._get_github_md_files_recursive("")
        
        return md_files
    
    def _get_github_md_files_recursive(self, path):
        """GitHubから再帰的に.mdファイルを取得"""
        md_files = []
        files = self.get_github_files(path)
        st.info(f"デバッグ: パス '{path}' で {len(files)} 個のアイテムを発見")
        
        for file in files:
            st.info(f"デバッグ: ファイル - {file.get('name', 'Unknown')} (タイプ: {file.get('type', 'Unknown')})")
            if file['type'] == 'file' and file['name'].endswith('.md'):
                relative_path = file['path']
                category = '/'.join(relative_path.split('/')[:-1]) if '/' in relative_path else ''
                md_files.append({
                    'title': file['name'][:-3],
                    'path': file['download_url'],
                    'relative_path': relative_path,
                    'category': category,
                    'source': 'github'
                })
                st.info(f"デバッグ: .mdファイル追加 - {file['name']}")
            elif file['type'] == 'dir':
                st.info(f"デバッグ: フォルダを再帰検索 - {file['name']}")
                md_files.extend(self._get_github_md_files_recursive(file['path']))
        
        st.info(f"デバッグ: パス '{path}' で合計 {len(md_files)} 個の.mdファイル発見")
        return md_files

    def read_file_content(self, file_path, source='local'):
        """ファイルの内容を読み取り（ローカルまたはGitHub）"""
        try:
            if source == 'github' or file_path.startswith('http'):
                # GitHubからファイルを読み取り
                response = requests.get(file_path)
                if response.status_code == 200:
                    return response.text
                else:
                    return f"ファイル読み取りエラー: HTTP {response.status_code}"
            else:
                # ローカルファイルから読み取り
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            return f"ファイル読み取りエラー: {str(e)}"

    def extract_key_points(self, content):
        """コンテンツから主要なポイントを抽出"""
        lines = content.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # ヘッダー、リスト項目、重要そうな行を抽出
            if (line.startswith('#') or 
                line.startswith('✔️') or 
                line.startswith('・') or
                line.startswith('-') or
                '！' in line or
                '。' in line[:50]):  # 最初の50文字以内に句点があるものを重要文として扱う
                key_points.append(line)
        
        return key_points[:10]  # 上位10個まで

    def create_twitter_post(self, content, title):
        """Twitter用投稿作成"""
        key_points = self.extract_key_points(content)
        
        # タイトルから主要テーマを抽出
        main_theme = title.split('_')[0] if '_' in title else title[:20]
        
        # ハッシュタグを抽出・生成
        hashtags = []
        if 'AI' in content.upper():
            hashtags.append('#AI活用')
        if '事務' in content or '業務' in content:
            hashtags.append('#業務効率化')
        if 'SNS' in content.upper():
            hashtags.append('#SNS運用')
        
        # 3個まで制限
        hashtags = hashtags[:3]
        hashtag_text = ' '.join(hashtags)
        
        # メイン文章作成（ハッシュタグを除いた文字数で制限）
        char_limit = 280 - len(hashtag_text) - 5  # 余白を考慮
        
        if key_points:
            main_text = f"{main_theme}について、{key_points[0][:50]}..."
        else:
            main_text = f"{main_theme}について書きました！"
        
        # 文字数調整
        if len(main_text) > char_limit:
            main_text = main_text[:char_limit-3] + "..."
        
        tweet = f"{main_text}\n\n{hashtag_text}"
        
        return tweet

    def create_linkedin_post(self, content, title):
        """LinkedIn用投稿作成"""
        key_points = self.extract_key_points(content)
        
        # プロフェッショナルな導入
        intro = f"【{title.replace('_', ' ')}】\n\n"
        
        # 主要ポイントを箇条書きで
        main_content = "主要なポイント：\n"
        for i, point in enumerate(key_points[:5], 1):
            clean_point = re.sub(r'^[#\-\*\•✔️]+\s*', '', point)
            if clean_point:
                main_content += f"• {clean_point[:100]}\n"
        
        # クロージング
        closing = "\n皆様の業務効率化や働き方改善の参考になれば幸いです。"
        
        # ハッシュタグ
        hashtags = "\n\n#働き方改革 #DX #業務効率化 #AI活用 #キャリアデザイン"
        
        post = intro + main_content + closing + hashtags
        
        # 文字数制限
        if len(post) > 1300:
            post = post[:1297] + "..."
        
        return post

    def create_note_intro(self, content, title):
        """note用導入文作成"""
        key_points = self.extract_key_points(content)
        
        # タイトル改善
        clean_title = title.replace('_', ' ').replace('【', '').replace('】', '')
        
        # 導入文作成
        if key_points:
            first_point = re.sub(r'^[#\-\*\•✔️]+\s*', '', key_points[0])
            intro = f"こんにちは！\n\n{first_point[:80]}...\n\nこのような経験から、今回は{clean_title}について詳しくお話しします。"
        else:
            intro = f"こんにちは！\n\n今回は「{clean_title}」について、私の実体験を交えながらお話しします。"
        
        # ハッシュタグ
        hashtags = "\n\n#働き方 #AI #業務効率化 #キャリア #フリーランス"
        
        note_post = intro + hashtags
        
        return note_post


class AIArticleGenerator:
    def __init__(self):
        self.available_models = self.get_available_models()
        self.client = None
        self.init_openrouter()
    
    def init_openrouter(self):
        """OpenRouterクライアントを初期化"""
        if not OPENAI_AVAILABLE:
            return
        
        # Streamlit SecretsまたはAPI Key入力から取得
        api_key = None
        if hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets:
            api_key = st.secrets['OPENROUTER_API_KEY']
        elif 'openrouter_api_key' in st.session_state:
            api_key = st.session_state['openrouter_api_key']
            
        if api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
    
    def get_available_models(self):
        """利用可能なOpenRouterモデルを取得"""
        return [
            "deepseek/deepseek-r1-0528:free",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "google/gemini-pro",
            "meta-llama/llama-3.1-70b-instruct",
            "mistralai/mistral-large",
            "anthropic/claude-3-haiku",
            "openai/gpt-3.5-turbo"
        ]
    
    def generate_article(self, topic, model='deepseek/deepseek-r1-0528:free', article_type='blog', target_length=1000):
        """AIを使って記事を生成"""
        if not self.client:
            return "❌ OpenRouter APIキーが設定されていません。"
        
        # プロンプトテンプレート
        prompts = {
            'blog': f"""
あなたは経験豊富なブログライターです。以下のトピックについて、読みやすく魅力的なブログ記事を{target_length}文字程度で書いてください。

トピック: {topic}

記事の構成:
1. 魅力的な導入文
2. 主要なポイント（3-5個）
3. 具体例や体験談
4. まとめと読者へのメッセージ

読者に価値を提供し、最後まで読みたくなるような記事をお願いします。日本語で回答してください。
""",
            'note': f"""
あなたはnote記事のライターです。以下のトピックについて、noteの読者に響く記事を{target_length}文字程度で書いてください。

トピック: {topic}

記事の特徴:
- 個人的な体験や気づきを含める
- 親しみやすい文体で書く
- 読者との距離感を大切にする
- 実用的な情報を提供する

noteらしい温かみのある記事をお願いします。日本語で回答してください。
""",
            'business': f"""
あなたはビジネス記事の専門ライターです。以下のトピックについて、ビジネスパーソン向けの記事を{target_length}文字程度で書いてください。

トピック: {topic}

記事の要求:
- 論理的で説得力のある構成
- データや事例を活用
- 実践的なアドバイス
- プロフェッショナルなトーン

読者の課題解決に役立つ記事をお願いします。日本語で回答してください。
"""
        }
        
        prompt = prompts.get(article_type, prompts['blog'])
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ 記事生成エラー: {str(e)}"


def main():
    try:
        st.set_page_config(
            page_title="SNS投稿ジェネレーター",
            page_icon="📱",
            layout="wide"
        )
    except Exception as e:
        st.error(f"ページ設定エラー: {str(e)}")
    
    st.title("🚀 SNS投稿ジェネレーター")
    st.markdown("📱 どのデバイスからでもアクセス可能なクラウド版SNS投稿生成ツール")
    
    # APIキー設定エリア
    if not (hasattr(st, 'secrets') and 'OPENROUTER_API_KEY' in st.secrets):
        with st.expander("🔑 APIキー設定"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("OpenRouter APIキー（記事生成用）")
                api_key_input = st.text_input(
                    "OpenRouter APIキーを入力してください", 
                    type="password",
                    help="https://openrouter.ai でAPIキーを取得してください"
                )
                if api_key_input:
                    st.session_state['openrouter_api_key'] = api_key_input
                    st.success("✅ OpenRouter APIキーが設定されました！")
            
            with col2:
                st.subheader("GitHubトークン（レート制限回避用）")
                github_token_input = st.text_input(
                    "GitHubトークンを入力してください（オプション）",
                    type="password", 
                    help="GitHub APIレート制限を回避するため。github.com → Settings → Developer settings → Personal access tokens"
                )
                if github_token_input:
                    st.session_state['github_token'] = github_token_input
                    st.success("✅ GitHubトークンが設定されました！")
    
    # データソース選択
    st.sidebar.header("📂 データソース")
    data_source = st.sidebar.radio(
        "データの読み込み先を選択",
        options=["GitHub（クラウド）", "ローカルファイル"],
        index=0  # デフォルトはGitHub
    )
    
    # ジェネレーター初期化
    if data_source == "ローカルファイル":
        writing_folder_path = r"C:\Users\kaiga\OneDrive\1.Vibe_cording\０．Writing"
        if not os.path.exists(writing_folder_path):
            st.error("⚠️ ローカルWritingフォルダが見つかりません。GitHubデータソースを使用してください。")
            generator = SocialMediaPostGenerator()  # GitHubモード
        else:
            generator = SocialMediaPostGenerator(writing_folder_path)
    else:
        generator = SocialMediaPostGenerator()  # GitHubモード
    
    # AI記事ジェネレーター初期化
    ai_generator = AIArticleGenerator()
    
    # メインタブ選択
    tab1, tab2 = st.tabs(["📱 SNS投稿生成", "🤖 AI記事作成"])
    
    with tab1:
        # サイドバー：ファイル選択
        st.sidebar.header("📂 ファイル選択")
        try:
            md_files = generator.get_all_md_files()
            st.info(f"デバッグ: 見つかったファイル数 = {len(md_files)}")
            if md_files:
                st.info(f"最初のファイル: {md_files[0]}")
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {str(e)}")
            md_files = []
        
        if not md_files:
            st.error("Markdownファイルが見つかりません")
            st.info("GitHubリポジトリが正しく設定されているか確認してください。")
            return
        
        # カテゴリでグループ化
        categories = {}
        for file in md_files:
            category = file.get('category', 'その他')
            if category not in categories:
                categories[category] = []
            categories[category].append(file)
        
        # カテゴリ選択
        if categories:
            selected_category = st.sidebar.selectbox(
                "カテゴリを選択",
                options=list(categories.keys())
            )
            
            # ファイル選択
            category_files = categories[selected_category]
            file_titles = [f['title'] for f in category_files]
            
            selected_file_title = st.sidebar.selectbox(
                "ファイルを選択",
                options=file_titles
            )
            
            # 選択されたファイル情報取得
            selected_file = next(f for f in category_files if f['title'] == selected_file_title)
        else:
            st.error("利用可能なファイルがありません")
            return
        
        # プラットフォーム選択
        st.sidebar.header("📱 プラットフォーム選択")
        selected_platforms = st.sidebar.multiselect(
            "投稿を作成するプラットフォームを選択",
            options=['Twitter', 'LinkedIn', 'note'],
            default=['Twitter', 'LinkedIn', 'note']
        )
    
        # メインエリア
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📄 元コンテンツ")
            
            # ファイル情報表示
            st.info(f"**ファイル**: {selected_file['title']}\n**パス**: {selected_file['relative_path']}")
            
            # ファイル内容読み取り
            content = generator.read_file_content(selected_file['path'], selected_file.get('source', 'local'))
            
            # 内容をプレビュー表示（最初の500文字）
            st.text_area(
                "コンテンツプレビュー",
                value=content[:500] + "..." if len(content) > 500 else content,
                height=300,
                disabled=True
            )
        
        with col2:
            st.header("📱 生成された投稿")
            
            for platform in selected_platforms:
                st.subheader(f"{platform} 投稿")
                
                # プラットフォーム別投稿生成
                if platform == 'Twitter':
                    post_content = generator.create_twitter_post(content, selected_file['title'])
                elif platform == 'LinkedIn':
                    post_content = generator.create_linkedin_post(content, selected_file['title'])
                elif platform == 'note':
                    post_content = generator.create_note_intro(content, selected_file['title'])
                
                # 投稿内容表示
                st.text_area(
                    f"{platform}用投稿 ({len(post_content)}文字)",
                    value=post_content,
                    height=150,
                    key=f"{platform}_{selected_file['title']}"
                )
                
                # コピーボタン
                if st.button(f"{platform}投稿をクリップボードにコピー", key=f"copy_{platform}_{selected_file['title']}"):
                    st.success(f"{platform}投稿をクリップボードにコピーしました！")
    
    with tab2:
        st.header("🤖 AI記事作成")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("記事生成設定")
            
            # トピック入力
            topic = st.text_input(
                "記事のトピック・テーマを入力してください",
                placeholder="例: AI活用で業務効率化を実現する5つの方法"
            )
            
            # 記事タイプ選択
            article_type = st.selectbox(
                "記事のタイプ",
                options=['blog', 'note', 'business'],
                format_func=lambda x: {
                    'blog': '📝 ブログ記事（一般的なブログスタイル）',
                    'note': '📙 note記事（親しみやすいスタイル）', 
                    'business': '💼 ビジネス記事（プロフェッショナルスタイル）'
                }[x]
            )
            
            # AIモデル選択
            selected_model = st.selectbox(
                "AIモデルを選択",
                options=ai_generator.available_models,
                index=0  # DeepSeek R1をデフォルト
            )
            
            # 文字数設定
            target_length = st.slider(
                "目標文字数",
                min_value=500,
                max_value=3000,
                value=1500,
                step=100
            )
            
            # 記事生成ボタン
            if st.button("🚀 記事を生成", type="primary"):
                if not topic:
                    st.error("トピックを入力してください")
                else:
                    with st.spinner("AI記事を生成中..."):
                        generated_article = ai_generator.generate_article(
                            topic=topic,
                            model=selected_model,
                            article_type=article_type,
                            target_length=target_length
                        )
                        st.session_state['generated_article'] = generated_article
                        st.session_state['article_topic'] = topic
        
        with col2:
            st.subheader("生成された記事")
            
            if 'generated_article' in st.session_state:
                # 記事内容表示
                article_content = st.text_area(
                    f"記事内容 ({len(st.session_state['generated_article'])}文字)",
                    value=st.session_state['generated_article'],
                    height=400,
                    key="article_editor"
                )
                
                # 保存・コピーボタン
                col2_1, col2_2 = st.columns([1, 1])
                
                with col2_1:
                    if st.button("📋 記事をコピー"):
                        st.success("✅ 記事をクリップボードにコピーしました！")
                
                with col2_2:
                    if st.button("💾 記事を保存"):
                        # GitHubに保存する機能（今後実装）
                        st.info("💡 記事保存機能は今後実装予定です")
            
            else:
                st.info("👈 左側で設定を行い、「記事を生成」ボタンをクリックしてください")
    
    # フッター情報
    st.markdown("---")
    st.markdown("💡 **使い方**: 左サイドバーでファイルとプラットフォームを選択すると、自動的に最適化された投稿が生成されます")

if __name__ == "__main__":
    main()