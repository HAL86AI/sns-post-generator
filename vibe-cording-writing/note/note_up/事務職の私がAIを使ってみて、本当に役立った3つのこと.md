# 事務職の私がAIを使ってみて、本当に役立った3つのこと

こんにちは、横浜はるかです😊 20年間の事務職経験を経て、今は合同会社アークスでAIを活用した業務効率化のお手伝いをしています。

「AIって本当に役に立つの？」「難しそうで手が出ない」という声をよく耳にします。私も最初はそう思っていました。

今日は、私が実際に試してみて「これは本当に助かった！」と思ったAIの使い方を3つ、具体的な例を交えてご紹介します。

## 1. メールの文章を整えてくれるAIアシスタント

「このメール、どう書けば伝わりやすいかな…」と悩むこと、ありませんか？私はよくありました。

そんな時、AIに相談してみたんです。

```javascript
function improveEmailText(originalText) {
  const prompt = `以下の文章を、ビジネスメールとして適切な形に整えてください。
  ・丁寧で分かりやすい表現に
  ・箇条書きを活用して読みやすく
  ・適度な改行を入れる
  ・必要に応じて見出しを追加
  
  【元の文章】
  ${originalText}`;
  
  // AI APIを呼び出す（実際にはOpenAIやGeminiなどのAPIを使用）
  const improvedText = callAIApi(prompt);
  return improvedText;
}

// 使用例
const myDraft = "明日の打ち合わせ、資料の準備お願いします。あと、前回の議事録も確認しておいてください。";
const improved = improveEmailText(myDraft);
Logger.log(improved);
```

これが、

```
お世話になっております。
合同会社アークスの横浜です。

【お願い】
・明日の打ち合わせの資料をご準備いただけますと幸いです。
・前回の議事録についても、あわせてご確認をお願いいたします。

何かご不明な点がございましたら、お気軽にお知らせください。

よろしくお願いいたします。
```

こんな風に、一気にビジネスライクな文章に変身します。

## 2. 議事録の自動要約

会議の議事録を取るのが苦手でした。特に、話が脱線した時の対応に困っていました。

そこで、音声文字起こしアプリとAIを組み合わせて、議事録の下書きを作成する仕組みを作りました。

```javascript
function generateMeetingMinutes(transcript) {
  const prompt = `以下の会話の内容を、以下の形式で議事録にまとめてください。
  
  # 会議名
  
  ## 日時
  
  ## 参加者
  
  ## 決定事項
  - [ ] タスク1（担当者：名前、期限：日付）
  
  ## 議論された内容
  
  ## 次回までのアクション
  
  ---
  
  【会話の内容】
  ${transcript}`;
  
  // AI APIを呼び出して議事録を生成
  const minutes = callAIApi(prompt);
  
  // Google ドキュメントに保存
  const doc = DocumentApp.create(`議事録_${Utilities.formatDate(new Date(), 'JST', 'yyyyMMdd_HHmm')}`);
  doc.getBody().setText(minutes);
  
  return doc.getUrl();
}
```

この仕組みを使ってから、議事録作成の時間が半分以下に短縮できました。

## 3. データ分析のサポート

エクセルでデータを分析する時、「このデータ、何か傾向があるのかな？」と悩むことがよくありました。

AIにデータを渡すと、自動で分析して気づきを教えてくれるツールを作成しました。

```javascript
function analyzeData(data) {
  // データをCSV形式に変換
  const csv = convertToCsv(data);
  
  const prompt = `以下のCSVデータを分析し、以下の観点で気づいたことを教えてください。
  - データの傾向や特徴
  - 注目すべき点や外れ値
  - 改善のヒントになりそうなポイント
  
  また、必要に応じてグラフ化の提案もお願いします。
  
  【データ】
  ${csv}`;
  
  // AI APIを呼び出して分析を実行
  const analysis = callAIApi(prompt);
  
  // 結果をスプレッドシートに保存
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('分析結果') || ss.insertSheet('分析結果');
  
  // ヘッダーを設定
  sheet.clear();
  sheet.appendRow(['分析日時', '分析結果']);
  
  // 分析結果を追加
  sheet.appendRow([new Date(), analysis]);
  
  // セルの幅を調整
  sheet.autoResizeColumn(1);
  sheet.autoResizeColumn(2);
  
  return analysis;
}

// 使用例
const salesData = [
  ['月', '売上'],
  ['1月', 100],
  ['2月', 150],
  ['3月', 200],
  // ...
];

const result = analyzeData(salesData);
Logger.log(result);
```

## おわりに

AIは「魔法のツール」ではありませんが、使い方を工夫すれば、事務職の強い味方になってくれます。

私が実感したのは、AIに「完璧」を求めすぎないこと。人間のサポートツールとして、うまく付き合っていくことが大切だと思います。

「これ、AIでできないかな？」と思ったら、まずは小さく試してみてください。意外な発見があるかもしれませんよ。

もし「こんなこと、AIでできる？」というご質問や、「もっと詳しく知りたい」ということがあれば、お気軽にコメントくださいね。

---
横浜はるか
合同会社アークス代表
https://x.com/haru_jp_teacher
https://note.com/earqs_haruka

#AI活用 #事務効率化 #GAS #業務改善 #事務職
