"""
Style Analysis Module for extracting writing patterns from sample articles
"""

import re
import os
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import json
import markdown
from pathlib import Path


class StyleAnalyzer:
    """Analyzes writing style from sample articles and style guides"""
    
    def __init__(self):
        self.style_patterns = {
            'tone_indicators': [],
            'common_phrases': [],
            'sentence_patterns': [],
            'paragraph_structure': {},
            'vocabulary_preferences': {},
            'formatting_style': {}
        }
    
    def load_style_guide(self, guide_path: str) -> Dict:
        """Load and parse style guide markdown file"""
        try:
            with open(guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract key information from style guide
            guide_data = {
                'tone_keywords': self._extract_tone_keywords(content),
                'common_expressions': self._extract_common_expressions(content),
                'platform_guidelines': self._extract_platform_guidelines(content),
                'structure_preferences': self._extract_structure_preferences(content)
            }
            
            return guide_data
        except Exception as e:
            print(f"Error loading style guide: {e}")
            return {}
    
    def analyze_sample_articles(self, articles_dir: str) -> Dict:
        """Analyze style patterns from sample articles"""
        articles_data = []
        
        for file_path in Path(articles_dir).glob('*.md'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                article_analysis = {
                    'title': self._extract_title(content),
                    'structure': self._analyze_structure(content),
                    'tone_patterns': self._analyze_tone_patterns(content),
                    'vocabulary': self._analyze_vocabulary(content),
                    'sentence_patterns': self._analyze_sentence_patterns(content),
                    'paragraph_stats': self._analyze_paragraph_stats(content)
                }
                
                articles_data.append(article_analysis)
                
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return self._synthesize_style_profile(articles_data)
    
    def _extract_tone_keywords(self, content: str) -> List[str]:
        """Extract tone-related keywords from style guide"""
        tone_section = re.search(r'### トーン\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if tone_section:
            return re.findall(r'[「」]([^「」]+)[「」]', tone_section.group(1))
        return []
    
    def _extract_common_expressions(self, content: str) -> List[str]:
        """Extract common expressions from style guide"""
        expr_section = re.search(r'### よく使う表現\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if expr_section:
            expressions = re.findall(r'- [「」]([^「」]+)[「」]', expr_section.group(1))
            return expressions
        return []
    
    def _extract_platform_guidelines(self, content: str) -> Dict:
        """Extract platform-specific guidelines"""
        platforms = {}
        
        # Extract note guidelines
        note_section = re.search(r'### note\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if note_section:
            platforms['note'] = self._parse_platform_info(note_section.group(1))
        
        # Extract LinkedIn guidelines
        linkedin_section = re.search(r'### LinkedIn\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if linkedin_section:
            platforms['linkedin'] = self._parse_platform_info(linkedin_section.group(1))
        
        # Extract Twitter guidelines
        twitter_section = re.search(r'### Twitter/X\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if twitter_section:
            platforms['twitter'] = self._parse_platform_info(twitter_section.group(1))
        
        return platforms
    
    def _parse_platform_info(self, content: str) -> Dict:
        """Parse platform-specific information"""
        info = {}
        
        # Extract character count
        char_count = re.search(r'(\d+)-?(\d+)?文字', content)
        if char_count:
            info['min_chars'] = int(char_count.group(1))
            info['max_chars'] = int(char_count.group(2) or char_count.group(1))
        
        # Extract tone information
        tone_match = re.search(r'トーン[：:]([^\\n]+)', content)
        if tone_match:
            info['tone'] = tone_match.group(1).strip()
        
        return info
    
    def _extract_structure_preferences(self, content: str) -> Dict:
        """Extract structure preferences from style guide"""
        structure = {}
        
        # Extract paragraph info
        para_section = re.search(r'### 文字数と段落\n(.*?)(?=\n###|\n##|\Z)', content, re.DOTALL)
        if para_section:
            para_info = para_section.group(1)
            # Extract sentences per paragraph
            sent_match = re.search(r'(\d+)-(\d+)文程度', para_info)
            if sent_match:
                structure['sentences_per_paragraph'] = {
                    'min': int(sent_match.group(1)),
                    'max': int(sent_match.group(2))
                }
        
        return structure
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        return title_match.group(1) if title_match else ""
    
    def _analyze_structure(self, content: str) -> Dict:
        """Analyze article structure"""
        lines = content.split('\n')
        structure = {
            'total_lines': len(lines),
            'headers': [],
            'paragraphs': 0,
            'empty_lines': 0
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                structure['headers'].append({'level': level, 'text': line[level:].strip()})
            elif line == '':
                structure['empty_lines'] += 1
            elif line:
                structure['paragraphs'] += 1
        
        return structure
    
    def _analyze_tone_patterns(self, content: str) -> Dict:
        """Analyze tone patterns in content"""
        # Remove markdown formatting
        clean_content = re.sub(r'[#*`_\[\]()]', '', content)
        
        tone_patterns = {
            'question_frequency': len(re.findall(r'[？?]', clean_content)),
            'casual_expressions': len(re.findall(r'(ですよね|だと思う|という感じ|なんです)', clean_content)),
            'polite_expressions': len(re.findall(r'(させていただ|おります|いたします)', clean_content)),
            'personal_pronouns': len(re.findall(r'(私|僕|自分)', clean_content)),
            'reader_engagement': len(re.findall(r'(皆さん|あなた|読者)', clean_content))
        }
        
        return tone_patterns
    
    def _analyze_vocabulary(self, content: str) -> Dict:
        """Analyze vocabulary usage"""
        # Simple vocabulary analysis
        words = re.findall(r'[ぁ-んァ-ン一-龯]+', content)
        word_freq = Counter(words)
        
        return {
            'total_words': len(words),
            'unique_words': len(word_freq),
            'most_common': word_freq.most_common(10)
        }
    
    def _analyze_sentence_patterns(self, content: str) -> Dict:
        """Analyze sentence patterns"""
        sentences = re.split(r'[。！？\n]', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        sentence_lengths = [len(s) for s in sentences]
        
        return {
            'total_sentences': len(sentences),
            'avg_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
            'sentence_length_distribution': {
                'short': len([s for s in sentence_lengths if s < 20]),
                'medium': len([s for s in sentence_lengths if 20 <= s < 50]),
                'long': len([s for s in sentence_lengths if s >= 50])
            }
        }
    
    def _analyze_paragraph_stats(self, content: str) -> Dict:
        """Analyze paragraph statistics"""
        paragraphs = re.split(r'\n\s*\n', content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        paragraph_stats = []
        for para in paragraphs:
            sentences = re.split(r'[。！？]', para)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            paragraph_stats.append({
                'sentence_count': len(sentences),
                'char_count': len(para),
                'line_count': len(para.split('\n'))
            })
        
        return {
            'total_paragraphs': len(paragraph_stats),
            'avg_sentences_per_paragraph': sum(p['sentence_count'] for p in paragraph_stats) / len(paragraph_stats) if paragraph_stats else 0,
            'avg_chars_per_paragraph': sum(p['char_count'] for p in paragraph_stats) / len(paragraph_stats) if paragraph_stats else 0
        }
    
    def _synthesize_style_profile(self, articles_data: List[Dict]) -> Dict:
        """Synthesize style profile from multiple articles"""
        if not articles_data:
            return {}
        
        # Aggregate statistics
        total_tone_patterns = defaultdict(int)
        total_vocabulary = defaultdict(int)
        total_sentence_stats = defaultdict(list)
        
        for article in articles_data:
            # Aggregate tone patterns
            for key, value in article['tone_patterns'].items():
                total_tone_patterns[key] += value
            
            # Aggregate vocabulary
            for word, count in article['vocabulary']['most_common']:
                total_vocabulary[word] += count
            
            # Aggregate sentence stats
            total_sentence_stats['avg_sentence_length'].append(article['sentence_patterns']['avg_sentence_length'])
            total_sentence_stats['total_sentences'].append(article['sentence_patterns']['total_sentences'])
        
        # Calculate averages
        style_profile = {
            'tone_patterns': dict(total_tone_patterns),
            'common_vocabulary': dict(Counter(total_vocabulary).most_common(20)),
            'sentence_stats': {
                'avg_sentence_length': sum(total_sentence_stats['avg_sentence_length']) / len(total_sentence_stats['avg_sentence_length']),
                'avg_sentences_per_article': sum(total_sentence_stats['total_sentences']) / len(total_sentence_stats['total_sentences'])
            },
            'structural_patterns': self._extract_common_structures(articles_data)
        }
        
        return style_profile
    
    def _extract_common_structures(self, articles_data: List[Dict]) -> Dict:
        """Extract common structural patterns"""
        structures = []
        
        for article in articles_data:
            headers = article['structure']['headers']
            structure_pattern = [h['level'] for h in headers]
            structures.append(structure_pattern)
        
        # Find most common structure patterns
        structure_counter = Counter(tuple(s) for s in structures)
        
        return {
            'common_header_patterns': [list(pattern) for pattern, count in structure_counter.most_common(3)],
            'typical_header_count': sum(len(s) for s in structures) / len(structures) if structures else 0
        }
    
    def save_analysis(self, style_profile: Dict, output_path: str):
        """Save style analysis results to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(style_profile, f, ensure_ascii=False, indent=2)
            print(f"Style analysis saved to {output_path}")
        except Exception as e:
            print(f"Error saving analysis: {e}")
    
    def load_analysis(self, analysis_path: str) -> Dict:
        """Load previously saved style analysis"""
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading analysis: {e}")
            return {}
    
    def _extract_style_info_from_text(self, style_text: str) -> Dict:
        """Extract style information from text content (for web UI)"""
        style_info = {
            'tone_keywords': [],
            'common_expressions': [],
            'writing_principles': [],
            'target_audience': []
        }
        
        # Extract tone-related information
        tone_patterns = [
            r'フレンドリー', r'親しみやすい', r'カジュアル', r'丁寧',
            r'プロフェッショナル', r'ビジネス', r'フォーマル'
        ]
        
        for pattern in tone_patterns:
            if re.search(pattern, style_text):
                style_info['tone_keywords'].append(pattern)
        
        # Extract common expressions patterns
        expression_patterns = [
            r'読者との対話', r'問いかけ', r'体験談', r'具体例',
            r'絵文字', r'分かりやすく', r'実践的'
        ]
        
        for pattern in expression_patterns:
            if re.search(pattern, style_text):
                style_info['common_expressions'].append(pattern)
        
        return style_info
    
    def _analyze_sample_texts(self, sample_articles: List[Dict]) -> Dict:
        """Analyze style from sample article texts (for web UI)"""
        if not sample_articles:
            return {}
        
        combined_analysis = {
            'total_articles': len(sample_articles),
            'avg_length': 0,
            'tone_patterns': {},
            'common_words': [],
            'structure_patterns': []
        }
        
        total_length = 0
        all_content = ""
        
        for article in sample_articles:
            content = article.get('content', '')
            total_length += len(content)
            all_content += content + "\n\n"
        
        if total_length > 0:
            combined_analysis['avg_length'] = total_length // len(sample_articles)
        
        # Analyze combined content
        if all_content:
            # Tone analysis
            combined_analysis['tone_patterns'] = self._analyze_tone_patterns(all_content)
            
            # Word frequency
            vocab_analysis = self._analyze_vocabulary(all_content)
            combined_analysis['common_words'] = vocab_analysis.get('most_common', [])[:10]
        
        return combined_analysis


if __name__ == "__main__":
    # Example usage
    analyzer = StyleAnalyzer()
    
    # Load style guide
    guide_data = analyzer.load_style_guide("../input/haru_writing_guide.md")
    print("Style guide loaded:", guide_data)
    
    # Analyze sample articles
    style_profile = analyzer.analyze_sample_articles("../input/note_md_files/")
    print("Style profile generated:", style_profile)
    
    # Save analysis
    analyzer.save_analysis(style_profile, "../output/style_analysis.json")