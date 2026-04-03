# Zaim API でできること — Claude Code で家計簿を自動化する

家計簿アプリ「Zaim」には公式の API が用意されています。この記事では Zaim API v2 で何ができるのかを整理し、Claude Code と組み合わせて家計管理を自動化する方法を紹介します。

## Zaim API とは

Zaim API は OAuth 1.0a 認証で利用できる REST API です。自分の家計簿データに対して、取得・登録・更新・削除の操作ができます。

公式: https://dev.zaim.net/

## エンドポイント一覧

### 認証

| メソッド | パス | 説明 |
|---|---|---|
| POST | `/v2/auth/request` | リクエストトークン取得 |
| POST | `/v2/auth/access` | アクセストークン取得 |

OAuth 1.0a の3-legged フローです。一度認証すればトークンを保存して使い回せます。

### データ取得（READ）

| メソッド | パス | 説明 |
|---|---|---|
| GET | `/v2/home/user/verify` | ユーザー情報の確認 |
| GET | `/v2/home/money` | 入出金データの一覧取得 |
| GET | `/v2/home/category` | カテゴリマスタ取得 |
| GET | `/v2/home/genre` | ジャンルマスタ取得 |
| GET | `/v2/home/account` | 口座一覧の取得 |
| GET | `/v2/currency` | 通貨情報の取得 |

### データ操作（CREATE / UPDATE / DELETE）

| メソッド | パス | 説明 |
|---|---|---|
| POST | `/v2/home/money/payment` | 支出の登録 |
| POST | `/v2/home/money/income` | 収入の登録 |
| POST | `/v2/home/money/transfer` | 振替の登録 |
| PUT | `/v2/home/money/payment/{id}` | 支出の更新 |
| PUT | `/v2/home/money/income/{id}` | 収入の更新 |
| DELETE | `/v2/home/money/payment/{id}` | 支出の削除 |
| DELETE | `/v2/home/money/income/{id}` | 収入の削除 |

## 各エンドポイントの詳細

### `/v2/home/money` — 入出金データ

最も使うエンドポイントです。

**パラメータ:**

| パラメータ | 型 | 説明 |
|---|---|---|
| `mapping` | int | `1` でカテゴリ名・ジャンル名を展開して返す |
| `category_id` | int | カテゴリで絞り込み |
| `genre_id` | int | ジャンルで絞り込み |
| `type` | string | `pay`（支出）/ `income`（収入）/ `transfer`（振替） |
| `start_date` | string | 取得開始日（YYYY-MM-DD） |
| `end_date` | string | 取得終了日（YYYY-MM-DD） |
| `limit` | int | 取得件数（デフォルト: 20, 最大: 100） |
| `page` | int | ページ番号 |

**レスポンス例:**

```json
{
  "money": [
    {
      "id": 12345678,
      "mode": "payment",
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
      "active": 1,
      "created": "2024-03-20 12:30:00",
      "currency_code": "JPY"
    }
  ]
}
```

### `/v2/home/category` — カテゴリマスタ

支出・収入それぞれのカテゴリ一覧を返します。

主な支出カテゴリ:
- 食費
- 日用品
- 交通費
- 通信費
- 教養・教育
- 趣味・娯楽
- 衣服・美容
- 健康・医療
- 交際費
- 特別な支出
- 住宅
- 水道・光熱

### `/v2/home/genre` — ジャンルマスタ

カテゴリの下位分類です。たとえば「食費」カテゴリの下に:
- 食料品
- カフェ
- 外食
- コンビニ
- その他食費

### `/v2/home/account` — 口座

登録されている銀行口座、クレジットカード、電子マネーなどの一覧です。

### 支出の登録 — `POST /v2/home/money/payment`

**必須パラメータ:**

| パラメータ | 型 | 説明 |
|---|---|---|
| `category_id` | int | カテゴリID |
| `genre_id` | int | ジャンルID |
| `amount` | int | 金額（正の整数） |
| `date` | string | 日付（YYYY-MM-DD） |

**オプション:**

| パラメータ | 型 | 説明 |
|---|---|---|
| `from_account_id` | int | 引き落とし元の口座ID |
| `comment` | string | メモ |
| `place` | string | 店名・場所 |

### 支出の更新 — `PUT /v2/home/money/payment/{id}`

登録済みの支出データを更新します。変更したいフィールドだけ送れます。
カテゴリの付け替えや、メモの追加などに使います。

## API でできないこと

- **月次サマリーの直接取得** — 自前で集計が必要
- **予算の取得・設定** — API 未提供
- **繰り返し設定の管理** — API 未提供
- **レシート画像の操作** — API 未提供
- **他ユーザーのデータ** — 自分のデータのみ

## Claude Code × Zaim = CCZaim

CCZaim は上記の API をラップして、Claude Code のスラッシュコマンドとして提供するツールキットです。

### `/dashboard` — 今月の家計ダッシュボード

APIから今月のデータを全件取得し、以下を自動集計して表示:
- 収支サマリー（収入・支出・差引）
- カテゴリ別支出ランキング
- 高額支出 TOP10
- 日別推移グラフ
- 未分類件数の通知

### `/zaim-search` — 自然言語検索

「先月のコンビニ代」「3月の食費」のように自然言語で取引を検索。
Claude が日付範囲やカテゴリ条件に変換して API を叩きます。

### `/zaim-add` — 支出・収入の登録

「ランチ1200円」と言うだけで、カテゴリを自動推定して登録。
登録前に必ず確認画面を出します。

### `/zaim-categorize` — 未分類の自動分類

店名やメモから最適なカテゴリを AI が推定。
一括で確認・承認して更新できます。

### `/zaim-report` — レポート生成

月次・四半期・年次のレポートをマークダウン形式で生成。
カテゴリ別割合、推移グラフ、所感まで含む詳細レポートです。

## セットアップ

```bash
git clone https://github.com/nyanko3141592/CCZaim.git
cd CCZaim
pip install -r requirements.txt
cp .env.example .env
# .env に Zaim API キーを設定
python zaim_client.py auth
```

あとは Claude Code を起動して `/dashboard` と打つだけです。

## まとめ

Zaim API は入出金の CRUD + マスタ取得という基本的な機能を提供しています。
月次サマリーや分析機能は API にはありませんが、データさえ取れれば Claude Code が集計・分析・レポート生成を全部やってくれます。

CCZaim を使えば:
- 毎月の家計チェックが `/dashboard` の一言で完了
- 未分類の取引が AI で自動整理
- 「先月いくら使った？」に即座に回答
- 詳細レポートをワンコマンドで生成

家計簿の「入力」はZaimアプリに任せて、「分析」はClaude Codeに任せる。
この組み合わせが今のところ最強です。
