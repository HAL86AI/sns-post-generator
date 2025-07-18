#!/usr/bin/env python3
"""
超シンプルなSNS投稿生成ツール - エラーなし保証版
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """固定テンプレートを返すだけの超シンプル版"""
    try:
        # 固定のコンテンツを返す
        note_content = """# 営業の自動化で変わった私の働き方

## 毎日の営業活動に疲れていませんか？

営業職の皆さん、毎日のフォローアップや顧客管理に時間を取られていませんか？

私も以前は、一日の大半を定型的な作業に費やしていました。そこで試してみたのが、営業プロセスの自動化です。

## 実際に導入したツールと効果

### CRMシステムの活用
- 顧客情報の一元管理
- フォローアップの自動化
- 売上予測の精度向上

### AI技術を活用した営業支援
- 提案書の自動生成
- 最適なアプローチタイミングの提案
- 成約率の向上

結果として、営業効率が30%向上し、より戦略的な業務に時間を使えるようになりました。

## まとめ：小さく始めて大きく改善

営業の自動化は、一朝一夕にはできません。でも、小さな工夫の積み重ねで確実に改善できます。

皆さんも、日々の営業活動の中で「これって自動化できないかな？」と思う作業があれば、ぜひ試してみてください。"""

        linkedin_content = """【営業自動化で生産性30%向上】

営業プロセスにAI技術を導入した結果をシェアします。

【背景】
毎日の定型作業に時間を取られ、戦略的な営業活動に集中できていませんでした。

【実施内容】
・CRMシステムでの顧客管理自動化
・AI提案書生成ツールの導入
・フォローアップの自動化

【結果】
・営業効率30%向上
・成約率15%アップ
・戦略業務に2時間/日の時間創出

【提案】
小さな自動化から始めて、徐々に範囲を拡げることをおすすめします。まずは1つの業務から試してみませんか？

#営業DX #業務効率化 #AI活用 #営業自動化"""

        twitter_content = """1/3 【発見】営業活動をAIで自動化したら、生産性が30%向上しました✨ 定型作業から解放されて、本当に大切な顧客との関係構築に集中できるように

2/3 【詳細】具体的にはCRMでの顧客管理、AI提案書生成、フォローアップ自動化を導入。結果：営業効率30%UP、成約率15%UP、戦略業務に2時間/日確保

3/3 【まとめ】完璧を求めず、小さな自動化から始めるのがコツ。まずは1つの定型業務から試してみませんか？ #営業DX #AI活用 #業務効率化"""

        # 文字数情報
        content_stats = {
            'note': {
                'content': note_content,
                'char_count': len(note_content),
                'validation': {'warnings': []}
            },
            'linkedin': {
                'content': linkedin_content,
                'char_count': len(linkedin_content),
                'validation': {'warnings': []}
            },
            'twitter': {
                'content': twitter_content,
                'char_count': len(twitter_content),
                'validation': {'warnings': []}
            }
        }

        return jsonify({
            'success': True,
            'generated_at': datetime.now().isoformat(),
            'model_used': 'template',
            'content': content_stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'エラーが発生しました: {str(e)}'
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)