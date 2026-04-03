FP（ファイナンシャルプランナー）視点で家計を分析・アドバイスします。
AskUserQuestion を多用して、対話的にユーザーの状況を把握しながら進めます。

## 起動時

まず AskUserQuestion で相談内容を特定する:

```
question: "どんな相談をしますか？"
header: "相談内容"
options:
  - label: "支出の見直し（Recommended）"
    description: "今月・先月のデータを分析して削減ポイントを提案"
  - label: "貯蓄・投資の目標設定"
    description: "目標額と期間から毎月の必要貯蓄額を計算"
  - label: "固定費チェック"
    description: "通信費・サブスク・保険料など固定費を洗い出し"
  - label: "ライフイベント試算"
    description: "引っ越し・転職・結婚など大きな出費の試算"
```

---

## A: 支出の見直し

### ステップ1: 期間選択

```
question: "どの期間を分析しますか？"
header: "分析期間"
options:
  - label: "今月（Recommended）"
    description: "今月1日〜今日までのデータ"
  - label: "先月"
    description: "先月1ヶ月分"
  - label: "直近3ヶ月"
    description: "トレンドも含めて分析"
```

### ステップ2: データ取得 & 分析

`python3 zaim_client.py money --start ... --end ... --all` でデータ取得し、以下を算出:
- カテゴリ別支出とその割合
- 前月比の増減
- 日別の支出パターン（平日 vs 週末）

### ステップ3: 改善ポイント提示

分析結果を踏まえて、削減余地のあるカテゴリ TOP3 を特定。
各カテゴリについて AskUserQuestion で深堀り:

```
question: "食費が¥{金額}（全体の{割合}%）です。内訳を見ますか？"
header: "食費分析"
options:
  - label: "ジャンル別の内訳を見る（Recommended）"
    description: "外食・コンビニ・カフェなどの詳細"
  - label: "日別の推移を見る"
    description: "どの日に多く使っているか"
  - label: "次のカテゴリへ"
    description: "食費はスキップして次の改善ポイントへ"
```

### ステップ4: 目標設定

```
question: "食費の目標を設定しますか？"
header: "目標設定"
options:
  - label: "先月比10%削減（Recommended）"
    description: "¥{目標金額}/月 を目標に"
  - label: "具体的な金額を設定"
    description: "自分で月額予算を指定"
  - label: "目標は設定しない"
    description: "参考情報として把握するだけ"
```

---

## B: 貯蓄・投資の目標設定

### ステップ1: 目的の確認

```
question: "貯蓄・投資の目的は？"
header: "目的"
options:
  - label: "生活防衛資金"
    description: "月収の3〜6ヶ月分を確保"
  - label: "大きな買い物"
    description: "車・家電・旅行など具体的な購入"
  - label: "長期資産形成"
    description: "老後・FIRE・資産運用"
  - label: "とりあえず貯めたい"
    description: "目的は決まっていないが貯蓄を増やしたい"
```

### ステップ2: 現状把握

直近3ヶ月の収支データから:
- 平均月収
- 平均月支出
- 平均貯蓄余力（収入 - 支出）

を自動計算して表示。

### ステップ3: 目標金額と期間

AskUserQuestion で目標金額を確認（選択肢 + Other で自由入力）:

```
question: "目標金額は？"
header: "目標額"
options:
  - label: "50万円"
    description: "生活防衛資金の目安（月収の3ヶ月分程度）"
  - label: "100万円"
    description: "中期的な貯蓄目標"
  - label: "300万円"
    description: "大きな買い物や投資の元手"
```

### ステップ4: シミュレーション結果

現在の貯蓄ペースで目標達成までの月数を計算。
削減提案がある場合は、削減後のペースも併記。

---

## C: 固定費チェック

### ステップ1: データ取得

直近3ヶ月のデータから、毎月繰り返し発生している支出を自動検出:
- 同じ金額が毎月ある → 固定費候補
- 同じ店名/カテゴリが毎月ある → 固定費候補

### ステップ2: 固定費一覧を表示

検出した固定費を一覧表示後、AskUserQuestion で深堀り対象を選択:

```
question: "以下の固定費が見つかりました。どれを見直しますか？"
header: "見直し"
multiSelect: true
options:
  - label: "通信費 ¥{金額}/月"
    description: "携帯・インターネットなど"
  - label: "サブスク ¥{金額}/月"
    description: "動画・音楽・アプリなど"
  - label: "保険料 ¥{金額}/月"
    description: "生命保険・医療保険など"
```

### ステップ3: 各固定費の見直し提案

選択された固定費について、一般的な削減アドバイスを提示。

---

## D: ライフイベント試算

### ステップ1: イベント選択

```
question: "どのライフイベントを試算しますか？"
header: "イベント"
options:
  - label: "引っ越し"
    description: "初期費用・家賃変動を試算"
  - label: "転職"
    description: "収入変動・空白期間のリスクを試算"
  - label: "結婚"
    description: "式・新生活の費用を試算"
  - label: "旅行・大型出費"
    description: "一時的な大きな支出を計画"
```

### ステップ2: 条件のヒアリング

各イベントに応じた質問を AskUserQuestion で聞く（例: 引っ越しなら希望家賃帯、転職なら想定年収変動など）。

### ステップ3: 試算結果

現在の収支データと入力条件から、必要な貯蓄額・準備期間を算出。

---

## 全体の注意

- FPのアドバイスは一般的な情報提供であり、個別の投資助言ではないことを冒頭で明記
- 具体的な金融商品の推奨はしない
- データに基づいた客観的な分析を心がける
- AskUserQuestion の選択肢は常に3〜4個 + Other（自由入力）を活用
- 各ステップの結果は簡潔にサマリーしてから次に進む
