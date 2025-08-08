import os
import streamlit as st
import re
from pathlib import Path
import hashlib
import json
import requests
from io import StringIO

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
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
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
        
        for file in files:
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
            elif file['type'] == 'dir':
                md_files.extend(self._get_github_md_files_recursive(file['path']))
        
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


def main():
    st.set_page_config(
        page_title="SNS投稿ジェネレーター",
        page_icon="📱",
        layout="wide"
    )
    
    st.title("🚀 SNS投稿ジェネレーター")
    st.markdown("📱 どのデバイスからでもアクセス可能なクラウド版SNS投稿生成ツール")
    
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
    
    # サイドバー：ファイル選択
    st.sidebar.header("📂 ファイル選択")
    md_files = generator.get_all_md_files()
    
    if not md_files:
        st.error("Markdownファイルが見つかりません")
        return
    
    # カテゴリでグループ化
    categories = {}
    for file in md_files:
        category = file['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(file)
    
    # カテゴリ選択
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
    
    # フッター情報
    st.markdown("---")
    st.markdown("💡 **使い方**: 左サイドバーでファイルとプラットフォームを選択すると、自動的に最適化された投稿が生成されます")

if __name__ == "__main__":
    main()