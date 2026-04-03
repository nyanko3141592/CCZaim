今月の家計ダッシュボードを表示し、気になるポイントを深堀りします。

## 手順

1. `python3 zaim_client.py dashboard` を実行してJSONデータを取得
2. 結果を以下のフォーマットで見やすく整形して表示:

### 表示フォーマット

```
## {YYYY年M月} 家計ダッシュボード

### 収支サマリー
| 項目 | 金額 |
|---|---|
| 収入 | ¥XXX,XXX |
| 支出 | ¥XXX,XXX |
| 差引 | ¥±XXX,XXX |

### カテゴリ別支出 TOP10
（棒グラフ風にUnicodeブロック文字で可視化）

### 今月の高額支出 TOP5

### 未分類
未分類がX件あります。`/zaim-categorize` で分類できます。
```

3. ダッシュボード表示後、AskUserQuestion で次のアクションを聞く:

```
question: "ダッシュボードを表示しました。次に何をしますか？"
header: "次のアクション"
options:
  - label: "特定カテゴリを深堀り"
    description: "気になるカテゴリのジャンル別内訳・日別推移を表示"
  - label: "先月と比較する"
    description: "前月比の増減を分析"
  - label: "未分類を整理する"
    description: "/zaim-categorize で未分類取引を分類"
  - label: "終了"
    description: "ダッシュボードを閉じる"
```

4. 「特定カテゴリを深堀り」が選ばれたら、支出上位カテゴリを AskUserQuestion で選ばせる:

```
question: "どのカテゴリを深堀りしますか？"
header: "カテゴリ"
options:
  - label: "食費 ¥{金額}"
    description: "全体の{割合}%"
  - label: "趣味・娯楽 ¥{金額}"
    description: "全体の{割合}%"
  - label: "日用品 ¥{金額}"
    description: "全体の{割合}%"
```

→ 選んだカテゴリのジャンル別内訳 + 個別取引を表示

## 注意
- 金額は3桁区切りで表示
- ネガティブな差引はそのまま表示（赤字であることを明記）
