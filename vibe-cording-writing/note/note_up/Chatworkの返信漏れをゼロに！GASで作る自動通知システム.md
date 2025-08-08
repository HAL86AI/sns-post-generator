# Chatworkの返信漏れをゼロに！GASで作る自動通知システム

こんにちは、合同会社アークスのはるです。

「あのメッセージ、返信したっけ？」
「気づいたら未読メッセージが大量に...」

Chatworkを使っていると、こんな経験ありませんか？私も以前は返信漏れが気になって、何度も確認作業をしていました。

そこで、Google Apps Script（GAS）を使って、返信漏れを防ぐ自動通知システムを作成しました。

## この記事を読むとわかること

- Chatworkの返信漏れを自動で通知する仕組みの作り方
- プログラミング初心者でもできるGASの基本的な使い方
- 業務効率を上げる自動化のコツ

## このシステムの特徴

1. **自動で未返信をチェック**
   - 前日までに返信していないメッセージを自動検出
   - 翌朝5時に通知が届く

2. **スプレッドシートで管理**
   - 未返信メッセージを自動で記録
   - 過去の履歴を確認可能

3. **カスタマイズ自由**
   - 通知タイミングを変更可能
   - 条件を追加してより便利に

## 準備するもの

1. Googleアカウント（無料）
2. Chatwork APIトークン（後述の手順で取得）
3. Googleスプレッドシート（新規作成）

## 1. Chatwork APIトークンの取得

1. Chatworkにログイン
2. 右上のプロフィール画像をクリック
3. 「設定」→「API設定」を選択
4. 「新しいAPIトークンを発行」をクリック
5. 適当な名前を入力して「発行」
6. 表示されたトークンをメモ（※このトークンは2度と表示されないので大切に保管）

## 2. スプレッドシートの準備

1. 以下のテンプレートをコピーして使用してください：
   [Chatwork通知ログ テンプレート](https://docs.google.com/spreadsheets/d/1ywHIRKXi_an-w9RWr74nF3-_GTuUEb8wY_sWr1kmviw/copy)
   
   または、新しいスプレッドシートを作成する場合は：
   
   1. [新しいGoogleスプレッドシート](https://sheets.new)を開く
   2. シート名を「Chatwork通知ログ」に変更
   3. 1行目に以下の見出しを入力
      - 日付
      - ルーム名
      - メッセージ本文
      - 投稿日時
      - 最終更新日時
      - ルームURL

## 3. GASプロジェクトの作成

1. スプレッドシートのメニューから「拡張機能」→「Apps Script」を選択
2. プロジェクト名を「Chatwork返信リマインダー」に変更
3. 以下のコードをコピーして貼り付け

```javascript
// 定数設定
const CONFIG = {
  // Chatwork APIトークン
  CHATWORK_API_TOKEN: 'ここにAPIトークンを入力',
  
  // スプレッドシートのURL
  SPREADSHEET_URL: 'ここにスプレッドシートのURLを入力',
  
  // 通知する期間（日数）
  TARGET_DAYS: 1,
  
  // 通知を送るチャットルームID（空の場合は全ルーム）
  TARGET_ROOMS: [],
  
  // 通知を除外するルームID
  EXCLUDE_ROOMS: [],
  
  // 通知メッセージ
  NOTIFICATION_MESSAGE: '[info][title]【未返信メッセージのお知らせ】[/title]\n' +
                     '前日までに返信のないメッセージがあります。\n' +
                     '確認をお願いします。[/info]\n\n',
  
  // デバッグモード（trueにするとログが詳細に表示されます）
  DEBUG: false
};

// メイン関数
function checkUnrepliedMessages() {
  try {
    // スプレッドシートを取得
    const spreadsheet = SpreadsheetApp.openByUrl(CONFIG.SPREADSHEET_URL);
    const sheet = spreadsheet.getSheetByName('Chatwork通知ログ') || spreadsheet.insertSheet('Chatwork通知ログ');
    
    // ヘッダーがなければ作成
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(['日付', 'ルーム名', 'メッセージ本文', '投稿日時', '最終更新日時', 'ルームURL']);
    }
    
    // ログを記録する配列
    const logs = [];
    
    // 対象のチャットルームを取得
    const rooms = getChatRooms();
    
    // 各ルームのメッセージを確認
    rooms.forEach(room => {
      if (CONFIG.DEBUG) console.log(`Checking room: ${room.name} (${room.room_id})`);
      
      // 未返信メッセージを取得
      const unrepliedMessages = getUnrepliedMessages(room.room_id);
      
      // ログに追加
      unrepliedMessages.forEach(message => {
        logs.push([
          Utilities.formatDate(new Date(), 'JST', 'yyyy/MM/dd'),
          room.name,
          message.body,
          message.send_time,
          message.update_time,
          `https://www.chatwork.com/#!rid${room.room_id}-${message.message_id}`
        ]);
      });
      
      // 未返信メッセージがあれば通知
      if (unrepliedMessages.length > 0) {
        sendNotification(room, unrepliedMessages);
      }
    });
    
    // スプレッドシートにログを追加
    if (logs.length > 0) {
      sheet.getRange(sheet.getLastRow() + 1, 1, logs.length, logs[0].length).setValues(logs);
    }
    
    if (CONFIG.DEBUG) console.log('処理が完了しました');
    return `処理が完了しました。${logs.length}件の未返信メッセージを記録しました。`;
    
  } catch (e) {
    console.error(`エラーが発生しました: ${e.message}`);
    return `エラーが発生しました: ${e.message}`;
  }
}

// チャットルーム一覧を取得
function getChatRooms() {
  const url = 'https://api.chatwork.com/v2/rooms';
  const response = callChatworkAPI(url);
  
  // 対象ルームをフィルタリング
  let rooms = response.data;
  
  // 特定のルームのみを対象にする場合
  if (CONFIG.TARGET_ROOMS.length > 0) {
    rooms = rooms.filter(room => CONFIG.TARGET_ROOMS.includes(room.room_id));
  }
  
  // 除外するルームをフィルタリング
  if (CONFIG.EXCLUDE_ROOMS.length > 0) {
    rooms = rooms.filter(room => !CONFIG.EXCLUDE_ROOMS.includes(room.room_id));
  }
  
  return rooms;
}

// 未返信メッセージを取得
function getUnrepliedMessages(roomId) {
  const now = new Date();
  const targetDate = new Date(now);
  targetDate.setDate(now.getDate() - CONFIG.TARGET_DAYS);
  
  const url = `https://api.chatwork.com/v2/rooms/${roomId}/messages?force=1`;
  const response = callChatworkAPI(url);
  
  const unrepliedMessages = [];
  let lastMessageIsMine = false;
  
  // メッセージを古い順に処理
  response.data.reverse().forEach(message => {
    const messageDate = new Date(message.send_time * 1000);
    
    // 対象期間外はスキップ
    if (messageDate < targetDate) return;
    
    const isMine = message.account.account_id === response.headers['x-ratelimit-account-id'];
    
    if (!isMine && lastMessageIsMine === false) {
      // 未返信メッセージとして追加
      unrepliedMessages.push({
        message_id: message.message_id,
        body: message.body,
        send_time: Utilities.formatDate(messageDate, 'JST', 'yyyy/MM/dd HH:mm:ss'),
        update_time: Utilities.formatDate(new Date(message.update_time * 1000), 'JST', 'yyyy/MM/dd HH:mm:ss')
      });
    }
    
    lastMessageIsMine = isMine;
  });
  
  return unrepliedMessages;
}

// 通知を送信
function sendNotification(room, messages) {
  let message = CONFIG.NOTIFICATION_MESSAGE;
  
  messages.forEach(msg => {
    message += `\n[info][title]${msg.send_time}[/title]`;
    message += `\n${msg.body.replace(/\[.*?\]/g, '').substring(0, 100)}...`;
    message += '\n[/info]\n';
  });
  
  const url = `https://api.chatwork.com/v2/rooms/${room.room_id}/messages`;
  const params = {
    method: 'post',
    payload: {
      body: message,
      self_unread: 0
    }
  };
  
  callChatworkAPI(url, params);
}

// Chatwork APIを呼び出す共通関数
function callChatworkAPI(url, options = {}) {
  const defaultOptions = {
    method: 'get',
    headers: {
      'X-ChatWorkToken': CONFIG.CHATWORK_API_TOKEN
    },
    muteHttpExceptions: true
  };
  
  const mergedOptions = { ...defaultOptions, ...options };
  
  if (mergedOptions.payload) {
    const formData = [];
    for (const key in mergedOptions.payload) {
      formData.push(`${encodeURIComponent(key)}=${encodeURIComponent(mergedOptions.payload[key])}`);
    }
    mergedOptions.payload = formData.join('&');
    mergedOptions.headers['Content-Type'] = 'application/x-www-form-urlencoded';
  }
  
  const response = UrlFetchApp.fetch(url, mergedOptions);
  const responseCode = response.getResponseCode();
  
  if (responseCode !== 200 && responseCode !== 204) {
    throw new Error(`APIエラー: ${responseCode} - ${response.getContentText()}`);
  }
  
  return {
    data: responseCode === 204 ? null : JSON.parse(response.getContentText()),
    headers: response.getHeaders(),
    status: responseCode
  };
}

// テスト用関数
function test() {
  console.log('テストを開始します');
  const result = checkUnrepliedMessages();
  console.log(result);
  return result;
}
```

## 4. コードの設定

1. コード内の以下の部分を編集します：
   - `CHATWORK_API_TOKEN`: 先ほど取得したChatwork APIトークン
   - `SPREADSHEET_URL`: コピーしたスプレッドシートのURL（ブラウザのアドレスバーからコピーしてください）

2. 必要に応じて以下の設定を変更します：
   - `TARGET_DAYS`: 何日前までの未返信をチェックするか（デフォルト: 1日前）
   - `TARGET_ROOMS`: 特定のルームのみを対象にする場合のルームID配列
   - `EXCLUDE_ROOMS`: 通知を除外するルームID配列
   - `NOTIFICATION_MESSAGE`: 通知メッセージのカスタマイズ

## 5. トリガーの設定

1. 左側のメニューから「トリガー」を選択
2. 「トリガーを追加」をクリック
3. 以下のように設定：
   - 実行する関数: `checkUnrepliedMessages`
   - 実行するデプロイ: ヘッド
   - イベントのソース: 時間主導型
   - 時間ベースのトリガーのタイプ: 日付ベースのタイマー
   - 時刻: 午前5時〜6時
4. 「保存」をクリック

## 6. テスト実行

1. コードエディタで「test」関数を選択
2. 「実行」ボタンをクリック
3. 初回は承認が必要なので、表示される手順に従って承認

## カスタマイズ方法

### 通知メッセージを変更する

`NOTIFICATION_MESSAGE`の内容を編集します。Chatworkの記法が使えます。

### 通知タイミングを変更する

トリガー設定で、通知を送信する時間帯を変更できます。

### 特定のルームのみを対象にする

```javascript
// 例: ルームIDが12345678のルームのみを対象にする
TARGET_ROOMS: [12345678],
```

### 特定のルームを除外する

```javascript
// 例: ルームIDが87654321のルームを除外する
EXCLUDE_ROOMS: [87654321],
```

## よくある質問

### Q. 通知が届きません

- APIトークンが正しく設定されているか確認してください
- トリガーが正しく設定されているか確認してください
- スクリプトの実行ログを確認してください

### Q. エラーが発生しました

エラーメッセージを確認してください。主な原因は以下の通りです：

- APIトークンが無効
- スプレッドシートのURLが間違っている
- 権限が不足している

## おわりに

このスクリプトを使うと、Chatworkの返信漏れを防ぐことができます。特に複数のチャットルームを管理している方にはおすすめです。

「もっとこうしてほしい」というご要望や、うまくいかない点があれば、お気軽にコメントください。

---

いかがでしたか？この記事が少しでもお役に立てば幸いです。

何かご質問やご要望がありましたら、お気軽にどうぞ！
