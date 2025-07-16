"""
Content Generator Module for creating platform-specific social media posts
"""

import re
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import time


@dataclass
class GenerationConfig:
    """コンテンツ生成の設定"""
    model_type: str
    temperature: float = 0.7
    max_tokens: int = 2000
    retry_attempts: int = 3
    retry_delay: float = 1.0


class ContentGenerator:
    """文体情報に基づいてプラットフォーム別のコンテンツを生成"""
    
    def __init__(self, model_type: str = "openrouter"):
        self.config = GenerationConfig(model_type=model_type)
        self.model_client = None
        self._initialize_model()
    
    def _initialize_model(self):
        """使用するモデルの初期化"""
        try:
            if self.config.model_type == "openrouter":
                self._init_openrouter()
            elif self.config.model_type == "claude":
                self._init_claude()
            elif self.config.model_type == "openai":
                self._init_openai()
            elif self.config.model_type == "local":
                self._init_local_model()
            else:
                raise ValueError(f"サポートされていないモデルタイプ: {self.config.model_type}")
        except Exception as e:
            print(f"警告: モデルの初期化に失敗しました ({e})")
            print("ローカルテンプレートベースの生成を使用します。")
            self.config.model_type = "template"
    
    def _init_claude(self):
        """Claude APIの初期化"""
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY環境変数が設定されていません")
            self.model_client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropicライブラリがインストールされていません: pip install anthropic")
    
    def _init_openai(self):
        """OpenAI APIの初期化"""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY環境変数が設定されていません")
            self.model_client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openaiライブラリがインストールされていません: pip install openai")
    
    def _init_local_model(self):
        """ローカルモデルの初期化"""
        try:
            # transformersを使用したローカルモデルの初期化
            from transformers import AutoTokenizer, AutoModelForCausalLM
            model_name = "rinna/japanese-gpt-neox-3.6b-instruction-ppo"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model_client = AutoModelForCausalLM.from_pretrained(model_name)
        except ImportError:
            raise ImportError("transformersライブラリがインストールされていません: pip install transformers torch")
    
    def _init_openrouter(self):
        """OpenRouter APIの初期化"""
        try:
            import requests
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY環境変数が設定されていません")
            
            # OpenRouter APIの設定
            self.openrouter_config = {
                "api_key": api_key,
                "base_url": "https://openrouter.ai/api/v1/chat/completions",
                "model": "anthropic/claude-3.5-sonnet-20241022",  # デフォルトモデル
                "headers": {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://sns-post-generator.onrender.com/",
                    "X-Title": "SNS Post Generator"
                }
            }
            self.model_client = requests.Session()
            self.model_client.headers.update(self.openrouter_config["headers"])
        except ImportError:
            raise ImportError("requestsライブラリがインストールされていません: pip install requests")
    
    def _call_api_with_retry(self, prompt: str) -> str:
        """APIを呼び出し、失敗時はリトライ"""
        for attempt in range(self.config.retry_attempts):
            try:
                if self.config.model_type == "openrouter":
                    return self._call_openrouter_api(prompt)
                elif self.config.model_type == "claude":
                    return self._call_claude_api(prompt)
                elif self.config.model_type == "openai":
                    return self._call_openai_api(prompt)
                elif self.config.model_type == "local":
                    return self._call_local_model(prompt)
                elif self.config.model_type == "template":
                    return self._generate_with_template(prompt)
                else:
                    raise ValueError(f"未サポートのモデルタイプ: {self.config.model_type}")
            
            except Exception as e:
                if attempt == self.config.retry_attempts - 1:
                    print(f"API呼び出しが失敗しました: {e}")
                    return self._generate_with_template(prompt)
                else:
                    print(f"API呼び出し失敗 (試行 {attempt + 1}/{self.config.retry_attempts}): {e}")
                    time.sleep(self.config.retry_delay)
        
        return self._generate_with_template(prompt)
    
    def _call_claude_api(self, prompt: str) -> str:
        """Claude APIを呼び出し"""
        message = self.model_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
    def _call_openai_api(self, prompt: str) -> str:
        """OpenAI APIを呼び出し"""
        response = self.model_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        return response.choices[0].message.content
    
    def _call_local_model(self, prompt: str) -> str:
        """ローカルモデルを呼び出し"""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model_client.generate(
                inputs,
                max_new_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text[len(prompt):].strip()
    
    def _call_openrouter_api(self, prompt: str) -> str:
        """OpenRouter APIを呼び出し"""
        import json
        
        payload = {
            "model": self.openrouter_config["model"],
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        response = self.model_client.post(
            self.openrouter_config["base_url"],
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if "choices" not in result or len(result["choices"]) == 0:
            raise Exception("OpenRouter API returned no choices")
        
        return result["choices"][0]["message"]["content"].strip()
    
    def _generate_with_template(self, prompt: str):
        """テンプレートベースでコンテンツを生成（フォールバック）"""
        # プロンプトからプラットフォームを判定
        if "note記事" in prompt or "800" in prompt:
            return self._generate_note_template()
        elif "LinkedIn" in prompt or "300" in prompt:
            return self._generate_linkedin_template()
        elif "Twitter" in prompt or "140" in prompt:
            return self._generate_twitter_template()
        else:
            return "申し訳ございませんが、コンテンツの生成に失敗しました。APIキーの設定を確認してください。"
    
    def _create_style_context(self, style_info: Dict) -> str:
        """文体情報をプロンプト用の文脈に変換"""
        context_parts = []
        
        # 文体ガイドから重要な情報を抽出
        if "style_guide" in style_info and style_info["style_guide"]:
            context_parts.append("【文体の特徴】")
            context_parts.append("- フレンドリーで親しみやすいトーン")
            context_parts.append("- 実際の経験に基づいた具体的なエピソードを交える")
            context_parts.append("- 読者との対話を意識した表現（「〜ですよね？」「〜しませんか？」など）")
            context_parts.append("- 絵文字を適度に使用")
            context_parts.append("- 専門用語は分かりやすく説明")
        
        # 文体プロファイルからの情報
        if "style_profile" in style_info and style_info["style_profile"]:
            profile = style_info["style_profile"]
            if "tone_patterns" in profile:
                context_parts.append("\n【文体パターン】")
                context_parts.append("- 読者への問いかけを多用")
                context_parts.append("- 親しみやすい表現")
                context_parts.append("- 個人的な体験談を含める")
        
        return "\n".join(context_parts)
    
    def generate_note_article(self, theme: str, style_info: Dict, target_length: Tuple[int, int]) -> str:
        """note記事を生成"""
        style_context = self._create_style_context(style_info)
        
        prompt = f"""
あなたは経験豊富なライターです。以下の条件に基づいて、note記事を作成してください。

{style_context}

【記事の構成】
1. 導入：読者の悩みに共感する問題提起
2. 本編：具体的な体験談や実例を交えて解説
3. まとめ：前向きなメッセージで締めくくる

【テーマ】
{theme}

【要件】
- 文字数：{target_length[0]}〜{target_length[1]}文字
- 読者が「やってみよう」と思える内容
- 具体的な数字や結果を含める
- 実体験に基づいたエピソード
- 読者との対話を意識した表現

マークダウン形式で記事を作成してください。
"""
        
        return self._call_api_with_retry(prompt)
    
    def generate_linkedin_post(self, theme: str, style_info: Dict, target_length: Tuple[int, int]) -> str:
        """LinkedIn投稿を生成"""
        style_context = self._create_style_context(style_info)
        
        prompt = f"""
あなたはビジネス経験豊富な専門家です。以下の条件に基づいて、LinkedIn投稿を作成してください。

{style_context}

【投稿の構成】
1. 結論先出し：主要なメッセージ
2. 根拠：体験談や具体例
3. 行動提案：読者への提案

【テーマ】
{theme}

【要件】
- 文字数：{target_length[0]}〜{target_length[1]}文字
- ビジネス関連の知見共有
- 論理的で分かりやすい構成
- 読者が行動を起こしたくなる内容
- プロフェッショナルなトーン

テキスト形式で投稿を作成してください。
"""
        
        return self._call_api_with_retry(prompt)
    
    def generate_twitter_thread(self, theme: str, style_info: Dict, max_tweets: int = 3) -> List[str]:
        """Twitter投稿（スレッド）を生成"""
        style_context = self._create_style_context(style_info)
        
        prompt = f"""
あなたは影響力のあるTwitterユーザーです。以下の条件に基づいて、Twitterスレッドを作成してください。

{style_context}

【スレッドの構成】
1/3 【発見】気づきやポイント
2/3 【詳細】具体的な内容や数値
3/3 【まとめ】行動提案やハッシュタグ

【テーマ】
{theme}

【要件】
- 最大{max_tweets}ツイート
- 各ツイート140文字以内
- インパクトのある表現
- エンゲージメントを促す内容
- 適切なハッシュタグ

各ツイートを番号付きで分けて作成してください。
"""
        
        response = self._call_api_with_retry(prompt)
        
        # テンプレートモードの場合、レスポンスは既にリストとして返される
        if isinstance(response, list):
            return response
        else:
            return self._parse_twitter_thread(response, max_tweets)
    
    def _parse_twitter_thread(self, response: str, max_tweets: int) -> List[str]:
        """Twitter スレッドのレスポンスを個別ツイートに分割"""
        tweets = []
        
        # 番号パターンでの分割を試行
        patterns = [
            r"(\d+)/\d+[：:\s]*(.+?)(?=\d+/\d+|$)",
            r"(\d+)[．.]\s*(.+?)(?=\d+[．.]|$)",
            r"【(\d+)】(.+?)(?=【\d+】|$)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL | re.MULTILINE)
            if matches and len(matches) <= max_tweets:
                tweets = [match[1].strip() for match in matches]
                break
        
        # パターンマッチングが失敗した場合、改行で分割
        if not tweets:
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            tweets = lines[:max_tweets]
        
        # 各ツイートを140文字以内に調整
        adjusted_tweets = []
        for tweet in tweets:
            if len(tweet) <= 140:
                adjusted_tweets.append(tweet)
            else:
                # 140文字以内に切り詰め
                adjusted_tweets.append(tweet[:137] + "...")
        
        return adjusted_tweets[:max_tweets]
    
    def _generate_note_template(self) -> str:
        """noteテンプレート記事（フォールバック用）"""
        return """# 営業の自動化で変わった私の働き方

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
    
    def _generate_linkedin_template(self) -> str:
        """LinkedInテンプレート投稿（フォールバック用）"""
        return """【営業自動化で生産性30%向上】

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
    
    def _generate_twitter_template(self) -> List[str]:
        """Twitterテンプレート投稿（フォールバック用）"""
        return [
            "1/3 【発見】営業活動をAIで自動化したら、生産性が30%向上しました✨ 定型作業から解放されて、本当に大切な顧客との関係構築に集中できるように",
            "2/3 【詳細】具体的にはCRMでの顧客管理、AI提案書生成、フォローアップ自動化を導入。結果：営業効率30%UP、成約率15%UP、戦略業務に2時間/日確保",
            "3/3 【まとめ】完璧を求めず、小さな自動化から始めるのがコツ。まずは1つの定型業務から試してみませんか？ #営業DX #AI活用 #業務効率化"
        ]