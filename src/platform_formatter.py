"""
Platform Formatter Module for formatting content according to platform specifications
"""

import re
import textwrap
from typing import List, Dict, Optional
from datetime import datetime


class PlatformFormatter:
    """プラットフォーム別のフォーマット調整を行う"""
    
    def __init__(self):
        self.platform_specs = {
            'note': {
                'max_title_length': 100,
                'preferred_paragraphs': 3,
                'use_emojis': True,
                'use_headers': True
            },
            'linkedin': {
                'max_length': 3000,
                'preferred_length': (300, 600),
                'use_hashtags': True,
                'professional_tone': True
            },
            'twitter': {
                'max_tweet_length': 280,
                'preferred_tweet_length': 140,
                'max_thread_length': 10,
                'use_hashtags': True,
                'use_thread_numbers': True
            }
        }
    
    def format_note_article(self, content: str) -> str:
        """note記事のフォーマット調整"""
        # 基本的なクリーニング
        formatted_content = self._clean_content(content)
        
        # タイトルの調整
        formatted_content = self._format_note_title(formatted_content)
        
        # 段落の調整
        formatted_content = self._format_note_paragraphs(formatted_content)
        
        # 見出しの調整
        formatted_content = self._format_note_headers(formatted_content)
        
        # 絵文字の調整
        formatted_content = self._adjust_emoji_usage(formatted_content, platform='note')
        
        # メタ情報の追加
        formatted_content = self._add_note_metadata(formatted_content)
        
        return formatted_content
    
    def format_linkedin_post(self, content: str) -> str:
        """LinkedIn投稿のフォーマット調整"""
        # 基本的なクリーニング
        formatted_content = self._clean_content(content)
        
        # 文字数調整
        formatted_content = self._adjust_linkedin_length(formatted_content)
        
        # ビジネストーンの調整
        formatted_content = self._adjust_professional_tone(formatted_content)
        
        # ハッシュタグの追加
        formatted_content = self._add_linkedin_hashtags(formatted_content)
        
        # LinkedIn特有のフォーマット
        formatted_content = self._format_linkedin_structure(formatted_content)
        
        return formatted_content
    
    def format_twitter_thread(self, tweets: List[str]) -> str:
        """Twitterスレッドのフォーマット調整"""
        formatted_tweets = []
        
        for i, tweet in enumerate(tweets, 1):
            # 文字数調整
            formatted_tweet = self._adjust_tweet_length(tweet)
            
            # スレッド番号の追加
            if len(tweets) > 1:
                formatted_tweet = f"{i}/{len(tweets)} {formatted_tweet}"
            
            # ハッシュタグの調整
            if i == len(tweets):  # 最後のツイートにハッシュタグ
                formatted_tweet = self._add_twitter_hashtags(formatted_tweet)
            
            formatted_tweets.append(formatted_tweet)
        
        # スレッド全体の調整
        return self._format_twitter_thread_structure(formatted_tweets)
    
    def _clean_content(self, content: str) -> str:
        """基本的なコンテンツクリーニング"""
        # 余分な空白の除去
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # 不要な文字の除去
        content = content.strip()
        
        return content
    
    def _format_note_title(self, content: str) -> str:
        """noteのタイトルフォーマット"""
        lines = content.split('\n')
        title_line = None
        title_index = -1
        
        # タイトル行を見つける
        for i, line in enumerate(lines):
            if line.startswith('#') and not line.startswith('##'):
                title_line = line
                title_index = i
                break
        
        if title_line:
            # タイトルから#を除去し、長さを調整
            title = title_line.lstrip('#').strip()
            max_length = self.platform_specs['note']['max_title_length']
            
            if len(title) > max_length:
                title = title[:max_length-3] + "..."
            
            lines[title_index] = f"# {title}"
        
        return '\n'.join(lines)
    
    def _format_note_paragraphs(self, content: str) -> str:
        """note記事の段落フォーマット"""
        # 段落間の適切な空白を確保
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # 長い段落の分割
                if len(paragraph) > 200 and not paragraph.startswith('#'):
                    sentences = re.split(r'[。！？]', paragraph)
                    if len(sentences) > 2:
                        mid_point = len(sentences) // 2
                        part1 = '。'.join(sentences[:mid_point]) + '。'
                        part2 = '。'.join(sentences[mid_point:])
                        formatted_paragraphs.extend([part1, part2])
                    else:
                        formatted_paragraphs.append(paragraph)
                else:
                    formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def _format_note_headers(self, content: str) -> str:
        """note記事の見出しフォーマット"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.startswith('#'):
                # 見出しレベルの調整（最大3レベルまで）
                level = len(line) - len(line.lstrip('#'))
                if level > 3:
                    level = 3
                
                header_text = line.lstrip('#').strip()
                formatted_lines.append('#' * level + ' ' + header_text)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _adjust_emoji_usage(self, content: str, platform: str) -> str:
        """絵文字使用の調整"""
        if platform == 'note' and self.platform_specs['note']['use_emojis']:
            # 適度な絵文字の追加（既に含まれていない場合）
            if '✨' not in content and '📊' not in content:
                # 適切な場所に絵文字を追加
                content = re.sub(r'(効果|結果|改善)', r'\1✨', content, count=1)
                content = re.sub(r'(データ|数字|統計)', r'\1📊', content, count=1)
        
        return content
    
    def _add_note_metadata(self, content: str) -> str:
        """note記事にメタデータを追加"""
        metadata = f"\n\n---\n\n*最終更新: {datetime.now().strftime('%Y年%m月%d日')}*\n"
        metadata += "*🤖 マルチプラットフォーム投稿生成ツールで作成*"
        
        return content + metadata
    
    def _adjust_linkedin_length(self, content: str) -> str:
        """LinkedIn投稿の文字数調整"""
        max_length = self.platform_specs['linkedin']['max_length']
        preferred_range = self.platform_specs['linkedin']['preferred_length']
        
        if len(content) > max_length:
            # 文字数オーバーの場合、段落単位で調整
            paragraphs = content.split('\n\n')
            adjusted_content = ""
            current_length = 0
            
            for paragraph in paragraphs:
                if current_length + len(paragraph) + 2 <= max_length:
                    adjusted_content += paragraph + '\n\n'
                    current_length += len(paragraph) + 2
                else:
                    break
            
            content = adjusted_content.strip()
        
        return content
    
    def _adjust_professional_tone(self, content: str) -> str:
        """ビジネス向けトーンへの調整"""
        # カジュアルな表現をプロフェッショナルな表現に変換
        professional_replacements = {
            r'すごく': '非常に',
            r'ちょっと': '少し',
            r'やばい': '驚くべき',
            r'めっちゃ': 'とても',
            r'やっぱり': 'やはり'
        }
        
        for casual, professional in professional_replacements.items():
            content = re.sub(casual, professional, content)
        
        return content
    
    def _add_linkedin_hashtags(self, content: str) -> str:
        """LinkedIn用ハッシュタグの追加"""
        if '#' not in content:
            hashtags = [
                '#ビジネス', '#営業DX', '#業務効率化', 
                '#AI活用', '#働き方改革', '#生産性向上'
            ]
            
            # コンテンツに関連するハッシュタグを選択
            relevant_hashtags = []
            for hashtag in hashtags:
                keyword = hashtag[1:]  # #を除く
                if keyword in content or any(related in content for related in self._get_related_keywords(keyword)):
                    relevant_hashtags.append(hashtag)
            
            if relevant_hashtags:
                content += '\n\n' + ' '.join(relevant_hashtags[:5])  # 最大5つまで
        
        return content
    
    def _format_linkedin_structure(self, content: str) -> str:
        """LinkedIn投稿の構造フォーマット"""
        # 段落間の適切なスペース
        content = re.sub(r'\n\n+', '\n\n', content)
        
        # 箇条書きの調整
        content = re.sub(r'^- ', '・ ', content, flags=re.MULTILINE)
        
        return content
    
    def _adjust_tweet_length(self, tweet: str) -> str:
        """ツイートの文字数調整"""
        max_length = self.platform_specs['twitter']['max_tweet_length']
        preferred_length = self.platform_specs['twitter']['preferred_tweet_length']
        
        if len(tweet) > max_length:
            # 文字数オーバーの場合、文末で切り詰め
            cut_point = max_length - 3
            tweet = tweet[:cut_point] + "..."
        
        return tweet
    
    def _add_twitter_hashtags(self, tweet: str) -> str:
        """Twitter用ハッシュタグの追加"""
        if '#' not in tweet:
            hashtags = ['#営業DX', '#AI活用', '#業務効率化']
            
            # 文字数制限内でハッシュタグを追加
            for hashtag in hashtags:
                if len(tweet) + len(' ' + hashtag) <= self.platform_specs['twitter']['max_tweet_length']:
                    tweet += ' ' + hashtag
                else:
                    break
        
        return tweet
    
    def _format_twitter_thread_structure(self, tweets: List[str]) -> str:
        """Twitterスレッド全体の構造フォーマット"""
        formatted_thread = []
        
        for i, tweet in enumerate(tweets):
            # ツイート番号とインデント
            formatted_thread.append(f"ツイート{i+1}:")
            formatted_thread.append(tweet)
            formatted_thread.append("")  # 空行
        
        return '\n'.join(formatted_thread)
    
    def _get_related_keywords(self, keyword: str) -> List[str]:
        """関連キーワードの取得"""
        keyword_map = {
            'ビジネス': ['事業', '会社', '企業', '商売'],
            '営業DX': ['営業', 'セールス', 'DX', 'デジタル変革'],
            '業務効率化': ['効率', '自動化', '改善', '最適化'],
            'AI活用': ['AI', '人工知能', '機械学習', 'ChatGPT'],
            '働き方改革': ['働き方', 'リモートワーク', '在宅勤務'],
            '生産性向上': ['生産性', 'パフォーマンス', '成果']
        }
        
        return keyword_map.get(keyword, [])
    
    def validate_content_length(self, content: str, platform: str) -> Dict[str, any]:
        """コンテンツの長さを検証"""
        validation_result = {
            'valid': True,
            'warnings': [],
            'length': len(content),
            'platform': platform
        }
        
        if platform == 'note':
            if len(content) < 800:
                validation_result['warnings'].append("note記事としては短めです（推奨: 800-1500文字）")
            elif len(content) > 1500:
                validation_result['warnings'].append("note記事としては長めです（推奨: 800-1500文字）")
        
        elif platform == 'linkedin':
            preferred_range = self.platform_specs['linkedin']['preferred_length']
            if len(content) < preferred_range[0]:
                validation_result['warnings'].append(f"LinkedIn投稿としては短めです（推奨: {preferred_range[0]}-{preferred_range[1]}文字）")
            elif len(content) > preferred_range[1]:
                validation_result['warnings'].append(f"LinkedIn投稿としては長めです（推奨: {preferred_range[0]}-{preferred_range[1]}文字）")
        
        elif platform == 'twitter':
            max_length = self.platform_specs['twitter']['max_tweet_length']
            if len(content) > max_length:
                validation_result['valid'] = False
                validation_result['warnings'].append(f"ツイートが文字数制限を超えています（{len(content)}/{max_length}文字）")
        
        return validation_result