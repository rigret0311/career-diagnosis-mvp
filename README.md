# キャリア診断サービス MVP

初心者でもローカルで動かせる、販売用の最小構成MVPです。  
LP表示、診断フォーム、メール取得、3通ステップメール、クリック計測、無料相談希望フォームまでを1つのFlaskアプリでまとめています。

## できること

- 1ページLPを表示
- 9問のキャリア診断フォームに回答
- メールアドレスを含む送信内容を `data/submissions.json` に保存
- SMTP設定があれば診断完了後に自動メール送信
- SMTP未設定でもメール本文をローカル保存して確認可能
- 2通目・3通目の追客メールを1コマンドで送信
- メール内リンクのクリックと無料相談希望を `data/events.json` に保存
- 市場価値ランク、想定年収レンジ、危機感、次アクションを自動表示
- `./start.sh` 1コマンドで起動
- Windowsでは `start.bat` 1コマンドで起動

## フォルダ構成

```text
MVP/
├── .env.example
├── app.py
├── config.py
├── diagnosis.py
├── mailer.py
├── storage.py
├── requirements.txt
├── start.bat
├── start.sh
├── README.md
├── data/
│   ├── events.json
│   └── submissions.json
├── scripts/
│   └── send_due_emails.py
├── static/
│   └── style.css
├── templates/
│   ├── consultation.html
│   ├── consultation_complete.html
│   ├── index.html
│   └── result.html
└── tests/
    └── test_app.py
```

## 起動方法 Mac

ターミナルでこのフォルダに移動して、次の1コマンドを実行してください。

```bash
./start.sh
```

起動後、ブラウザで以下を開きます。

```text
http://127.0.0.1:5000
```

## 起動方法 Windows

エクスプローラーでこのフォルダを開き、`start.bat` をダブルクリックしてください。  
コマンドプロンプトから起動する場合は、次のコマンドを実行します。

```bat
start.bat
```

起動後、ブラウザで以下を開きます。

```text
http://127.0.0.1:5000
```

## 初回起動でやっていること

`./start.sh` と `start.bat` は自動で以下を実行します。

1. `.venv` というPython仮想環境を作成
2. `.env` があれば自動で読み込む
3. 必要なライブラリをインストール
4. Flaskアプリを起動

つまり、基本は `./start.sh` だけで大丈夫です。

## 自動メールを有効にする方法

実メール送信したい場合は、`.env.example` をコピーして `.env` を作ってください。

```bash
cp .env.example .env
```

最低限、以下を設定します。

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_FROM_EMAIL`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_USE_TLS`

設定後に `./start.sh` を実行すると、診断完了後に1通目のメールを自動送信します。

## 自動メールが未設定のとき

`.env` がない場合でもアプリは止まりません。  
その代わり、送信予定のメール本文を次のフォルダに保存します。

```text
data/email_previews/
```

まずは本文を作り込んでから、SMTP設定を足せばすぐ実送信に移れます。

## 2通目・3通目を送る方法

診断後の追客メールは、毎日1回このコマンドを実行すれば送れます。

Mac:

```bash
.venv/bin/python scripts/send_due_emails.py
```

Windows:

```bat
.venv\Scripts\python scripts\send_due_emails.py
```

このコマンドは、`data/submissions.json` の `email_sequence` を見て、期限が来ている `pending` メールだけを送信します。

- 2通目: 診断翌日に送信対象
- 3通目: 診断3日後に送信対象
- SMTP未設定なら `data/email_previews/` に本文を保存
- 送信結果は `email_sequence` に保存

## 手動で起動したい場合

Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
```

## データ保存先

診断フォームの送信内容は次のファイルに保存されます。

```text
data/submissions.json
```

保存される内容:

- 送信日時
- リードID
- メールアドレス
- 入力された回答
- 診断結果
- 推定市場価値ランク
- 推定年収レンジ
- おすすめ職種
- 行動提案
- 3通ステップメールの送信ステータス

クリックや相談希望は次のファイルに保存されます。

```text
data/events.json
```

保存されるイベント:

- `email_click`: メール内リンクのクリック
- `consultation_submit`: 無料相談希望フォームの送信

## テスト方法

自動テストを実行する場合:

```bash
source .venv/bin/activate
python -m unittest tests/test_app.py
```

ローカルSMTPデバッグサーバーでメール送信確認をしたい場合:

```bash
python3 -m smtpd -c DebuggingServer -n 127.0.0.1:1025
```

別ターミナルで `.env` を次のように設定します。

```text
SMTP_HOST=127.0.0.1
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=false
SMTP_USE_SSL=false
SMTP_FROM_EMAIL=test@example.com
SMTP_FROM_NAME=キャリア市場価値診断
REPLY_TO_EMAIL=test@example.com
APP_BASE_URL=http://127.0.0.1:5000
```

その後 `./start.sh` を実行すると、デバッグサーバー側にメール本文が表示されます。

## よくあるエラーと対処

### `permission denied: ./start.sh`

実行権限を付けてください。

```bash
chmod +x start.sh
./start.sh
```

### `python3: command not found`

Python 3 が入っていません。  
MacならPython 3をインストールしてから、もう一度 `./start.sh` を実行してください。

### `Python が見つかりません`

WindowsにPythonが入っていない、またはPATHに登録されていません。  
Python 3をインストールし、インストール時に `Add python.exe to PATH` を有効にしてから `start.bat` を実行してください。

### `No module named venv`

Pythonの仮想環境機能が使えない状態です。  
Python 3 を入れ直すと解決することが多いです。

### ポート5000が使用中

別のアプリが同じポートを使っています。  
`app.py` の最後にある `port=5000` を別の数字に変更してください。たとえば `5001` で動かせます。

### SMTP認証エラーになる

`.env` のユーザー名、パスワード、ポート、TLS設定を見直してください。  
失敗した場合でも、メール本文は `data/email_previews/` に保存されます。

## カスタマイズガイド

### 質問内容を変更したい

`config.py` の `QUESTIONS` を編集します。

- 質問文を変える
- 選択肢を増やす
- テキスト入力を増やす

主に見る場所:

- `label`: 質問文
- `type`: `text` / `email` / `textarea` / `select` / `radio`
- `options`: 選択肢
- `scores`: 診断タイプへの加点

### 診断ロジックを変更したい

`diagnosis.py` を編集します。

主に見る場所:

- `calculate_scores()`: どの回答でどのタイプに点を入れるか
- `pick_dominant_type()`: 同点だったときの決め方
- `build_diagnosis_result()`: 表示する診断結果の組み立て

### 結果テキストを変更したい

`config.py` の `RESULT_TEMPLATES` を編集します。

変更できる内容:

- タイプ名
- 見出し
- 解説文
- 危機感
- 武器化ポイント
- おすすめ職種
- 行動提案

### デザインを変えたい

`static/style.css` を編集します。

LPや結果画面の色・余白・ボタン・カードデザインはここで変更できます。

### メール本文を変えたい

`mailer.py` の `_build_step_one_body()`、`_build_step_two_body()`、`_build_step_three_body()` を編集します。

主に変える場所:

- 件名
- 本文の煽り
- CTA
- 案内リンク
- 返信先メールアドレス

### 追客メールの送信タイミングを変えたい

`app.py` の `_build_email_sequence()` を編集します。

- 1通目: 即時
- 2通目: 現在は翌日
- 3通目: 現在は3日後

## 処理の流れ

```text
トップページ表示
  ↓
フォーム入力
  ↓
/diagnose にPOST
  ↓
サーバーで入力チェック
  ↓
診断ロジックで市場価値ランクと年収レンジを推定
  ↓
lead_idを発行
  ↓
1通目メールを送信またはプレビュー保存
  ↓
2通目・3通目をpendingとして保存
  ↓
結果ページを表示
  ↓
メール内リンクをクリック
  ↓
data/events.json にemail_clickを保存
  ↓
無料相談フォームを送信
  ↓
data/events.json にconsultation_submitを保存
```

## 収益化前提で次にやるとよいこと

- Stripe決済を追加して有料診断化
- 相談希望者に送る個別返信テンプレートを追加
- Googleスプレッドシート連携で分析
- 管理画面を追加して回答一覧を見える化

## 金策までの運用フロー

このMVPは、まず無料診断から初CVを取るための構成です。最初は商品を増やすより、反応がある悩みを見つけることを優先します。

1. SNSやXに診断LPを投稿する
2. 無料診断でメールアドレスを取得する
3. 診断直後の1通目で結果と危機感を送る
4. 毎日1回、追客メール送信コマンドを実行する
5. 2通目・3通目で無料相談フォームへ誘導する
6. `data/events.json` でクリックと相談希望を確認する
7. 相談希望者に個別返信する
8. 初回は無料で悩みを聞く
9. 繰り返し出る悩みを有料商品にする
10. 反応がある商品だけStripe決済を追加する

## 売る商品案

- 職務経歴書添削: 3,000〜10,000円
- 転職ロードマップ作成: 9,800〜29,800円
- 30日伴走: 29,800〜98,000円
- 個別キャリア相談: 30分 3,000〜8,000円

最初は高機能な決済ページより、無料相談から直接提案する方が検証が速いです。

## 見るべき数字

- 診断数: LPからフォーム送信まで進んだ人数
- メール取得数: 有効なメールアドレスを残した人数
- クリック数: メール内リンクを押した人数
- 無料相談CV数: 相談フォームを送信した人数
- 個別返信数: 実際に返信・会話できた人数
- 有料化候補数: お金を払ってでも解決したい悩みの件数

## GitHub公開前チェック

公開前に以下を確認してください。

- `.env` が存在してもGitに含めない
- `.venv/` をGitに含めない
- `data/email_previews/` をGitに含めない
- `data/submissions.json` は `[]` の状態にする
- `data/events.json` は `[]` の状態にする
- SMTPのパスワードや個人情報をREADMEに書かない
- `python -m unittest tests/test_app.py` が通ることを確認する

初回コミットのメッセージ案:

```text
Initial career diagnosis MVP
```
