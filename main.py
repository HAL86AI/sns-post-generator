#!/usr/bin/env python3
"""
Multi-platform Social Media Post Generator
ブログ記事の文体サンプルと新しいトピックをもとに、note、LinkedIn、X（Twitter）用の投稿文を自動生成
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from style_analyzer import StyleAnalyzer
from content_generator import ContentGenerator
from platform_formatter import PlatformFormatter


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数をパース"""
    parser = argparse.ArgumentParser(
        description="マルチプラットフォーム投稿文生成ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py --styleguide input/haru_writing_guide.md --snsworkflow input/sns_posting_workflow.md --articles input/note_md_files/ --theme input/topic.txt
        """
    )
    
    parser.add_argument(
        "--styleguide",
        required=True,
        help="文体ガイドファイルのパス（例: input/haru_writing_guide.md）"
    )
    
    parser.add_argument(
        "--snsworkflow", 
        required=True,
        help="SNS投稿ワークフローファイルのパス（例: input/sns_posting_workflow.md）"
    )
    
    parser.add_argument(
        "--articles",
        required=True,
        help="サンプル記事ディレクトリのパス（例: input/note_md_files/）"
    )
    
    parser.add_argument(
        "--theme",
        required=True,
        help="テーマファイルのパス（例: input/topic.txt）"
    )
    
    parser.add_argument(
        "--output",
        default="output",
        help="出力ディレクトリのパス（デフォルト: output）"
    )
    
    parser.add_argument(
        "--model",
        default="openrouter",
        choices=["openrouter", "claude", "openai", "local"],
        help="使用する生成モデル（デフォルト: openrouter）"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="詳細なログ出力"
    )
    
    return parser.parse_args()


def validate_input_files(args: argparse.Namespace) -> bool:
    """入力ファイルの存在チェック"""
    errors = []
    
    if not os.path.exists(args.styleguide):
        errors.append(f"文体ガイドファイルが見つかりません: {args.styleguide}")
    
    if not os.path.exists(args.snsworkflow):
        errors.append(f"SNSワークフローファイルが見つかりません: {args.snsworkflow}")
    
    if not os.path.exists(args.articles):
        errors.append(f"サンプル記事ディレクトリが見つかりません: {args.articles}")
    
    if not os.path.exists(args.theme):
        errors.append(f"テーマファイルが見つかりません: {args.theme}")
    
    if errors:
        for error in errors:
            print(f"エラー: {error}", file=sys.stderr)
        return False
    
    return True


def load_theme(theme_path: str) -> str:
    """テーマファイルから内容を読み込み"""
    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except Exception as e:
        print(f"エラー: テーマファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        return ""


def create_output_directory(output_dir: str) -> bool:
    """出力ディレクトリの作成"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        return True
    except Exception as e:
        print(f"エラー: 出力ディレクトリの作成に失敗しました: {e}", file=sys.stderr)
        return False


def save_generated_content(content: Dict[str, str], output_dir: str) -> bool:
    """生成されたコンテンツをファイルに保存"""
    try:
        # note記事の保存
        if 'note' in content:
            note_path = os.path.join(output_dir, "note_draft.md")
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content['note'])
            print(f"note記事案を保存しました: {note_path}")
        
        # LinkedIn投稿の保存
        if 'linkedin' in content:
            linkedin_path = os.path.join(output_dir, "linkedin_post.txt")
            with open(linkedin_path, 'w', encoding='utf-8') as f:
                f.write(content['linkedin'])
            print(f"LinkedIn投稿案を保存しました: {linkedin_path}")
        
        # Twitter投稿の保存
        if 'twitter' in content:
            twitter_path = os.path.join(output_dir, "twitter_thread.txt")
            with open(twitter_path, 'w', encoding='utf-8') as f:
                f.write(content['twitter'])
            print(f"Twitter投稿案を保存しました: {twitter_path}")
        
        return True
    except Exception as e:
        print(f"エラー: ファイルの保存に失敗しました: {e}", file=sys.stderr)
        return False


def main():
    """メイン処理"""
    print("🌟 マルチプラットフォーム投稿文生成ツール")
    print("=" * 50)
    
    # コマンドライン引数の解析
    args = parse_arguments()
    
    # 入力ファイルの検証
    if not validate_input_files(args):
        sys.exit(1)
    
    # 出力ディレクトリの作成
    if not create_output_directory(args.output):
        sys.exit(1)
    
    try:
        # 1. 文体分析の実行
        print("\n📊 文体分析を開始...")
        analyzer = StyleAnalyzer()
        
        # 文体ガイドの読み込み
        style_guide = analyzer.load_style_guide(args.styleguide)
        if args.verbose:
            print(f"文体ガイド読み込み完了: {len(style_guide)} 項目")
        
        # サンプル記事の分析
        style_profile = analyzer.analyze_sample_articles(args.articles)
        if args.verbose:
            print(f"サンプル記事分析完了: {style_profile.get('total_articles', 0)} 記事")
        
        # 2. テーマの読み込み
        print("\n📝 テーマ情報を読み込み...")
        theme_content = load_theme(args.theme)
        if not theme_content:
            print("エラー: テーマの読み込みに失敗しました")
            sys.exit(1)
        
        if args.verbose:
            print(f"テーマ: {theme_content[:100]}...")
        
        # 3. SNSワークフローの読み込み
        print("\n🔄 SNS投稿ワークフローを読み込み...")
        with open(args.snsworkflow, 'r', encoding='utf-8') as f:
            workflow_content = f.read()
        
        # 4. コンテンツ生成
        print("\n✨ コンテンツ生成を開始...")
        generator = ContentGenerator(model_type=args.model)
        formatter = PlatformFormatter()
        
        # 統合した文体情報を作成
        combined_style = {
            "style_guide": style_guide,
            "style_profile": style_profile,
            "workflow": workflow_content
        }
        
        # プラットフォーム別にコンテンツを生成
        generated_content = {}
        
        print("  📄 note記事を生成中...")
        note_content = generator.generate_note_article(
            theme=theme_content,
            style_info=combined_style,
            target_length=(800, 1500)
        )
        generated_content['note'] = formatter.format_note_article(note_content)
        
        print("  💼 LinkedIn投稿を生成中...")
        linkedin_content = generator.generate_linkedin_post(
            theme=theme_content,
            style_info=combined_style,
            target_length=(300, 600)
        )
        generated_content['linkedin'] = formatter.format_linkedin_post(linkedin_content)
        
        print("  🐦 Twitter投稿を生成中...")
        twitter_content = generator.generate_twitter_thread(
            theme=theme_content,
            style_info=combined_style,
            max_tweets=3
        )
        generated_content['twitter'] = formatter.format_twitter_thread(twitter_content)
        
        # 5. 結果の保存
        print("\n💾 結果を保存中...")
        if save_generated_content(generated_content, args.output):
            print("\n✅ すべての処理が完了しました！")
            print(f"\n出力ファイル:")
            print(f"  📄 note記事: {args.output}/note_draft.md")
            print(f"  💼 LinkedIn: {args.output}/linkedin_post.txt")
            print(f"  🐦 Twitter: {args.output}/twitter_thread.txt")
        else:
            print("\n❌ ファイルの保存でエラーが発生しました")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()