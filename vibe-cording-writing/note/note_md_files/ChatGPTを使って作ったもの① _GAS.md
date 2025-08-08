# ChatGPTを使って作ったもの① #GAS

## 記事内容
Excelやスプシのスキルがごく一般レベルでもChatGPTやAIを使えばいろんなものが作れちゃいます！
今思いつくChatGPTを使って作ったものはこんな感じです。
スプシが変更されたら通知がChatworkへ届くGAS
関数をいろいろ使った自分専用の在庫管理データ
一覧リストと請求書テンプレが連動しているスプシ
Gmailに届いたメール内容がChatWorkへも届くGAS
スプシが変更されたら通知がChatworkへ届くGAS
名前等を自動に差し込んで一斉メールを送れるPython
複数セルの文字をテンプレに差し込んで表示させるExcel
毎日指定時間に自動で必要なCSVデータをダウンロードするPowerAutomate
などなど・・・
今日紹介するのは
「スプシが変更されたら通知がChatworkへ届くGAS」
です。
クライアントさんと共有しているスプレッドシートですが、必要がないときは見ないので、クライアントさんが追加・修正などをした場合、私たちはわからないんですよね。
そのために毎日スプシ見るのも時間の無駄かなと思って、何か変更があれば
Chatworkへ通知が来るようにGASを組んでみました。
スプシの機能でメール通知はありますがメールではなくChatworkへ届けたかったのでGASを使いました。
GASスクリプト例
// スクリプトプロパティからAPIトークンとルームIDを取得
// 事前に「スクリプトプロパティ」にCHATWORK_API_TOKENとCHATWORK_ROOM_IDを設定してください。
var
CHATWORK_API_TOKEN = PropertiesService.getScriptProperties().getProperty(
'CHATWORK_API_TOKEN'
);
var
CHATWORK_ROOM_ID = PropertiesService.getScriptProperties().getProperty(
'CHATWORK_ROOM_ID'
);
// 通知の再試行回数と間隔
var
MAX_RETRIES =
3
;
var
RETRY_INTERVAL =
5
*
60
*
1000
;
// 5分
// スプレッドシート全体の編集を監視して通知を送信
function
onEdit
(
e
)
{
if
(!e || e.authMode === ScriptApp.AuthMode.NONE) {
    Logger.log(
'シンプルなトリガーまたは手動実行です。処理を終了します。'
);
return
;
  }
try
{
var
sheet = e.source.getActiveSheet();
var
range = e.range;
var
row = range.getRow();
var
column = range.getColumn();
var
newValue = range.getValue();
// 編集されたセルの情報を取得
var
editedCellInfo =
'シート名: '
+ sheet.getName() +
', 行: '
+ row +
', 列: '
+ column +
', 新しい値: '
+ newValue;

    Logger.log(
'編集が検出されました: '
+ editedCellInfo);
// ChatWorkまたはメールで通知を送信
var
message =
'スプレッドシートの内容が変更されました。\n\n'
+ editedCellInfo;
    sendNotificationWithRetry(message);

  }
catch
(error) {
    Logger.log(
'スクリプトの実行中にエラーが発生しました: '
+ error.message);
    sendErrorNotification(error);
  }
}
// 通知を再試行しながら送信
function
sendNotificationWithRetry
(
message, retryCount =
0
)
{
if
(retryCount >= MAX_RETRIES) {
    Logger.log(
'最大再試行回数に達しました。バックアップ通知を送信します。'
);
    sendBackupNotification(message);
return
;
  }
var
result = sendChatworkNotification(CHATWORK_API_TOKEN, CHATWORK_ROOM_ID, message);
if
(!result.success) {
    Logger.log(
'送信が失敗しました。'
+ (retryCount +
1
) +
'回目の再試行を'
+ (RETRY_INTERVAL /
60000
) +
'分後に実行します。'
);
    ScriptApp.newTrigger(
'retryNotification'
)
      .timeBased()
      .after(RETRY_INTERVAL)
      .create();

    PropertiesService.getScriptProperties().setProperties({
'message'
: message,
'retryCount'
: retryCount +
1
});
  }
}
// 再試行トリガーの処理
function
retryNotification
(
)
{
var
props = PropertiesService.getScriptProperties();
var
message = props.getProperty(
'message'
);
var
retryCount =
parseInt
(props.getProperty(
'retryCount'
));

  sendNotificationWithRetry(message, retryCount);
// このトリガーを削除
var
triggers = ScriptApp.getProjectTriggers();
for
(
var
i =
0
; i < triggers.length; i++) {
if
(triggers[i].getHandlerFunction() ===
'retryNotification'
) {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}
// ChatWorkで通知を送信
function
sendChatworkNotification
(
apiToken, roomId, message
)
{
if
(!apiToken || !roomId) {
    Logger.log(
'ChatWork API トークンまたはルームIDが設定されていません。'
);
return
{
success
:
false
,
response
: {
code
:
500
,
body
:
'API token or room ID is not set'
} };
  }
try
{
var
url =
'https://api.chatwork.com/v2/rooms/'
+ roomId +
'/messages'
;
var
options = {
'method'
:
'post'
,
'headers'
: {
'X-ChatWorkToken'
: apiToken
      },
'payload'
: {
'body'
: message
      },
'muteHttpExceptions'
:
true
};

    Logger.log(
'ChatWorkに通知を送信中: '
+ message);
var
response = UrlFetchApp.fetch(url, options);
var
responseCode = response.getResponseCode();
var
responseBody = response.getContentText();
    Logger.log(
'ChatWork APIレスポンス: '
+ responseBody +
'（ステータスコード: '
+ responseCode +
'）'
);
return
{
success
: responseCode ===
200
,
response
: {
code
: responseCode,
body
: responseBody
      }
    };
  }
catch
(error) {
    Logger.log(
'通知の送信中にエラーが発生しました: '
+ error.message);
return
{
success
:
false
,
response
: {
code
:
500
,
body
: error.message
      }
    };
  }
}
// バックアップ通知をメールで送信
function
sendBackupNotification
(
message
)
{
var
recipient =
'backup@example.com'
;
// ダミーのメールアドレス
var
subject =
'ChatWork通知の送信に失敗しました'
;
var
body =
'ChatWorkへの通知送信に失敗しました。以下のメッセージを手動で送信してください：\n\n'
+ message;

  MailApp.sendEmail(recipient, subject, body);
  Logger.log(
'バックアップ通知をメールで送信しました: '
+ recipient);
}
// エラー通知をメールで送信
function
sendErrorNotification
(
error
)
{
var
recipient =
'admin@example.com'
;
// ダミーのメールアドレス
var
subject =
'GASスクリプトでエラーが発生しました'
;
var
body =
'スクリプトの実行中に以下のエラーが発生しました：\n\n'
+ error.message +
'\n\nスタックトレース：\n'
+ error.stack;

  MailApp.sendEmail(recipient, subject, body);
  Logger.log(
'エラー通知をメールで送信しました: '
+ recipient);
}
copy
これ、ChatGPTが作ってくれました！私が使っているのとはちょっと違うので、もし動作しなかったらすみません。エラーをChatGPTに聞いたら修正してくれるのでぜひやってみてください。
該当のスプシに何か入力するとChatworkに通知が来ますし、加工すれば通知文も好きに指定できます。
私は、
”〇番の請求書を発行する指示が来ました！”
という通知文にして、スタッフと共有しています。
しかもPDFも簡単に出力できるようにもしてあるので、チェックしてクリックするだけで終わり。ホント一瞬で請求書発行が完了します。なので作業は１～5分になりました。
具体的なやり方は、興味がありそうだったらまた解説しますね！

## お知らせ
