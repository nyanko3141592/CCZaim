# Zaim API でできること — MoneyForward から乗り換えた理由

## この記事の対象読者

「**Zaim の API って、実際どこまでできるの？**」

MoneyForward を使っていて、値上げやカスタマイズ性の限界にモヤモヤしている人。Zaim への移行を検討しているけど、API の中身がよく分からなくて踏み出せない人。あるいは、家計簿データをプログラムから自由に触りたいと思っている人。

この記事はそんなあなたに向けて書いています。

Zaim API の公式ドキュメントはログイン後にしか見られず、情報が散らばっていて全体像を掴みにくい。そこで、[CCZaim](https://github.com/nyanko3141592/CCZaim)（Claude Code から Zaim を操作するOSSツールキット）の開発ドキュメントとして、「何ができて、何ができないのか」を一つの記事にまとめました。

パラメータの型、レスポンスのフィールド名、ページネーションの挙動、ハマりどころまで、すべて2026年4月時点の実測値です。「API があるらしいけど、本当に使えるの？」という疑問に、具体的なコードと実データで答えます。

> **免責事項**: この記事は CCZaim の開発ドキュメントであり、Zaim の公式ドキュメントではありません。API の仕様は予告なく変更される場合があります。正確な情報は [Zaim Developers Center](https://dev.zaim.net/) の公式ドキュメントをご確認ください。

---

## なぜ Zaim なのか

家計簿アプリは色々ある。MoneyForward、Zaim、Moneytree...。
自分はMoneyForwardのプレミアムに3年以上年払いで課金していた。銀行・クレカの自動連携は便利だったが、致命的な問題があった。

**API が公開されていない。**

プレミアムに課金しても、自分のデータをプログラムから触れない。自動仕分けは微妙だし、「管理オタク」のニーズを満たしてくれない。FP無料面談も受けたが、自分でFP資格を取った後では正直物足りなかった。

Zaim に乗り換えた最大の理由は**API があること**。Web UIはシンプルだが、APIがあるなら自分好みのインターフェースを作ればいい。データさえ取れれば、分析はClaude Codeに任せられる。

移行してみたら、APIで未分類項目の自動仕分けができて最高だった。MoneyForwardで手動でやっていた作業が一瞬で終わる。

> MoneyForward から Zaim への移行は、CSV をダウンロードして Claude Code に「Zaim の連携フォーマットに変換して」と頼めば一発。

## Zaim API の基本情報

| 項目 | 内容 |
|---|---|
| ベースURL | `https://api.zaim.net/v2` |
| 認証方式 | OAuth 1.0a（3-legged） |
| データ形式 | JSON |
| 開発者登録 | [Zaim Developers Center](https://dev.zaim.net/) |

Zaim Developers Center でアプリを登録すると、Consumer Key と Consumer Secret が発行されます。
これを使って OAuth 認証を行い、自分のアカウントの家計簿データにアクセスします。

> **注意**: Zaim API の公式ドキュメントはログイン後にのみ閲覧可能です。
> この記事の情報は、公式ドキュメント・各種クライアントライブラリ・実際の API レスポンスを突き合わせて整理したものです。

## 認証フロー

OAuth 1.0a の 3-legged フロー。一回やれば終わり。

```
1. アプリ → Zaim: リクエストトークンを取得
   POST /v2/auth/request

2. ユーザー → Zaim: ブラウザで認証・認可
   https://auth.zaim.net/users/auth?oauth_token=...

3. Zaim → アプリ: コールバックURLに認可コード付きでリダイレクト

4. アプリ → Zaim: アクセストークンを取得
   POST /v2/auth/access
```

一度アクセストークンを取得すれば、ファイルに保存して使い回せる。有効期限は明示されていないが、実用上は長期間有効。

## エンドポイント一覧

### データ取得（GET）

| パス | 説明 | 用途 |
|---|---|---|
| `/v2/home/user/verify` | ユーザー情報 | 認証確認、ユーザーID取得 |
| `/v2/home/money` | 入出金データ一覧 | **メインのデータ取得** |
| `/v2/home/category` | カテゴリマスタ | 支出・収入のカテゴリ一覧 |
| `/v2/home/genre` | ジャンルマスタ | カテゴリの下位分類 |
| `/v2/home/account` | 口座一覧 | 銀行・クレカ・電子マネー |
| `/v2/currency` | 通貨情報 | 通貨コード一覧 |

### データ作成（POST）

| パス | 説明 |
|---|---|
| `/v2/home/money/payment` | 支出の登録 |
| `/v2/home/money/income` | 収入の登録 |
| `/v2/home/money/transfer` | 振替の登録 |

### データ更新（PUT）

| パス | 説明 |
|---|---|
| `/v2/home/money/payment/{id}` | 支出の更新 |
| `/v2/home/money/income/{id}` | 収入の更新 |

### データ削除（DELETE）

| パス | 説明 |
|---|---|
| `/v2/home/money/payment/{id}` | 支出の削除 |
| `/v2/home/money/income/{id}` | 収入の削除 |
| `/v2/home/money/transfer/{id}` | 振替の削除 |

**要するに CRUD 全部揃っている。** MoneyForward にはこれがない。

---

## 各エンドポイントの詳細

### `/v2/home/user/verify` — ユーザー情報

認証が正しく行われているかの確認。最初にこれを叩いてトークンの有効性を確認するのが定番。

```
GET /v2/home/user/verify
```

---

### `/v2/home/money` — 入出金データ

**Zaim API の中核。** 家計簿に記録されたすべての取引（支出・収入・振替）を取得できる。

自動仕分けの起点もここ。未分類の取引を取得 → カテゴリを推定 → `PUT` で更新、というフローが組める。

```
GET /v2/home/money?mapping=1&start_date=2024-03-01&end_date=2024-03-31&limit=100
```

#### リクエストパラメータ

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `mapping` | int | - | `1` を指定するとカテゴリ名・ジャンル名がレスポンスに展開される**はず**だが、環境によっては展開されないことがある。その場合は `/v2/home/category` と `/v2/home/genre` からマスタを取得して自前で結合する |
| `category_id` | int | - | 特定カテゴリの取引だけに絞り込み |
| `genre_id` | int | - | 特定ジャンルの取引だけに絞り込み |
| `type` | string | - | `pay`（支出）/ `income`（収入）/ `transfer`（振替）で絞り込み |
| `start_date` | string | - | 取得開始日。`YYYY-MM-DD` 形式 |
| `end_date` | string | - | 取得終了日。`YYYY-MM-DD` 形式 |
| `limit` | int | - | 1リクエストあたりの取得件数。指定しない場合は全件返る模様（2026年4月実測）。ページネーション時は `100` 程度を指定するのが無難 |
| `page` | int | - | ページ番号。`limit` と組み合わせてページネーションに使う |

#### レスポンス（`mapping=1` 指定時、またはマスタ結合後）

```json
{
  "money": [
    {
      "id": 12345678,
      "mode": "payment",
      "user_id": 1234,
      "date": "2024-03-20",
      "amount": 1200,
      "category_id": 101,
      "category_name": "食費",
      "genre_id": 10102,
      "genre_name": "カフェ",
      "from_account_id": 0,
      "to_account_id": 0,
      "place": "スターバックス",
      "comment": "ラテ",
      "name": "",
      "place_uid": "",
      "receipt_id": 0,
      "active": 1,
      "created": "2024-03-20 12:30:00",
      "currency_code": "JPY"
    }
  ]
}
```

#### レスポンスフィールド解説

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | int | 取引の一意ID。更新・削除時に使う |
| `mode` | string | 取引種別: `payment`（支出）/ `income`（収入）/ `transfer`（振替） |
| `user_id` | int | ユーザーID |
| `date` | string | 取引日（YYYY-MM-DD） |
| `amount` | int | 金額（正の整数） |
| `category_id` | int | カテゴリID |
| `category_name` | string | カテゴリ名（`mapping=1` 時のみ） |
| `genre_id` | int | ジャンルID |
| `genre_name` | string | ジャンル名（`mapping=1` 時のみ） |
| `from_account_id` | int | 出金元の口座ID（0 = 未設定） |
| `to_account_id` | int | 入金先の口座ID（0 = 未設定） |
| `place` | string | 店名・場所 |
| `comment` | string | メモ |
| `name` | string | 品名 |
| `place_uid` | string | 店舗のUID（空文字の場合が多い） |
| `receipt_id` | int | レシートID（レシート撮影時に付与） |
| `active` | int | 有効フラグ（通常は `1`） |
| `created` | string | 作成日時 |
| `currency_code` | string | 通貨コード（通常 `JPY`） |

#### ページネーション

```
GET /v2/home/money?mapping=1&limit=100&page=1  → 1〜100件目
GET /v2/home/money?mapping=1&limit=100&page=2  → 101〜200件目
GET /v2/home/money?mapping=1&limit=100&page=3  → 201〜300件目（0件なら終了）
```

空の配列が返ったら終了。レスポンスに総件数は含まれないため、空になるまでループする。

---

### `/v2/home/category` — カテゴリマスタ

支出・収入それぞれのカテゴリ一覧を取得する。

```
GET /v2/home/category
```

#### 主なデフォルト支出カテゴリ

ユーザーがカスタムカテゴリを追加している場合は異なる。必ず API から取得して使うこと。

| カテゴリ | 説明 |
|---|---|
| 食費 | 食料品・外食・カフェなど |
| 日用品 | 消耗品・ドラッグストアなど |
| 交通費 | 電車・バス・タクシーなど |
| 通信費 | 携帯・インターネット・サブスクなど |
| 教養・教育 | 書籍・セミナーなど |
| 趣味・娯楽 | ゲーム・映画・ガジェットなど |
| 衣服・美容 | 服・美容院など |
| 健康・医療 | 医療費・薬・ジムなど |
| 交際費 | 飲み会・プレゼントなど |
| 特別な支出 | 家具・家電・冠婚葬祭など |
| 住宅 | 家賃・住宅ローンなど |
| 水道・光熱 | 電気・ガス・水道 |

---

### `/v2/home/genre` — ジャンルマスタ

カテゴリの下位分類。例えば「食費」カテゴリには:

- 食料品
- カフェ
- 外食
- コンビニ
- その他食費

支出を登録・更新する際には、カテゴリID **と** ジャンルID の両方が必要。

---

### `/v2/home/account` — 口座一覧

Zaim に登録されている口座（銀行口座・クレジットカード・電子マネーなど）の一覧を取得する。
口座 ID は、支出の登録時に `from_account_id`（どの口座から払ったか）を指定するのに使う。

---

### `/v2/currency` — 通貨情報

利用可能な通貨の一覧。日本国内利用では基本的に `JPY` のみ。

---

## データ操作の詳細

### 支出の登録 — `POST /v2/home/money/payment`

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `category_id` | int | **必須** | カテゴリID |
| `genre_id` | int | **必須** | ジャンルID |
| `amount` | int | **必須** | 金額（正の整数） |
| `date` | string | **必須** | 日付（YYYY-MM-DD） |
| `from_account_id` | int | 任意 | 引き落とし元の口座ID |
| `comment` | string | 任意 | メモ |
| `place` | string | 任意 | 店名・場所 |
| `name` | string | 任意 | 品名 |

> **注意**: POST リクエストではパラメータを **リクエストボディ**（form data）として送るのが正式。Python なら `data=` を使う。`params=`（URLクエリ）でも動作する場合があるが、OAuth 1.0a の署名の一貫性のためにも `data=` を推奨。

### 収入の登録 — `POST /v2/home/money/income`

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `category_id` | int | **必須** | カテゴリID |
| `amount` | int | **必須** | 金額 |
| `date` | string | **必須** | 日付 |
| `to_account_id` | int | 任意 | 入金先の口座ID |
| `comment` | string | 任意 | メモ |

収入の登録では `genre_id` は不要。

### 振替の登録 — `POST /v2/home/money/transfer`

口座間の資金移動を記録する。

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `amount` | int | **必須** | 金額 |
| `date` | string | **必須** | 日付 |
| `from_account_id` | int | **必須**（実質） | 出金元の口座ID。口座IDなしだと400エラーになる（2026年4月実測） |
| `to_account_id` | int | **必須**（実質） | 入金先の口座ID |
| `comment` | string | 任意 | メモ |

### 更新 — `PUT /v2/home/money/{mode}/{id}`

変更したいフィールドだけ送ればOK。**未分類取引の自動仕分けで最も使うエンドポイント。**

よくある使い方:
- 未分類の取引にカテゴリ・ジャンルを付ける
- メモや店名を追記する
- 金額の修正

### 削除 — `DELETE /v2/home/money/{mode}/{id}`

取引を削除する。取り消し不可。

---

## API でできること・できないこと

### できること

- 入出金データの CRUD（取得・作成・更新・削除）
- カテゴリ・ジャンル・口座のマスタ取得
- 日付範囲やカテゴリでの絞り込み
- ページネーションによる全件取得
- 振替（口座間移動）の記録

### できないこと

| 機能 | 状況 | 回避策 |
|---|---|---|
| 月次サマリーの直接取得 | API 未提供 | 生データを取得して自前で集計（Claude Code が得意） |
| 予算の取得・設定 | API 未提供 | ローカルで JSON 管理すれば十分 |
| 繰り返し設定（定期支出） | API 未提供 | — |
| レシート画像の取得 | API 未提供 | `receipt_id` はあるが画像は取れない |
| 他ユーザーのデータ | 自分のデータのみ | — |
| カテゴリ・ジャンルの作成 | 取得のみ | Zaim アプリから作成 |
| 未登録店舗の明細登録 | API だと辛い場合がある | Claude Code のデスクトップ版で Web UI を操作させる手もある |
| 銀行自動連携の管理 | API 未提供 | — |

**「できないこと」のほとんどは、Claude Code を組み合わせれば回避できる。** データさえ取れれば分析・集計は AI の領域。予算管理もローカルの JSON で十分だし、Web UI でしかできない操作はデスクトップ版 Claude Code に触らせればいい。

---

## 実践 Tips

### 1. `mapping=1` は常に付ける

ID だけ返されても使いにくい。`mapping=1` を付けるとカテゴリ名・ジャンル名が展開されるはずだが、**実際には展開されないケースがある**（2026年4月時点で確認）。確実に名前を得たい場合は、`/v2/home/category` と `/v2/home/genre` からマスタを取得して自前で結合する。CCZaim の `enrich_items()` がこれを自動でやっている。

### 2. 全件取得はページネーションで

```python
all_items = []
page = 1
while True:
    data = get_money(session, limit=100, page=page, start_date="2024-01-01")
    items = data.get("money", [])
    if not items:
        break
    all_items.extend(items)
    page += 1
```

### 3. POST は body で送るのが安全

GET はクエリパラメータ、POST/PUT はリクエストボディ。
Python の `requests` なら `data=` を使うのが推奨。`params=` でも動作する場合があるが、OAuth 署名の安定性のために `data=` が無難。

### 4. カテゴリ ID はハードコードしない

ユーザーごとに異なる場合がある。毎回 API から取得してマッピングするのが安全。

### 5. レート制限に注意

公式にレート制限の仕様は公開されていない。ページネーションのループ時は適度に間隔を空けるのが無難。

---

## MoneyForward との比較

| 項目 | MoneyForward | Zaim |
|---|---|---|
| API 公開 | **なし** | **あり（CRUD全部）** |
| 銀行自動連携 | あり | あり |
| 自動仕分け | 微妙 | API + AI で自作可能 |
| 月額費用 | プレミアム: 月500円〜 | 無料プランでもAPI利用可能 |
| Web UI | きれい | シンプル（APIがあれば自分好みにできる） |
| データエクスポート | CSV | CSV + API |
| カスタマイズ性 | 低い | API経由で何でもできる |

MoneyForward が優れているのは Web UI の完成度。でも「自分のデータを自分のプログラムで触りたい」なら Zaim 一択。

---

## 関連リンク

- [Zaim Developers Center](https://dev.zaim.net/) — 公式の開発者ポータル
- [Zaim](https://zaim.net/) — 家計簿アプリ本体
- [CCZaim](https://github.com/nyanko3141592/CCZaim) — Claude Code で Zaim を操作するツールキット
- [pyzaim](https://github.com/liebe-magi/pyzaim) — Python クライアントライブラリ
- [zaim.js](https://github.com/hotchemi/zaim.js/) — Node.js クライアントライブラリ
- [go-zaim](https://github.com/s-sasaki-0529/go-zaim) — Go クライアントライブラリ
