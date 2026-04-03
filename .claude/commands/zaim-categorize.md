未分類の取引を1件ずつインタラクティブに分類します。AskUserQuestion を活用して効率よく進めます。

## 手順

1. `python3 zaim_client.py uncategorized` で未分類取引を取得
2. `python3 zaim_client.py categories` と `python3 zaim_client.py genres` でカテゴリ・ジャンルマスタを取得
3. 未分類が0件なら「未分類の取引はありません」と表示して終了

### 分類フロー（1件ずつ）

各取引について、店名・金額・日付・コメントから最適カテゴリを推定し、**AskUserQuestion で確認する**。

#### ステップA: カテゴリ選択

AskUserQuestion を使い、AIが推定したカテゴリを第1選択肢（Recommended）として提示。
残りの選択肢は金額帯・店名から可能性の高い候補を2〜3個並べる。

```
question: "「{店名}」¥{金額}（{日付}）のカテゴリは？"
header: "カテゴリ"
options:
  - label: "{推定カテゴリ}（Recommended）"
    description: "店名「{店名}」から推定"
  - label: "{候補2}"
    description: "{理由}"
  - label: "{候補3}"
    description: "{理由}"
  - label: "スキップ"
    description: "あとで分類する"
```

#### ステップB: ジャンル選択

カテゴリが決まったら、そのカテゴリ配下のジャンルを AskUserQuestion で選ばせる。

```
question: "{カテゴリ} のジャンルは？"
header: "ジャンル"
options:
  - label: "{推定ジャンル}（Recommended）"
  - label: "{ジャンル候補2}"
  - label: "{ジャンル候補3}"
```

#### ステップC: 更新実行

```python
import zaim_client
s = zaim_client.get_session()
zaim_client.update_payment(s, money_id, category_id=..., genre_id=...)
```

更新したら「{店名} → {カテゴリ}/{ジャンル} に分類しました」と表示して次の取引へ。

### 一括モード

未分類が5件以上ある場合は、最初に AskUserQuestion で進め方を聞く:

```
question: "未分類が{N}件あります。どう進めますか？"
header: "分類方法"
options:
  - label: "1件ずつ確認（Recommended）"
    description: "各取引のカテゴリをひとつずつ選択"
  - label: "AI提案を一括表示"
    description: "全件のAI提案を表で見てからまとめて承認"
  - label: "高額順に上位5件だけ"
    description: "金額が大きいものから優先的に分類"
```

### 分類ルール（AI推定用）

よくある店名→カテゴリのマッピング:
- コンビニ（セブン、ファミマ、ローソン）→ 食費 > コンビニ
- スーパー（まいばすけっと、OK、西友）→ 食費 > 食料品
- ドラッグストア（マツキヨ、ウエルシア）→ 日用品 > ドラッグストア
- カフェ（スタバ、ドトール、タリーズ）→ 食費 > カフェ
- 交通系（Suica、PASMO）→ 交通費 > 電車
- Amazon → 金額・コメントで判断（書籍/ガジェット/日用品を区別）
- 飲食店名 → 食費 > 外食
- 薬局・病院 → 健康・医療

## 注意
- スキップされた取引は最後にまとめてリマインド
- 更新は1件ずつ即座に実行（バッチではなくリアルタイム）
