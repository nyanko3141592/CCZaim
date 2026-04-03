#!/usr/bin/env python3
"""CCZaim — Zaim API client for Claude Code.

Full-featured wrapper around Zaim API v2 with OAuth 1.0a authentication.
Designed to be called from Claude Code skills via `python zaim_client.py <command>`.
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

# --- Config ---

ENV_PATH = Path(__file__).parent / ".env"
TOKEN_FILE = Path(__file__).parent / "tokens.json"

load_dotenv(ENV_PATH)

CONSUMER_KEY = os.environ.get("ZAIM_CONSUMER_KEY", "")
CONSUMER_SECRET = os.environ.get("ZAIM_CONSUMER_SECRET", "")

BASE_URL = "https://api.zaim.net/v2"


# --- Auth ---


def authenticate():
    """Perform OAuth 1.0a flow and save tokens."""
    if not CONSUMER_KEY or not CONSUMER_SECRET:
        print("ERROR: ZAIM_CONSUMER_KEY / ZAIM_CONSUMER_SECRET が .env に設定されていません")
        sys.exit(1)

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        callback_uri="http://localhost",
    )
    fetch_response = oauth.fetch_request_token(f"{BASE_URL}/auth/request")
    resource_owner_key = fetch_response["oauth_token"]
    resource_owner_secret = fetch_response["oauth_token_secret"]

    auth_url = oauth.authorization_url("https://auth.zaim.net/users/auth")
    print(f"\n以下のURLをブラウザで開いて認証してください:\n{auth_url}\n")
    webbrowser.open(auth_url)

    redirect_response = input("リダイレクトされたURL全体を貼り付けてください: ")
    oauth_response = oauth.parse_authorization_response(redirect_response)

    oauth = OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=oauth_response["oauth_verifier"],
    )
    tokens = oauth.fetch_access_token(f"{BASE_URL}/auth/access")

    TOKEN_FILE.write_text(json.dumps(tokens, indent=2))
    print(f"トークンを {TOKEN_FILE} に保存しました。")
    return tokens


def get_session():
    """Return an authenticated OAuth1Session."""
    if TOKEN_FILE.exists():
        tokens = json.loads(TOKEN_FILE.read_text())
    else:
        tokens = authenticate()

    return OAuth1Session(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=tokens["oauth_token"],
        resource_owner_secret=tokens["oauth_token_secret"],
    )


# --- API Methods ---


def verify_user(session):
    """GET /v2/home/user/verify"""
    resp = session.get(f"{BASE_URL}/home/user/verify")
    resp.raise_for_status()
    return resp.json()


def get_money(session, **params):
    """GET /v2/home/money

    Params:
        mapping (int): 1 でカテゴリ名等を展開
        category_id (int): カテゴリで絞り込み
        genre_id (int): ジャンルで絞り込み
        type (str): pay / income / transfer
        start_date (str): YYYY-MM-DD
        end_date (str): YYYY-MM-DD
        limit (int): 取得件数 (default: 100)
        page (int): ページ番号
    """
    params.setdefault("mapping", 1)
    params.setdefault("limit", 100)
    resp = session.get(f"{BASE_URL}/home/money", params=params)
    resp.raise_for_status()
    return resp.json()


def get_all_money(session, start_date=None, end_date=None):
    """全件取得（ページネーション自動処理）"""
    all_items = []
    page = 1
    while True:
        params = {"mapping": 1, "limit": 100, "page": page}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = get_money(session, **params)
        items = data.get("money", [])
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items


def get_categories(session):
    """GET /v2/home/category"""
    resp = session.get(f"{BASE_URL}/home/category")
    resp.raise_for_status()
    return resp.json()


def get_genres(session):
    """GET /v2/home/genre"""
    resp = session.get(f"{BASE_URL}/home/genre")
    resp.raise_for_status()
    return resp.json()


def get_accounts(session):
    """GET /v2/home/account"""
    resp = session.get(f"{BASE_URL}/home/account")
    resp.raise_for_status()
    return resp.json()


def get_currencies(session):
    """GET /v2/currency"""
    resp = session.get(f"{BASE_URL}/currency")
    resp.raise_for_status()
    return resp.json()


def create_payment(session, category_id, genre_id, amount, date, *, comment="", from_account_id=None, place=""):
    """POST /v2/home/money/payment"""
    data = {
        "mapping": 1,
        "category_id": category_id,
        "genre_id": genre_id,
        "amount": amount,
        "date": date,
    }
    if comment:
        data["comment"] = comment
    if from_account_id:
        data["from_account_id"] = from_account_id
    if place:
        data["place"] = place
    resp = session.post(f"{BASE_URL}/home/money/payment", data=data)
    resp.raise_for_status()
    return resp.json()


def create_income(session, category_id, amount, date, *, comment="", to_account_id=None):
    """POST /v2/home/money/income"""
    data = {
        "mapping": 1,
        "category_id": category_id,
        "amount": amount,
        "date": date,
    }
    if comment:
        data["comment"] = comment
    if to_account_id:
        data["to_account_id"] = to_account_id
    resp = session.post(f"{BASE_URL}/home/money/income", data=data)
    resp.raise_for_status()
    return resp.json()


def create_transfer(session, amount, date, *, from_account_id=None, to_account_id=None, comment=""):
    """POST /v2/home/money/transfer"""
    data = {
        "mapping": 1,
        "amount": amount,
        "date": date,
    }
    if from_account_id:
        data["from_account_id"] = from_account_id
    if to_account_id:
        data["to_account_id"] = to_account_id
    if comment:
        data["comment"] = comment
    resp = session.post(f"{BASE_URL}/home/money/transfer", data=data)
    resp.raise_for_status()
    return resp.json()


def update_payment(session, money_id, **fields):
    """PUT /v2/home/money/payment/{id}"""
    fields["mapping"] = 1
    resp = session.put(f"{BASE_URL}/home/money/payment/{money_id}", data=fields)
    resp.raise_for_status()
    return resp.json()


def update_income(session, money_id, **fields):
    """PUT /v2/home/money/income/{id}"""
    fields["mapping"] = 1
    resp = session.put(f"{BASE_URL}/home/money/income/{money_id}", data=fields)
    resp.raise_for_status()
    return resp.json()


def delete_money(session, money_id, mode="payment"):
    """DELETE /v2/home/money/{mode}/{id}"""
    resp = session.delete(f"{BASE_URL}/home/money/{mode}/{money_id}")
    resp.raise_for_status()
    return resp.json()


# --- Aggregation Helpers ---


def monthly_summary(items):
    """月別の収支サマリーを生成"""
    summary = {}
    for item in items:
        month = item.get("date", "")[:7]  # YYYY-MM
        if not month:
            continue
        if month not in summary:
            summary[month] = {"income": 0, "payment": 0, "transfer": 0}
        mode = item.get("mode", "")
        amount = int(item.get("amount", 0))
        if mode == "income":
            summary[month]["income"] += amount
        elif mode == "payment":
            summary[month]["payment"] += amount
        elif mode == "transfer":
            summary[month]["transfer"] += amount
    return dict(sorted(summary.items()))


def category_breakdown(items, mode="payment"):
    """カテゴリ別の内訳を生成"""
    breakdown = {}
    for item in items:
        if item.get("mode") != mode:
            continue
        cat = item.get("category_name", item.get("category_id", "不明"))
        amount = int(item.get("amount", 0))
        breakdown[cat] = breakdown.get(cat, 0) + amount
    return dict(sorted(breakdown.items(), key=lambda x: -x[1]))


def genre_breakdown(items, mode="payment"):
    """ジャンル別の内訳を生成"""
    breakdown = {}
    for item in items:
        if item.get("mode") != mode:
            continue
        genre = item.get("genre_name", item.get("genre_id", "不明"))
        amount = int(item.get("amount", 0))
        breakdown[genre] = breakdown.get(genre, 0) + amount
    return dict(sorted(breakdown.items(), key=lambda x: -x[1]))


def find_uncategorized(items):
    """未分類の取引を抽出"""
    return [
        item for item in items
        if item.get("mode") == "payment"
        and (not item.get("category_id") or item.get("category_name") in ("未分類", ""))
    ]


def top_expenses(items, n=20):
    """支出の高額順トップN"""
    payments = [i for i in items if i.get("mode") == "payment"]
    return sorted(payments, key=lambda x: -int(x.get("amount", 0)))[:n]


def daily_totals(items, mode="payment"):
    """日別の合計"""
    totals = {}
    for item in items:
        if item.get("mode") != mode:
            continue
        date = item.get("date", "")
        amount = int(item.get("amount", 0))
        totals[date] = totals.get(date, 0) + amount
    return dict(sorted(totals.items()))


# --- CLI ---


def format_money_item(item):
    """取引データを人間が読める形式に整形"""
    mode_label = {"payment": "支出", "income": "収入", "transfer": "振替"}.get(item.get("mode", ""), "?")
    cat = item.get("category_name", "")
    genre = item.get("genre_name", "")
    return (
        f"[{item.get('date', '?')}] {mode_label} "
        f"¥{int(item.get('amount', 0)):,} "
        f"{cat}/{genre} "
        f"{item.get('place', '')} "
        f"{item.get('comment', '')}"
    ).strip()


def cmd_auth(_args):
    authenticate()


def cmd_user(_args):
    s = get_session()
    print(json.dumps(verify_user(s), indent=2, ensure_ascii=False))


def cmd_money(args):
    s = get_session()
    params = {}
    if "--start" in args:
        params["start_date"] = args[args.index("--start") + 1]
    if "--end" in args:
        params["end_date"] = args[args.index("--end") + 1]
    if "--type" in args:
        params["type"] = args[args.index("--type") + 1]
    if "--limit" in args:
        params["limit"] = int(args[args.index("--limit") + 1])
    if "--all" in args:
        items = get_all_money(s, params.get("start_date"), params.get("end_date"))
        for item in items:
            print(format_money_item(item))
        print(f"\n合計 {len(items)} 件")
    elif "--json" in args:
        print(json.dumps(get_money(s, **params), indent=2, ensure_ascii=False))
    else:
        data = get_money(s, **params)
        for item in data.get("money", []):
            print(format_money_item(item))


def cmd_categories(_args):
    s = get_session()
    data = get_categories(s)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_genres(_args):
    s = get_session()
    data = get_genres(s)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_accounts(_args):
    s = get_session()
    data = get_accounts(s)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_summary(args):
    s = get_session()
    # Default: past 3 months
    end = datetime.now()
    start = end - timedelta(days=90)
    if "--start" in args:
        start = datetime.strptime(args[args.index("--start") + 1], "%Y-%m-%d")
    if "--end" in args:
        end = datetime.strptime(args[args.index("--end") + 1], "%Y-%m-%d")

    items = get_all_money(s, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    ms = monthly_summary(items)

    print("=== 月別サマリー ===")
    for month, vals in ms.items():
        net = vals["income"] - vals["payment"]
        print(
            f"{month}: 収入 ¥{vals['income']:,} / 支出 ¥{vals['payment']:,} / "
            f"差引 ¥{net:,}"
        )

    print("\n=== カテゴリ別支出 ===")
    cb = category_breakdown(items)
    for cat, amount in cb.items():
        print(f"  {cat}: ¥{amount:,}")

    print(f"\n合計 {len(items)} 件の取引を集計")


def cmd_dashboard(args):
    """ダッシュボード表示"""
    s = get_session()
    now = datetime.now()
    month_start = now.strftime("%Y-%m-01")
    month_end = now.strftime("%Y-%m-%d")

    items = get_all_money(s, month_start, month_end)
    ms = monthly_summary(items)
    current_month = now.strftime("%Y-%m")

    vals = ms.get(current_month, {"income": 0, "payment": 0, "transfer": 0})
    net = vals["income"] - vals["payment"]

    output = {
        "month": current_month,
        "income": vals["income"],
        "payment": vals["payment"],
        "net": net,
        "transaction_count": len(items),
        "category_breakdown": category_breakdown(items),
        "genre_breakdown": genre_breakdown(items),
        "top_expenses": [
            {
                "date": i.get("date"),
                "amount": int(i.get("amount", 0)),
                "category": i.get("category_name", ""),
                "genre": i.get("genre_name", ""),
                "place": i.get("place", ""),
                "comment": i.get("comment", ""),
            }
            for i in top_expenses(items, 10)
        ],
        "daily_totals": daily_totals(items),
        "uncategorized_count": len(find_uncategorized(items)),
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def cmd_uncategorized(_args):
    """未分類取引を表示"""
    s = get_session()
    now = datetime.now()
    start = (now - timedelta(days=60)).strftime("%Y-%m-%d")
    items = get_all_money(s, start, now.strftime("%Y-%m-%d"))
    uncat = find_uncategorized(items)
    if not uncat:
        print("未分類の取引はありません。")
        return
    print(f"未分類の取引: {len(uncat)} 件\n")
    for item in uncat:
        print(f"  ID:{item.get('id')} {format_money_item(item)}")


COMMANDS = {
    "auth": (cmd_auth, "OAuth認証を実行"),
    "user": (cmd_user, "ユーザー情報を表示"),
    "money": (cmd_money, "取引データを取得 [--start/--end/--type/--limit/--all/--json]"),
    "categories": (cmd_categories, "カテゴリ一覧を表示"),
    "genres": (cmd_genres, "ジャンル一覧を表示"),
    "accounts": (cmd_accounts, "口座一覧を表示"),
    "summary": (cmd_summary, "月別サマリーを表示 [--start/--end]"),
    "dashboard": (cmd_dashboard, "今月のダッシュボード（JSON）"),
    "uncategorized": (cmd_uncategorized, "未分類の取引を表示"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print("CCZaim — Zaim API client for Claude Code\n")
        print("Usage: python zaim_client.py <command> [options]\n")
        print("Commands:")
        for name, (_, desc) in COMMANDS.items():
            print(f"  {name:16s} {desc}")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS.keys())}")
        sys.exit(1)

    COMMANDS[cmd][0](sys.argv[2:])


if __name__ == "__main__":
    main()
