# CCZaim — Claude Code × Zaim 家計管理ツール

このリポジトリは Claude Code から Zaim API を操作するためのツールキットです。

## セットアップ

1. `pip install -r requirements.txt`
2. `.env.example` → `.env` にコピーして API キーを設定
3. `python zaim_client.py auth` で OAuth 認証

## コア

- `zaim_client.py` — Zaim API v2 のフル機能クライアント（CLIとしてもライブラリとしても使える）

## スキル一覧

| コマンド | 説明 |
|---|---|
| `/dashboard` | 今月の家計ダッシュボード表示 → 深堀り |
| `/zaim-search` | 取引データ検索 |
| `/zaim-add` | 支出・収入を登録 |
| `/zaim-categorize` | 未分類取引の対話的分類（1件ずつ or 一括） |
| `/zaim-report` | 期間・観点を選んでレポート生成 |
| `/zaim-fp` | FP相談（支出見直し・貯蓄目標・固定費・ライフイベント） |
| `/zaim-budget` | カテゴリ別予算の設定・消化チェック |
| `/zaim-accounts` | 口座一覧表示 |
| `/zaim-setup` | 初期セットアップガイド |

## Claudeへの指示

- `zaim_client.py` を経由して Zaim API を操作する。直接 API を叩かない
- 取引の登録・更新・削除は**必ずユーザーに確認してから**実行する
- 選択肢がある場面では**積極的に AskUserQuestion を使う**（カテゴリ選択、期間選択、深堀り先など）
- AskUserQuestion の第1選択肢はAIの推定ベストを `(Recommended)` 付きで提示する
- 金額は `¥{:,}` 形式で3桁区切り表示する
- データ取得は `python zaim_client.py <command>` のCLIで行う
- ライブラリとして使う場合は `import zaim_client` で各関数を呼ぶ
