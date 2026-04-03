# Zaim API でできること

家計簿アプリ「[Zaim](https://zaim.net/)」には、公式の REST API が用意されています。
この記事では Zaim API v2 の全体像を整理します。「API で何ができて、何ができないのか」を把握することが目的です。

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

Zaim API は OAuth 1.0a の 3-legged フローを採用しています。

```
1. アプリ → Zaim: リクエストトークンを取得
   POST /v2/auth/request

2. ユーザー → Zaim: ブラウザで認証・認可
   https://auth.zaim.net/users/auth?oauth_token=...

3. Zaim → アプリ: コールバックURLに認可コード付きでリダイレクト

4. アプリ → Zaim: アクセストークンを取得
   POST /v2/auth/access
```

一度アクセストークンを取得すれば、ファイルに保存して使い回せます。有効期限は明示されていませんが、実用上は長期間有効です。

## エンドポイント一覧

### データ取得（GET）

| パス | 説明 | 用途 |
|---|---|---|
| `/v2/home/user/verify` | ユーザー情報 | 認証確認、ユーザーID取得 |
| `/v2/home/money` | 入出金データ一覧 | メインのデータ取得 |
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

---

## 各エンドポイントの詳細

### `/v2/home/user/verify` — ユーザー情報

認証が正しく行われているかの確認に使います。ユーザーID やアカウント情報が返ります。

```
GET /v2/home/user/verify
```

最初にこのエンドポイントを叩いて、トークンが有効かどうかを確認するのが定番の使い方です。

---

### `/v2/home/money` — 入出金データ

**Zaim API の中核となるエンドポイント**です。家計簿に記録されたすべての取引（支出・収入・振替）を取得できます。

```
GET /v2/home/money?mapping=1&start_date=2024-03-01&end_date=2024-03-31&limit=100
```

#### リクエストパラメータ

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `mapping` | int | - | `1` を指定するとカテゴリ名・ジャンル名がレスポンスに展開される。**指定しないと ID のみ**返るため、基本的に常に `1` を指定する |
| `category_id` | int | - | 特定カテゴリの取引だけに絞り込み |
| `genre_id` | int | - | 特定ジャンルの取引だけに絞り込み |
| `type` | string | - | `pay`（支出）/ `income`（収入）/ `transfer`（振替）で絞り込み |
| `start_date` | string | - | 取得開始日。`YYYY-MM-DD` 形式 |
| `end_date` | string | - | 取得終了日。`YYYY-MM-DD` 形式 |
| `limit` | int | - | 1リクエストあたりの取得件数（実測ではデフォルト20程度、最大100程度。公式ドキュメント非公開のため正確な値は要確認） |
| `page` | int | - | ページ番号。`limit` と組み合わせてページネーションに使う |

#### レスポンス（`mapping=1` 指定時）

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
| `receipt_id` | int | レシートID（レシート撮影時に付与） |
| `active` | int | 有効フラグ（通常は `1`） |
| `created` | string | 作成日時 |
| `currency_code` | string | 通貨コード（通常 `JPY`） |

#### ページネーション

`limit` と `page` を組み合わせてページネーションを行います。

```
GET /v2/home/money?mapping=1&limit=100&page=1  → 1〜100件目
GET /v2/home/money?mapping=1&limit=100&page=2  → 101〜200件目
GET /v2/home/money?mapping=1&limit=100&page=3  → 201〜300件目（0件なら終了）
```

**空の配列が返ったらそれ以上のデータはありません。** レスポンスに総件数やページ数は含まれないため、空になるまでループする必要があります。

---

### `/v2/home/category` — カテゴリマスタ

支出・収入それぞれのカテゴリ一覧を取得します。

```
GET /v2/home/category
```

#### 主なデフォルト支出カテゴリ

ユーザーがカスタムカテゴリを追加している場合、この一覧とは異なります。
必ず API から取得して使ってください。

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

#### 主なデフォルト収入カテゴリ

| カテゴリ | 説明 |
|---|---|
| 給与 | 月給・ボーナス |
| 臨時収入 | 一時的な収入 |
| 投資 | 配当・売却益 |

---

### `/v2/home/genre` — ジャンルマスタ

カテゴリの下位分類（ジャンル）の一覧です。

```
GET /v2/home/genre
```

ジャンルは各カテゴリに紐づいています。例えば「食費」カテゴリには以下のジャンルがあります:

- 食料品
- カフェ
- 外食
- コンビニ
- その他食費

支出を登録・更新する際には、カテゴリID **と** ジャンルID の両方が必要です。ジャンルがどのカテゴリに属するかは、このエンドポイントのレスポンスで確認できます。

---

### `/v2/home/account` — 口座一覧

Zaim に登録されている口座（銀行口座・クレジットカード・電子マネーなど）の一覧を取得します。

```
GET /v2/home/account
```

口座 ID は、支出の登録時に `from_account_id`（どの口座から払ったか）を指定するのに使います。

---

### `/v2/currency` — 通貨情報

利用可能な通貨の一覧です。日本国内利用では基本的に `JPY` のみですが、海外旅行時の外貨記録に使えます。

```
GET /v2/currency
```

---

## データ操作の詳細

### 支出の登録 — `POST /v2/home/money/payment`

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `category_id` | int | **必須** | カテゴリID（`/v2/home/category` で取得） |
| `genre_id` | int | **必須** | ジャンルID（`/v2/home/genre` で取得） |
| `amount` | int | **必須** | 金額（正の整数） |
| `date` | string | **必須** | 日付（YYYY-MM-DD） |
| `from_account_id` | int | 任意 | 引き落とし元の口座ID |
| `comment` | string | 任意 | メモ（自由テキスト） |
| `place` | string | 任意 | 店名・場所 |
| `name` | string | 任意 | 品名 |

> **注意**: POST リクエストではパラメータを URL クエリではなく **リクエストボディ**（form data）として送る必要があります。

### 収入の登録 — `POST /v2/home/money/income`

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `category_id` | int | **必須** | カテゴリID |
| `amount` | int | **必須** | 金額（正の整数） |
| `date` | string | **必須** | 日付（YYYY-MM-DD） |
| `to_account_id` | int | 任意 | 入金先の口座ID |
| `comment` | string | 任意 | メモ |

収入の登録では `genre_id` は不要です。

### 振替の登録 — `POST /v2/home/money/transfer`

口座間の資金移動を記録します。

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `amount` | int | **必須** | 金額 |
| `date` | string | **必須** | 日付 |
| `from_account_id` | int | 任意 | 出金元の口座ID |
| `to_account_id` | int | 任意 | 入金先の口座ID |
| `comment` | string | 任意 | メモ |

### 支出の更新 — `PUT /v2/home/money/payment/{id}`

登録済みの支出を更新します。**変更したいフィールドだけ送ればOK**です。

よくある使い方:
- 未分類の取引にカテゴリ・ジャンルを付ける
- メモや店名を追記する
- 金額の修正

### 収入の更新 — `PUT /v2/home/money/income/{id}`

支出の更新と同様です。

### 削除 — `DELETE /v2/home/money/{mode}/{id}`

取引を削除します。`{mode}` は `payment` または `income` です。

> **注意**: 削除は取り消せません。

---

## API でできること・できないことまとめ

### できること

- 入出金データの CRUD（取得・作成・更新・削除）
- カテゴリ・ジャンル・口座のマスタ取得
- 日付範囲やカテゴリでの絞り込み検索
- ページネーションによる全件取得
- 振替（口座間移動）の記録

### できないこと

| 機能 | 状況 |
|---|---|
| 月次サマリーの直接取得 | API 未提供。生データを取得して自前で集計する必要がある |
| 予算の取得・設定 | API 未提供。Zaim アプリ上では予算機能があるが、API からはアクセスできない |
| 繰り返し設定（定期支出）の管理 | API 未提供 |
| レシート画像の取得・アップロード | API 未提供。`receipt_id` フィールドはあるが、画像本体は取得不可 |
| 他ユーザーのデータ閲覧 | 自分のデータのみ。家族共有的な使い方は API では不可 |
| カテゴリ・ジャンルの作成・編集 | 取得のみ。マスタの変更は Zaim アプリから行う |
| 口座の作成・編集 | 取得のみ |
| Zaim アプリの連携先（銀行自動取得）の管理 | API 未提供 |

---

## API を使う上での Tips

### 1. `mapping=1` は常に付ける

ID だけ返されても人間には意味がわかりません。`mapping=1` を付けるとカテゴリ名・ジャンル名が展開されるので、常に指定しましょう。

### 2. 全件取得はページネーションで

1回のリクエストで取得できる件数には上限があります。月をまたぐデータや大量の取引がある場合は、`page` パラメータを使ってループ取得します。

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

### 3. POST は body で送る

GET のクエリパラメータとは違い、POST/PUT のパラメータはリクエストボディ（form data）として送ります。Python の `requests` ライブラリなら `params=` ではなく `data=` を使ってください。

### 4. カテゴリ ID / ジャンル ID はハードコードしない

カテゴリやジャンルの ID はユーザーごとに異なる場合があります。毎回 `/v2/home/category` と `/v2/home/genre` から取得してマッピングするのが安全です。

### 5. レート制限に注意

公式にレート制限の仕様は公開されていませんが、短時間に大量のリクエストを送るとエラーになる場合があります。ページネーションのループ時には適度な間隔を空けるのが無難です。

---

## 関連リンク

- [Zaim Developers Center](https://dev.zaim.net/) — 公式の開発者ポータル
- [Zaim](https://zaim.net/) — 家計簿アプリ本体
- [CCZaim](https://github.com/nyanko3141592/CCZaim) — Claude Code で Zaim を操作するツールキット
- [pyzaim](https://github.com/liebe-magi/pyzaim) — Python クライアントライブラリ
- [zaim.js](https://github.com/hotchemi/zaim.js/) — Node.js クライアントライブラリ
- [go-zaim](https://github.com/s-sasaki-0529/go-zaim) — Go クライアントライブラリ
