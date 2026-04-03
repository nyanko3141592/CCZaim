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
| `/dashboard` | 今月の家計ダッシュボード表示 |
| `/zaim-search` | 取引データ検索 |
| `/zaim-add` | 支出・収入を登録 |
| `/zaim-categorize` | 未分類取引の自動分類 |
| `/zaim-report` | 期間レポート生成 |
| `/zaim-accounts` | 口座一覧表示 |
| `/zaim-setup` | 初期セットアップガイド |

## Claudeへの指示

- `zaim_client.py` を経由して Zaim API を操作する。直接 API を叩かない
- 取引の登録・更新・削除は**必ずユーザーに確認してから**実行する
- 金額は `¥{:,}` 形式で3桁区切り表示する
- データ取得は `python zaim_client.py <command>` のCLIで行う
- ライブラリとして使う場合は `import zaim_client` で各関数を呼ぶ
