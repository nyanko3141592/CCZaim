# Claude Code で簡単 Zaim 管理 — MoneyForward を卒業した話

## きっかけ

MoneyForwardのプレミアムに3年以上課金していた。年払いで。

銀行・クレカの自動連携は便利だった。でも不満が溜まっていた:

- **API が公開されていない** — 自分のデータなのにプログラムから触れない
- **自動仕分けが微妙** — 結局手動で直す羽目になる
- **高い割にViewer以上の価値がない** — 管理オタクのニーズを満たさない
- **FP無料面談** — FP資格を自分で取った後では物足りない

ある日気づいた。Claude Code に CSV を渡して話すだけで、MoneyForward のプレミアム機能より遥かに高度な分析ができる。

じゃあ、**API がある家計簿アプリ + Claude Code** でよくないか？

Zaim に乗り換えた。API で未分類項目を自動仕分けできて最高だった。

そして作ったのが CCZaim。

## CCZaim とは

**Zaim API のクライアント + Claude Code のスラッシュコマンド**を1つのリポジトリにまとめたもの。

```
クローン → API キー設定 → 認証 → あとは Claude に話しかけるだけ
```

記録は Zaim アプリに任せる。分析は Claude Code に任せる。API で繋ぐ。

### 何ができる？

| やりたいこと | コマンド |
|---|---|
| 今月の家計を一目で把握 | `/dashboard` |
| 「先月のコンビニ代」を調べる | `/zaim-search` |
| 「ランチ1200円」を記録する | `/zaim-add` |
| 未分類の取引を整理する | `/zaim-categorize` |
| 月次・四半期レポートを作る | `/zaim-report` |
| 支出の見直し・貯蓄目標を相談 | `/zaim-fp` |
| カテゴリ別の予算を管理 | `/zaim-budget` |
| 口座一覧を確認 | `/zaim-accounts` |

---

## セットアップ

### 必要なもの

- Python 3.10 以上
- [Zaim アカウント](https://zaim.net/)
- [Zaim Developer アカウント](https://dev.zaim.net/)（API キー取得用）
- [Claude Code](https://claude.ai/code)

### MoneyForward から移行する場合

MoneyForward から CSV エクスポート → Claude Code に「Zaim の連携フォーマットに変換して」と頼めば一発で変換できる。構えるほどの作業ではない。

### 手順

#### 1. クローン

```bash
git clone https://github.com/nyanko3141592/CCZaim.git
cd CCZaim
```

#### 2. 依存パッケージインストール

```bash
pip3 install -r requirements.txt
```

`requests-oauthlib` と `python-dotenv` の2つだけ。

#### 3. Zaim Developer Center でアプリ登録

1. [dev.zaim.net](https://dev.zaim.net/) にアクセス
2. Zaim アカウントでログイン
3. 「新しいアプリケーションを登録」
4. アプリ名は何でもOK（例: `CCZaim`）
5. コールバック URL は `http://localhost`
6. 登録後、**Consumer Key** と **Consumer Secret** をメモ

> Zaim の Developer 登録自体は無料。課金不要。

#### 4. 環境変数を設定

```bash
cp .env.example .env
```

`.env` を開いて Key / Secret を貼り付ける:

```
ZAIM_CONSUMER_KEY=ここにConsumerKey
ZAIM_CONSUMER_SECRET=ここにConsumerSecret
```

#### 5. OAuth 認証

```bash
python3 zaim_client.py auth
```

ブラウザが開く → Zaim にログイン → 「許可」 → リダイレクトされた URL をコピー → ターミナルに貼り付け。

`tokens.json` が保存される（`.gitignore` 済み）。

#### 6. 動作確認

```bash
python3 zaim_client.py user     # ユーザー情報
python3 zaim_client.py money    # 最近の取引
```

データが出たら完了。

---

## 各コマンドの詳細

### `/dashboard` — 今月の家計ダッシュボード

```
> /dashboard
```

今月の全取引を集計して表示:

- **収支サマリー**: 収入・支出・差引
- **カテゴリ別支出**: 棒グラフ付きランキング
- **高額支出 TOP5**
- **日別推移**
- **未分類件数**

表示後、Claude が次のアクションを提案する:

```
ダッシュボードを表示しました。次に何をしますか？
○ 特定カテゴリを深堀り
○ 先月と比較する
○ 未分類を整理する
○ 終了
```

選択肢を選ぶだけでどんどん深堀りできる。MoneyForward の「分析」タブより遥かに柔軟。

> ちなみに Zaim の支出データを Claude Code に分析させたら「Claude Code の利用代金が高いので削りましょう」とアドバイスされた。お前が言うな。

---

### `/zaim-search` — 取引データ検索

自然言語で検索できる。

```
> /zaim-search
> 先月のコンビニ支出
```

こんな聞き方もOK:

- 「3月の食費を調べて」
- 「今月1万円以上の支出」
- 「直近の Amazon 購入」
- 「去年の交際費」

結果は表形式 + 合計サマリー。

```
| 日付 | カテゴリ | ジャンル | 金額 | 場所 | メモ |
|---|---|---|---|---|---|
| 2024-03-05 | 食費 | コンビニ | ¥580 | セブンイレブン | |
| 2024-03-12 | 食費 | コンビニ | ¥1,200 | ファミマ | お弁当 |

合計: ¥4,280（8件）
```

---

### `/zaim-add` — 支出・収入の登録

```
> /zaim-add
> 今日ランチで1200円使った
```

Claude が入力を解析して確認表示:

```
以下の内容で登録します:

| 項目 | 内容 |
|---|---|
| 種別 | 支出 |
| 金額 | ¥1,200 |
| 日付 | 2024-04-04 |
| カテゴリ | 食費 |
| ジャンル | 外食 |

よろしいですか？
```

確認してから登録。誤登録の心配なし。

---

### `/zaim-categorize` — 未分類取引の対話的分類

**これが Zaim + Claude Code の真骨頂。** MoneyForward で手動でやっていた仕分けが、選択肢を選ぶだけで終わる。

```
> /zaim-categorize
```

#### まず進め方を聞かれる

```
未分類が12件あります。どう進めますか？
○ 1件ずつ確認（Recommended）
○ AI提案を一括表示
○ 高額順に上位5件だけ
```

#### 1件ずつの分類フロー

店名と金額からAIがカテゴリを推定、選択肢で確認:

```
「セブンイレブン」¥580（2024-03-05）のカテゴリは？
○ 食費（Recommended） — 店名から推定
○ 日用品 — コンビニで日用品を買った場合
○ スキップ — あとで分類する
```

カテゴリを選ぶと次はジャンル:

```
食費 のジャンルは？
○ コンビニ（Recommended）
○ 食料品
○ その他食費
```

選択するとすぐに Zaim が更新され、次の取引へ。テンポよく進む。

> API で未登録の店舗の場合は辛いこともある。そういう時は Claude Code のデスクトップ版から Web UI を直接触ってもらうという手もある。

---

### `/zaim-report` — 期間レポート生成

```
> /zaim-report
```

#### 期間の選択

```
どの期間のレポートを作りますか？
○ 先月（Recommended）
○ 今月（途中経過）
○ 直近3ヶ月
○ 今年
```

#### 観点の選択（複数選択可）

```
どの観点を重視しますか？
☐ カテゴリ別分析（Recommended）
☐ 前期比較
☐ 高額支出の洗い出し
☐ 日別パターン分析
```

選んだ内容に応じてレポートが生成される:

- **総括**: 収入・支出・差引・件数
- **カテゴリ別支出**: 割合付き棒グラフ
- **前期比較**: 増減と増減率
- **高額支出一覧**
- **日別パターン**: 曜日別平均グラフ
- **AIの所感**: トレンドや改善ポイント

表示後もフォローアップの選択肢が出る。FP相談や予算設定への導線がある。

---

### `/zaim-fp` — FP 相談

ファイナンシャルプランナー的な視点で、実データに基づいたアドバイスをもらえる。

```
> /zaim-fp
```

#### 4つの相談メニュー

```
どんな相談をしますか？
○ 支出の見直し（Recommended）
○ 貯蓄・投資の目標設定
○ 固定費チェック
○ ライフイベント試算
```

#### 支出の見直し

実データから削減余地のあるカテゴリ TOP3 を特定。ジャンル別内訳を見て、具体的な削減目標を対話的に設定:

```
食費が¥38,200（全体の32%）です。内訳を見ますか？
○ ジャンル別の内訳を見る（Recommended）
○ 日別の推移を見る
○ 次のカテゴリへ
```

```
食費の目標を設定しますか？
○ 先月比10%削減（¥34,400/月）（Recommended）
○ 具体的な金額を設定
○ 目標は設定しない
```

#### 貯蓄・投資の目標設定

直近3ヶ月の収支から貯蓄余力を自動計算。目標金額と期間を設定してシミュレーション。

#### 固定費チェック

毎月繰り返し発生している支出を自動検出。通信費・サブスク・保険料を一覧表示し、複数選択で見直し対象を選べる。

#### ライフイベント試算

引っ越し・転職・結婚などの大きな出費を、現在の収支データに基づいて試算。

> MoneyForward の FP 面談は予約して時間を取って...という手間がかかった。Claude Code なら `/zaim-fp` の一言で即座に始まる。しかも自分のリアルなデータに基づいている。

---

### `/zaim-budget` — カテゴリ別予算管理

Zaim API には予算機能がない。CCZaim がローカルの `budget.json` で独自に管理する。

```
> /zaim-budget
```

#### 予算消化チェック

```
## 今月の予算消化状況（4/15時点）

| カテゴリ | 予算 | 実績 | 残り | 消化率 |
|---|---|---|---|---|
| 食費 | ¥40,000 | ¥28,500 | ¥11,500 | 71% ⚠️ ペース超過 |
| 日用品 | ¥10,000 | ¥3,200 | ¥6,800 | 32% ✅ 順調 |
| 趣味 | ¥15,000 | ¥15,800 | -¥800 | 105% 🔴 超過！ |
```

超過があれば対応を聞かれる:

```
趣味が¥800超過しています。どうしますか？
○ 内訳を確認する（Recommended）
○ 今月は許容する
○ 予算を増額する
```

#### 予算の設定

過去の実績ベース・収入からの逆算・手入力の3方式。実績ベースなら、直近3ヶ月の平均からカテゴリごとに提案してくれる。

---

### `/zaim-accounts` — 口座一覧

```
> /zaim-accounts
```

銀行・クレカ・電子マネーの一覧を表示。

---

## CLI 単体でも使える

Claude Code なしでも `zaim_client.py` はコマンドラインツールとして動く。

```bash
python3 zaim_client.py money                                    # 最近の取引
python3 zaim_client.py money --start 2024-01-01 --end 2024-03-31 --all  # 全件取得
python3 zaim_client.py summary --start 2024-01-01               # 月別サマリー
python3 zaim_client.py dashboard                                # 今月ダッシュボード（JSON）
python3 zaim_client.py uncategorized                            # 未分類の取引
python3 zaim_client.py categories                               # カテゴリマスタ
python3 zaim_client.py genres                                   # ジャンルマスタ
python3 zaim_client.py accounts                                 # 口座マスタ
```

ライブラリとしても使える:

```python
import zaim_client

s = zaim_client.get_session()
items = zaim_client.get_all_money(s, "2024-03-01", "2024-03-31")

summary = zaim_client.monthly_summary(items)
breakdown = zaim_client.category_breakdown(items)
```

---

## ファイル構成

```
CCZaim/
├── zaim_client.py              # Zaim API クライアント（コア）
├── CLAUDE.md                   # Claude Code プロジェクト設定
├── README.md
├── .claude/commands/           # スラッシュコマンド（9個）
│   ├── dashboard.md
│   ├── zaim-search.md
│   ├── zaim-add.md
│   ├── zaim-categorize.md
│   ├── zaim-report.md
│   ├── zaim-fp.md
│   ├── zaim-budget.md
│   ├── zaim-accounts.md
│   └── zaim-setup.md
├── docs/
│   ├── zaim-api-guide.md       # Zaim API 解説記事
│   └── cczaim-guide.md         # この記事
├── tests/
│   └── test_client.py          # テスト（20件）
├── requirements.txt
├── .env.example
├── .gitignore
└── LICENSE                     # MIT
```

---

## よくある質問

### Q. Zaim の有料プラン（プレミアム）は必要？

不要。API は無料プランでも使える。

### Q. MoneyForward からの移行は大変？

CSV ダウンロード → Claude Code に変換させるだけ。30分もかからない。

### Q. API キーが漏れたらどうなる？

家計簿データに第三者がアクセスできてしまう。`.env` と `tokens.json` は `.gitignore` 済みだが、取り扱いには注意。わかりやすいから.envにしたけど各自ちゃんと設定をしよう。

### Q. Zaim アプリ側にも反映される？

API で行った操作は即座に反映される。

### Q. 自分でスラッシュコマンドを追加できる？

`.claude/commands/` にマークダウンファイルを置くだけ。`zaim_client.py` の関数を使えばコードもほぼ不要。

### Q. Web UI がシンプルすぎない？

**API があるので問題ない。** 自分好みの UI を作ればいいし、Claude Code 経由なら UI すら不要。データさえ取れればあとは AI の仕事。

---

## まとめ

MoneyForward が悪いサービスとは思わない。でも「自分のデータを自分のプログラムで触りたい」人にとっては、APIがないのは致命的だった。

Zaim + Claude Code にしてから:

- 未分類の仕分けが選択肢を選ぶだけで完了
- 「先月いくら使った？」に即座に回答
- FP相談がコマンド一発で始まる
- 予算管理も対話的にできる
- Claude Code に支出を分析させたら自分の利用代金を削れと言われる

家計簿の「入力」は Zaim アプリに任せて、「分析」は Claude Code に任せる。

リポジトリ: [github.com/nyanko3141592/CCZaim](https://github.com/nyanko3141592/CCZaim)
