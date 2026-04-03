CCZaimの初期セットアップを行います。

## 手順

1. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

2. `.env` ファイルを作成:
   - `.env.example` をコピーして `.env` を作成
   - ユーザーに Zaim Developer Center (https://dev.zaim.net/) でアプリを登録するよう案内
   - Consumer Key / Secret を `.env` に設定

3. OAuth認証を実行:
```bash
python zaim_client.py auth
```
   - ブラウザが開くので、Zaimにログインして認証
   - リダイレクトURLをターミナルに貼り付け

4. 動作確認:
```bash
python zaim_client.py user
python zaim_client.py money --limit 5
```

5. 完了メッセージ:
```
セットアップ完了です！以下のコマンドが使えます:
- /dashboard — 今月の家計ダッシュボード
- /zaim-search — 取引検索
- /zaim-add — 取引登録
- /zaim-categorize — 未分類の自動分類
- /zaim-report — 期間レポート生成
- /zaim-accounts — 口座一覧
```
