# AIとGASでできる、ちょっとした事務効率化の工夫

こんにちは、横浜はるかです😊 20年間の事務職経験を活かし、AIやGASを活用した業務効率化に取り組んでいます。

今日は、私が実際に使っている「これならできそう！」と思える、小さな効率化の工夫をいくつかご紹介します。特別なスキルがなくても、今日から始められるものばかりですよ。

## 1. カレンダーから自動でToDoリストを作成

Googleカレンダーの予定を元に、その日のToDoリストを自動で作成するスクリプトです。

```javascript
function createTodoFromCalendar() {
  const calendar = CalendarApp.getDefaultCalendar();
  const events = calendar.getEventsForDay(new Date());
  
  let todoList = "# 今日の予定\n\n";
  
  events.forEach((event, index) => {
    const time = event.getStartTime().toLocaleTimeString('ja-JP', {hour: '2-digit', minute:'2-digit'});
    todoList += `${index + 1}. [ ] ${time} ${event.getTitle()}\n`;
  });
  
  // メモアプリに保存（例：Google KeepやNotionなど）
  saveToNoteApp(todoList);
}
```

## 2. スプレッドシートのデータを自動で整形

毎回同じように行っているデータの並び替えや書式設定を自動化します。

```javascript
function formatSpreadsheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  
  // ヘッダー行を太字に
  const headerRow = range.offset(0, 0, 1);
  headerRow.setFontWeight('bold');
  
  // 日付列の書式を設定
  const dateColumn = 3; // C列が日付の場合
  const dateRange = sheet.getRange(2, dateColumn, sheet.getLastRow()-1, 1);
  dateRange.setNumberFormat('yyyy/MM/dd');
  
  // 数値の書式を設定
  const numberColumns = [4, 5, 6]; // D,E,F列が数値の場合
  numberColumns.forEach(col => {
    const numRange = sheet.getRange(2, col, sheet.getLastRow()-1, 1);
    numRange.setNumberFormat('#,##0');
  });
  
  // 列幅を自動調整
  sheet.autoResizeColumns(1, sheet.getLastColumn());
}
```

## 3. メールの下書きを自動生成

よく使うメールのテンプレートを用意し、状況に応じて自動で下書きを作成します。

```javascript
function createDraftEmail() {
  const template = {
    '打ち合わせの依頼': {
      subject: '【打ち合わせのご案内】{{件名}}',
      body: `{{宛先}} 様

お世話になっております。
合同会社アークスの横浜です。

この度、{{件名}}について打ち合わせをさせていただけますと幸いです。

【候補日時】
{{日付1}}
{{日付2}}
{{日付3}}

ご都合のよろしい日時がございましたら、お知らせください。
よろしくお願いいたします。

-- 
横浜 はるか`
    },
    '資料送付': {
      subject: '【資料送付】{{件名}}',
      body: `{{宛先}} 様

お世話になっております。
合同会社アークスの横浜です。

{{件名}}の資料を送付いたします。
ご確認のほど、よろしくお願いいたします。

-- 
横浜 はるか`
    }
  };
  
  // メールの種類を選択
  const type = '打ち合わせの依頼'; // 実際にはUIから選択
  const data = {
    '件名': '業務効率化について',
    '宛先': '山田 太郎',
    '日付1': '2023年4月1日 10:00〜11:00',
    '日付2': '2023年4月2日 14:00〜15:00',
    '日付3': '2023年4月3日 16:00〜17:00'
  };
  
  // テンプレートにデータを埋め込む
  let subject = template[type].subject;
  let body = template[type].body;
  
  Object.keys(data).forEach(key => {
    const regex = new RegExp(`{{${key}}}`);
    subject = subject.replace(regex, data[key]);
    body = body.replace(regex, data[key]);
  });
  
  // 下書きを作成
  GmailApp.createDraft(data['宛先'] + ' 様', subject, body);
}
```

## 4. 定期的なリマインダーを設定

定期的に行う業務のリマインダーを自動で設定します。

```javascript
function setMonthlyReminders() {
  const reminders = [
    { title: '請求書発行', day: 25, time: '10:00' },
    { title: '経費精算', day: 28, time: '15:00' },
    { title: '月次レポート作成', day: 1, time: '13:00' }
  ];
  
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth();
  
  reminders.forEach(reminder => {
    const reminderDate = new Date(currentYear, currentMonth, reminder.day);
    
    // 時間を設定
    const [hours, minutes] = reminder.time.split(':').map(Number);
    reminderDate.setHours(hours, minutes, 0, 0);
    
    // 過去の日付の場合は翌月に設定
    if (reminderDate < now) {
      reminderDate.setMonth(currentMonth + 1);
    }
    
    // カレンダーに追加
    const calendar = CalendarApp.getDefaultCalendar();
    calendar.createEvent(
      `【リマインダー】${reminder.title}`,
      reminderDate,
      new Date(reminderDate.getTime() + 30 * 60 * 1000), // 30分後
      {
        description: reminder.title + 'の時間です。',
        guests: 'your-email@example.com' // 自分のメールアドレス
      }
    );
  });
}
```

## 5. スプレッドシートのデータを元に簡単なレポートを作成

スプレッドシートのデータを元に、簡単なレポートを自動生成します。

```javascript
function generateSimpleReport() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('売上データ');
  const data = sheet.getDataRange().getValues();
  
  // ヘッダーを取得
  const headers = data[0];
  
  // データを整形
  let report = '# 売上レポート\n\n';
  
  // 合計を計算
  const amountIndex = headers.indexOf('金額');
  const total = data.slice(1).reduce((sum, row) => {
    return sum + (parseInt(row[amountIndex]) || 0);
  }, 0);
  
  report += `## 合計売上: ${total.toLocaleString()}円\n\n`;
  
  // カテゴリ別の合計を計算
  const categoryIndex = headers.indexOf('カテゴリ');
  const categories = {};
  
  data.slice(1).forEach(row => {
    const category = row[categoryIndex];
    const amount = parseInt(row[amountIndex]) || 0;
    
    if (category) {
      if (!categories[category]) {
        categories[category] = 0;
      }
      categories[category] += amount;
    }
  });
  
  // カテゴリ別の結果を追加
  report += '## カテゴリ別売上\n\n';
  
  Object.entries(categories).forEach(([category, amount]) => {
    const percentage = ((amount / total) * 100).toFixed(1);
    report += `- ${category}: ${amount.toLocaleString()}円 (${percentage}%)\n`;
  });
  
  // ドキュメントに保存
  const doc = DocumentApp.create(`売上レポート_${Utilities.formatDate(new Date(), 'JST', 'yyyyMMdd')}`);
  doc.getBody().editAsText().appendText(report);
  
  return doc.getUrl();
}
```

## おわりに

いかがでしたか？どれも特別なスキルがなくても、コピー＆ペーストで使えるものばかりです。

私も最初は「プログラミングなんて難しそう」と思っていましたが、少しずつ試していくうちに、だんだんと楽しくなってきました。

「このスクリプト、もう少しアレンジしてみよう」とか「ここを変えたらもっと便利になるかも」と考えるのも、なかなか楽しいものです。

もし「ここがわからない」「もっと詳しく知りたい」ということがあれば、お気軽にコメントで教えてくださいね。一緒に学んでいきましょう！

---
横浜はるか
合同会社アークス代表
https://x.com/haru_jp_teacher
https://note.com/earqs_haruka

#GAS #事務効率化 #AI #自動化 #事務仕事
