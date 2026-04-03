# CCZaim

Claude Code から Zaim（家計簿アプリ）を操作するためのツールキット。
クローンして `.env` を設定するだけで、Claude Code 経由で家計データの閲覧・登録・分析ができます。

## Quick Start

```bash
# 1. クローン
git clone https://github.com/nyanko3141592/CCZaim.git
cd CCZaim

# 2. 依存インストール
pip install -r requirements.txt

# 3. API キー設定
cp .env.example .env
# .env を編集して ZAIM_CONSUMER_KEY / ZAIM_CONSUMER_SECRET を設定
# https://dev.zaim.net/ でアプリを登録して取得

# 4. OAuth 認証
python zaim_client.py auth

# 5. Claude Code で使う
claude
# > /dashboard
```

## できること

### スラッシュコマンド

| コマンド | 説明 |
|---|---|
| `/dashboard` | 今月の家計ダッシュボード |
| `/zaim-search` | 「先月のコンビニ」「3月の食費」など自然言語で検索 |
| `/zaim-add` | 「ランチ1200円」で支出を登録 |
| `/zaim-categorize` | 未分類の取引をAIが自動分類提案 |
| `/zaim-report` | 月次・四半期・年次レポート生成 |
| `/zaim-accounts` | 口座一覧の表示 |
| `/zaim-setup` | 初期セットアップガイド |

### 自然言語で何でも聞ける

```
> 今月食費いくら使った？
> 先月と今月の支出を比較して
> 最近Amazonで何買った？
> 未分類の取引を整理して
```

## CLI 単体でも使える

```bash
python zaim_client.py money --start 2024-03-01 --end 2024-03-31 --all
python zaim_client.py summary --start 2024-01-01
python zaim_client.py dashboard
python zaim_client.py uncategorized
python zaim_client.py categories
python zaim_client.py accounts
```

## 必要なもの

- Python 3.10+
- [Zaim アカウント](https://zaim.net/)
- [Zaim Developer アカウント](https://dev.zaim.net/)（API キー取得用）
- [Claude Code](https://claude.ai/code)

## ファイル構成

```
CCZaim/
├── zaim_client.py          # Zaim API クライアント（コア）
├── .claude/commands/       # Claude Code スラッシュコマンド
│   ├── dashboard.md
│   ├── zaim-search.md
│   ├── zaim-add.md
│   ├── zaim-categorize.md
│   ├── zaim-report.md
│   ├── zaim-accounts.md
│   └── zaim-setup.md
├── CLAUDE.md               # Claude Code プロジェクト設定
├── docs/
│   └── zaim-api-guide.md   # Zaim API 解説記事
├── tests/
│   └── test_client.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## License

MIT
