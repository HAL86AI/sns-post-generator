#!/usr/bin/env python3
"""
Web UI for Multi-platform Social Media Post Generator
モダンでシンプルなWebインターフェース
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil
from pathlib import Path
import json
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(str(Path(__file__).parent / "src"))

from style_analyzer import StyleAnalyzer
from content_generator import ContentGenerator
from platform_formatter import PlatformFormatter

app = Flask(__name__)
CORS(app)

# 設定
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 許可するファイル拡張子
ALLOWED_EXTENSIONS = {'txt', 'md'}

def allowed_file(filename):
    """アップロードファイルの拡張子チェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """コンテンツ生成API"""
    try:
        data = request.get_json()
        
        # 必須フィールドのチェック
        required_fields = ['theme', 'style_guide', 'sns_workflow']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({
                    'success': False,
                    'error': f'{field}は必須項目です'
                }), 400
        
        # 入力データの取得
        theme = data['theme']
        style_guide_text = data['style_guide']
        sns_workflow_text = data['sns_workflow']
        sample_articles = data.get('sample_articles', [])
        model_type = data.get('model_type', 'template')
        
        # 文体分析の実行
        analyzer = StyleAnalyzer()
        
        # 文体ガイドの処理
        style_guide = analyzer._extract_style_info_from_text(style_guide_text)
        
        # サンプル記事の分析
        style_profile = {}
        if sample_articles:
            style_profile = analyzer._analyze_sample_texts(sample_articles)
        
        # 統合した文体情報
        combined_style = {
            "style_guide": style_guide,
            "style_profile": style_profile,
            "workflow": sns_workflow_text
        }
        
        # コンテンツ生成
        generator = ContentGenerator(model_type=model_type)
        formatter = PlatformFormatter()
        
        generated_content = {}
        
        # note記事生成
        note_content = generator.generate_note_article(
            theme=theme,
            style_info=combined_style,
            target_length=(800, 1500)
        )
        generated_content['note'] = formatter.format_note_article(note_content)
        
        # LinkedIn投稿生成
        linkedin_content = generator.generate_linkedin_post(
            theme=theme,
            style_info=combined_style,
            target_length=(300, 600)
        )
        generated_content['linkedin'] = formatter.format_linkedin_post(linkedin_content)
        
        # Twitter投稿生成
        twitter_content = generator.generate_twitter_thread(
            theme=theme,
            style_info=combined_style,
            max_tweets=3
        )
        generated_content['twitter'] = formatter.format_twitter_thread(twitter_content)
        
        # 文字数情報の追加
        content_stats = {
            'note': {
                'content': generated_content['note'],
                'char_count': len(generated_content['note']),
                'validation': formatter.validate_content_length(generated_content['note'], 'note')
            },
            'linkedin': {
                'content': generated_content['linkedin'],
                'char_count': len(generated_content['linkedin']),
                'validation': formatter.validate_content_length(generated_content['linkedin'], 'linkedin')
            },
            'twitter': {
                'content': generated_content['twitter'],
                'char_count': len(generated_content['twitter']),
                'validation': formatter.validate_content_length(generated_content['twitter'], 'twitter')
            }
        }
        
        return jsonify({
            'success': True,
            'generated_at': datetime.now().isoformat(),
            'model_used': generator.config.model_type,
            'content': content_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'コンテンツ生成中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """ファイルアップロード処理"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400
        
        file = request.files['file']
        file_type = request.form.get('file_type', 'sample_article')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'ファイルが選択されていません'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # ファイル内容を読み込み
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ファイルを削除（メモリ使用量を抑えるため）
            os.remove(file_path)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'content': content,
                'file_type': file_type,
                'char_count': len(content)
            })
        
        return jsonify({'success': False, 'error': '許可されていないファイル形式です（.txt, .mdのみ）'}), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'ファイルアップロード中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/download/<platform>')
def download_content(platform):
    """生成されたコンテンツのダウンロード"""
    try:
        # セッションからコンテンツを取得（実際の実装では適切なストレージを使用）
        # この例では、リクエストパラメータからコンテンツを取得
        content = request.args.get('content', '')
        
        if not content:
            return jsonify({'success': False, 'error': 'ダウンロードするコンテンツがありません'}), 400
        
        # 一時ファイルを作成
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        temp_file.write(content)
        temp_file.close()
        
        # ファイル名の設定
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_map = {
            'note': f'note_draft_{timestamp}.md',
            'linkedin': f'linkedin_post_{timestamp}.txt',
            'twitter': f'twitter_thread_{timestamp}.txt'
        }
        
        filename = filename_map.get(platform, f'{platform}_content_{timestamp}.txt')
        
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'ダウンロード中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/static/manifest.json')
def manifest():
    """PWA manifest file"""
    return send_file('static/manifest.json', mimetype='application/json')

@app.route('/static/sw.js')
def service_worker():
    """Service Worker file"""
    return send_file('static/sw.js', mimetype='application/javascript')

# カスタム404エラーハンドラ
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'success': False, 'error': 'エンドポイントが見つかりません'}), 404

# カスタム500エラーハンドラ
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'サーバー内部エラーが発生しました'}), 500

