指定期間の家計レポートを生成します。AskUserQuestion で条件をヒアリングしてから生成します。

## ステップ1: 期間選択

AskUserQuestion で対象期間を確認:

```
question: "どの期間のレポートを作りますか？"
header: "期間"
options:
  - label: "先月（Recommended）"
    description: "前月1ヶ月分の詳細レポート"
  - label: "今月（途中経過）"
    description: "今月1日〜今日まで"
  - label: "直近3ヶ月"
    description: "月別推移も含めたトレンド分析"
  - label: "今年"
    description: "年初から今日までの累計"
```

## ステップ2: レポートの観点

```
question: "どの観点を重視しますか？"
header: "観点"
multiSelect: true
options:
  - label: "カテゴリ別分析（Recommended）"
    description: "何にいくら使っているか"
  - label: "前期比較"
    description: "前月・前年同月との増減"
  - label: "高額支出の洗い出し"
    description: "大きな出費を一覧表示"
  - label: "日別パターン分析"
    description: "曜日・日付ごとの支出傾向"
```

## ステップ3: データ取得 & レポート生成

`python3 zaim_client.py money --start YYYY-MM-DD --end YYYY-MM-DD --all` でデータ取得。
選択された観点に応じてレポートを構成:

### レポートフォーマット

```markdown
# 家計レポート: {期間}

## 総括
- 総収入: ¥XXX,XXX
- 総支出: ��XXX,XXX
- 収支差: ¥±XXX,XXX
- 取引件数: N件

## カテゴリ別支出（選択時）
| カテゴリ | 金額 | 割合 | ██████ |
|---|---|---|---|

## 前期比較（選択時）
| カテゴリ | 今期 | 前期 | 増減 | 増減率 |
|---|---|---|---|---|

## 高額支出 TOP10（選択時）

## 日別パターン（選択時）
（曜日別平均、Unicode文字でミニグラフ表示）

## AIの所感
（データから読み取れるトレンドや改善ポイント）
```

## ステップ4: フォローアップ

レポート表示後:

```
question: "レポートを見て気になった点はありますか？"
header: "フォロー"
options:
  - label: "特定カテゴリを深堀り"
    description: "ジャンル別の内訳を詳細表示"
  - label: "FP相談に進む"
    description: "/zaim-fp で改善提案を受ける"
  - label: "予算を設定する"
    description: "/zaim-budget でカテゴリ別予算を管理"
  - label: "終了"
    description: "レポートを閉じる"
```

## 注意
- 金額は全て3桁区切り
- 割合は小数第1位まで
- グラフはUnicodeブロック文字（▏▎▍▌▋▊▉█）で表現
