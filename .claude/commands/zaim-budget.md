カテゴリ別の月額予算を設定・管理します。AskUserQuestion で対話的に進めます。

## 起動時

まず AskUserQuestion でモードを選択:

```
question: "予算管理で何をしますか？"
header: "予算"
options:
  - label: "今月の予算消化チェック（Recommended）"
    description: "設定済みの予算に対する今月の進捗を表示"
  - label: "予算を新規設定"
    description: "カテゴリ別の月額予算をゼロから設定"
  - label: "予算を調整"
    description: "既存の予算を変更"
```

---

## 予算消化チェック

1. `budget.json` から設定済みの予算を読み込み
2. `python3 zaim_client.py dashboard` で今月のカテゴリ別支出を取得
3. 各カテゴリの消化率を計算して表示:

```
## 今月の予算消化状況（{月/日}時点）

| カテゴリ | 予算 | 実績 | 残り | 消化率 | ステータス |
|---|---|---|---|---|---|
| 食費 | ¥40,000 | ¥28,500 | ¥11,500 | 71% | ██████▏　 ⚠️ ペース超過 |
| 日用品 | ¥10,000 | ¥3,200 | ¥6,800 | 32% | ███▏　　　 ✅ 順調 |
| 趣味 | ¥15,000 | ¥15,800 | -¥800 | 105% | ██████████ 🔴 超過！ |
```

4. 超過・ペース超過のカテゴリがあれば AskUserQuestion で対応を聞く:

```
question: "趣味が¥800超過しています。どうしますか？"
header: "超過対応"
options:
  - label: "内訳を確認する（Recommended）"
    description: "趣味カテゴリの取引を詳細表示"
  - label: "今月は許容する"
    description: "今回は超過を受け入れる"
  - label: "予算を増額する"
    description: "趣味の月額予算を見直す"
```

---

## 予算の新規設定

### ステップ1: 設定方式

```
question: "予算の設定方式を選んでください"
header: "方式"
options:
  - label: "過去の実績ベース（Recommended）"
    description: "直近3ヶ月の平均支出を元に提案"
  - label: "収入からの逆算"
    description: "手取り月収から貯蓄目標を引いて配分"
  - label: "ゼロから手入力"
    description: "全カテゴリを自分で設定"
```

### ステップ2（実績ベースの場合）

直近3ヶ月のカテゴリ別平均を計算し、各カテゴリについて AskUserQuestion:

```
question: "食費: 過去3ヶ月平均 ¥38,200。予算をいくらにしますか？"
header: "食費"
options:
  - label: "¥40,000（平均+5%の余裕）（Recommended）"
    description: "現状維持ペース"
  - label: "¥35,000（平均-8%）"
    description: "少し引き締める"
  - label: "¥30,000（平均-21%）"
    description: "かなり引き締める"
```

### ステップ2（収入逆算の場合）

```
question: "手取り月収はいくらですか？"
header: "月収"
options:
  - label: "25万円"
  - label: "30万円"
  - label: "35万円"
  - label: "40万円"
```

→ 貯蓄目標を聞く → 残りを一般的な割合で配分提案

### ステップ3: 確定 & 保存

設定した予算を `budget.json` に保存:

```json
{
  "month": "2024-04",
  "budgets": {
    "食費": 40000,
    "日用品": 10000,
    "交通費": 8000,
    "通信費": 5000,
    "趣味・娯楽": 15000
  },
  "savings_target": 50000
}
```

---

## 予算の調整

1. 現在の予算と直近の実績を並べて表示
2. 調整したいカテゴリを AskUserQuestion (multiSelect) で選択
3. 各カテゴリの新しい予算を AskUserQuestion で設定
4. `budget.json` を更新

## 注意
- `budget.json` が存在しない場合は新規設定フローへ誘導
- 予算はZaim API側には保存しない（Zaimに予算APIがないため）
- ローカルの `budget.json` で管理する
