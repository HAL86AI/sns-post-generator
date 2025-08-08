# GASとAIで作る、自分だけの業務効率化ツール

こんにちは、横浜はるかです😊 前回の記事では、デジタル化のコツについてお話ししましたが、今回はもう一歩進んで「自分だけの業務効率化ツール」の作り方をご紹介します。

特別なプログラミングスキルは必要ありません。コピー＆ペーストで使えるコードを用意しましたので、ぜひお試しください。

## 1. メールの文章を自動で整えるツール

ビジネスメールを書くときに、つい堅苦しくなりすぎたり、逆にカジュアルになりすぎたりすることはありませんか？AIを使って、適切なビジネスメールに整えるツールを作ってみましょう。

```javascript
function formatBusinessEmail() {
  // 入力された文章を取得（実際にはテキストエリアなどから取得）
  const draft = "明日の打ち合わせ、よろしく！";
  
  // AIに依頼するプロンプト
  const prompt = `以下の文章をビジネスメールとして適切な形に整えてください。
  ・敬語を適切に使用する
  ・件名も作成する
  ・署名は不要
  
  入力：${draft}
  
  出力フォーマット：
  件名：
  本文：`;
  
  // AI APIを呼び出す（実際にはOpenAIやGeminiなどのAPIを使用）
  const response = callAIApi(prompt);
  
  // 結果を表示（実際にはUIに表示）
  Logger.log(response);
  return response;
}

// 使用例
// 件名：
// 明日の打ち合わせのご確認
// 
// 本文：
// お世話になっております。
// 合同会社アークスの横浜です。
// 
// 明日の打ち合わせの件、何卒よろしくお願いいたします。
// ご不明な点がございましたら、お気軽にお知らせください。
```

## 2. スケジュール調整を自動化するツール

面倒な日程調整を自動化するツールです。候補日を入力するだけで、調整用のメール本文を作成します。

```javascript
function createScheduleEmail() {
  // イベントの詳細を設定
  const eventDetails = {
    title: 'プロジェクト打ち合わせ',
    location: 'オンライン（Zoom）',
    duration: 60, // 分単位
    timeZone: 'Asia/Tokyo',
    // 候補日時（実際にはカレンダーから選択）
    candidateDates: [
      new Date(2023, 3, 10, 14, 0), // 年, 月-1, 日, 時, 分
      new Date(2023, 3, 11, 10, 0),
      new Date(2023, 3, 12, 15, 0)
    ]
  };
  
  // 日付をフォーマットする関数
  const formatDate = (date) => {
    const options = { 
      month: 'long', 
      day: 'numeric', 
      weekday: 'short',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    };
    return date.toLocaleDateString('ja-JP', options) + '〜';
  };
  
  // メール本文を作成
  let emailBody = `お世話になっております。
合同会社アークスの横浜です。

${eventDetails.title}の日程調整のご連絡をさせていただきます。

【候補日時】
`;
  
  // 候補日時を追加
  eventDetails.candidateDates.forEach((date, index) => {
    emailBody += `${index + 1}. ${formatDate(date)}\n`;
  });
  
  emailBody += `\n【場所】
${eventDetails.location}

【所要時間】
${eventDetails.duration}分程度を予定しております。

ご都合のよろしい日時がございましたら、お知らせください。
何卒よろしくお願いいたします。

-- 
横浜 はるか`;
  
  // 件名
  const subject = `【${eventDetails.title}】日程調整のご連絡`;
  
  // メールの下書きを作成
  GmailApp.createDraft('', subject, emailBody);
  
  return {
    subject: subject,
    body: emailBody
  };
}
```

## 3. タスク管理を自動化するツール

チャットツール（Slackなど）で「〇〇をやる」と書くと、自動でタスクに追加されるツールです。

```javascript
function processSlackMessage(event) {
  // Slackからのイベントを想定
  const message = event.text;
  const userId = event.user;
  
  // タスク追加のパターンを検出（例：「〇〇をやる」）
  const taskMatch = message.match(/(.+?)をやる/);
  
  if (taskMatch) {
    const taskName = taskMatch[1].trim();
    const dueDate = new Date();
    dueDate.setDate(dueDate.getDate() + 1); // デフォルトは翌日
    
    // タスクを追加（実際にはタスク管理ツールのAPIを使用）
    const task = addToTaskManager({
      name: taskName,
      dueDate: dueDate,
      assignee: userId
    });
    
    // 確認メッセージを返信
    return {
      response_type: 'in_channel',
      text: `タスクを追加しました: *${taskName}*\n期限: ${dueDate.toLocaleDateString('ja-JP')}`
    };
  }
  
  return null;
}

// タスク管理ツールに追加する関数（サンプル）
function addToTaskManager(task) {
  // 実際には、お使いのタスク管理ツールのAPIを呼び出す
  // 例: Todoist, Asana, Trello など
  Logger.log(`タスクを追加: ${task.name} (期限: ${task.dueDate})`);
  return { id: 'task123', ...task };
}
```

## 4. ドキュメントのテンプレートから自動生成するツール

よく使うドキュメント（見積書、請求書など）をテンプレートから自動生成するツールです。

```javascript
function generateDocument(templateName, data) {
  // テンプレートを取得（実際にはGoogleドライブから取得）
  const template = getTemplate(templateName);
  
  // テンプレート内のプレースホルダーを置換
  let content = template.content;
  
  Object.keys(data).forEach(key => {
    const placeholder = `{{${key}}}`;
    content = content.replace(new RegExp(placeholder, 'g'), data[key]);
  });
  
  // 新しいドキュメントを作成
  const doc = DocumentApp.create(`${data.documentName}_${new Date().toISOString().split('T')[0]}`);
  doc.getBody().setText(content);
  
  // フォーマットを適用（見出しや表のスタイルなど）
  applyDocumentStyles(doc, template.styles);
  
  return doc.getUrl();
}

// 使用例
function createEstimate() {
  const estimateData = {
    documentName: '見積書',
    companyName: '株式会社サンプル',
    estimateNumber: 'EST-2023-001',
    date: '2023年4月10日',
    dueDate: '2023年5月10日',
    items: [
      { name: 'コンサルティング料金', quantity: 10, unitPrice: 10000 },
      { name: 'システム開発費', quantity: 1, unitPrice: 300000 }
    ],
    taxRate: 10 // %
  };
  
  // 合計金額を計算
  const subtotal = estimateData.items.reduce((sum, item) => {
    return sum + (item.quantity * item.unitPrice);
  }, 0);
  
  const tax = Math.floor(subtotal * (estimateData.taxRate / 100));
  const total = subtotal + tax;
  
  // データに追加
  estimateData.subtotal = subtotal.toLocaleString();
  estimateData.tax = tax.toLocaleString();
  estimateData.total = total.toLocaleString();
  
  // ドキュメントを生成
  const docUrl = generateDocument('見積書テンプレート', estimateData);
  Logger.log(`見積書を作成しました: ${docUrl}`);
  return docUrl;
}
```

## 5. データを可視化するダッシュボード

スプレッドシートのデータを元に、自動でダッシュボードを更新するツールです。

```javascript
function updateDashboard() {
  // データを取得（実際にはスプレッドシートから取得）
  const data = getSalesData();
  
  // グラフ用のデータを準備
  const chartData = {
    labels: data.map(item => item.month),
    datasets: [{
      label: '売上',
      data: data.map(item => item.sales),
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1
    }]
  };
  
  // ダッシュボードのHTMLを生成
  const htmlTemplate = HtmlService.createTemplateFromFile('dashboard-template');
  htmlTemplate.chartData = JSON.stringify(chartData);
  htmlTemplate.summary = calculateSummary(data);
  
  // ダッシュボードを更新
  const dashboard = DriveApp.getFileById('ダッシュボードのファイルID');
  dashboard.setContent(htmlTemplate.evaluate().getContent());
  
  // 関係者にメールで通知
  sendDashboardUpdateNotification(dashboard.getUrl());
}

// サマリーを計算
function calculateSummary(data) {
  const total = data.reduce((sum, item) => sum + item.sales, 0);
  const average = total / data.length;
  const lastMonth = data[data.length - 1];
  const prevMonth = data[data.length - 2];
  const growth = prevMonth ? ((lastMonth.sales - prevMonth.sales) / prevMonth.sales * 100).toFixed(1) : 0;
  
  return {
    total: total.toLocaleString(),
    average: Math.floor(average).toLocaleString(),
    growth: growth
  };
}
```

## おわりに

いかがでしたか？これらのツールは、ほんの一例です。大切なのは「自分にとって本当に必要なもの」を作ること。

最初から完璧を目指す必要はありません。小さく始めて、少しずつ改良していくのがコツです。

「この作業、毎回同じことをしているな」と感じたら、それが自動化のチャンスかもしれません。

もし「こんなツールを作りたいけど、どうしたらいいかわからない」ということがあれば、お気軽にコメントで教えてください。一緒に考えていきましょう！

---
横浜はるか
合同会社アークス代表
https://x.com/haru_jp_teacher
https://note.com/earqs_haruka

#GAS #AI #業務効率化 #自動化 #事務仕事
