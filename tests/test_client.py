#!/usr/bin/env python3
"""Tests for zaim_client.py — aggregation helpers and CLI formatting."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import zaim_client


# --- Test data ---

SAMPLE_ITEMS = [
    {
        "id": 1,
        "mode": "payment",
        "date": "2024-03-01",
        "amount": 1200,
        "category_id": 101,
        "category_name": "食費",
        "genre_id": 10102,
        "genre_name": "カフェ",
        "place": "スタバ",
        "comment": "ラテ",
    },
    {
        "id": 2,
        "mode": "payment",
        "date": "2024-03-05",
        "amount": 3500,
        "category_id": 101,
        "category_name": "食費",
        "genre_id": 10101,
        "genre_name": "食料品",
        "place": "まいばすけっと",
        "comment": "",
    },
    {
        "id": 3,
        "mode": "payment",
        "date": "2024-03-10",
        "amount": 15000,
        "category_id": 65832140,
        "category_name": "趣味・娯楽",
        "genre_id": 35738156,
        "genre_name": "ガジェット",
        "place": "Amazon",
        "comment": "USBハブ",
    },
    {
        "id": 4,
        "mode": "income",
        "date": "2024-03-25",
        "amount": 300000,
        "category_id": 11,
        "category_name": "給与",
        "genre_id": 1101,
        "genre_name": "給与",
        "place": "",
        "comment": "3月分給与",
    },
    {
        "id": 5,
        "mode": "payment",
        "date": "2024-04-02",
        "amount": 800,
        "category_id": 101,
        "category_name": "食費",
        "genre_id": 10102,
        "genre_name": "カフェ",
        "place": "ドトール",
        "comment": "",
    },
    {
        "id": 6,
        "mode": "payment",
        "date": "2024-03-15",
        "amount": 2000,
        "category_name": "",
        "genre_name": "",
        "place": "不明な店",
        "comment": "",
    },
    {
        "id": 7,
        "mode": "transfer",
        "date": "2024-03-20",
        "amount": 50000,
        "category_name": "",
        "genre_name": "",
        "place": "",
        "comment": "口座振替",
    },
]


# --- monthly_summary ---


def test_monthly_summary():
    result = zaim_client.monthly_summary(SAMPLE_ITEMS)
    assert "2024-03" in result
    assert "2024-04" in result
    assert result["2024-03"]["income"] == 300000
    assert result["2024-03"]["payment"] == 1200 + 3500 + 15000 + 2000
    assert result["2024-03"]["transfer"] == 50000
    assert result["2024-04"]["payment"] == 800
    print("PASS: test_monthly_summary")


def test_monthly_summary_empty():
    result = zaim_client.monthly_summary([])
    assert result == {}
    print("PASS: test_monthly_summary_empty")


# --- category_breakdown ---


def test_category_breakdown():
    result = zaim_client.category_breakdown(SAMPLE_ITEMS)
    assert "趣味・娯楽" in result
    assert "食費" in result
    # 食費 = 1200 + 3500 + 800 = 5500
    assert result["食費"] == 5500
    assert result["趣味・娯楽"] == 15000
    # Sorted by amount descending
    keys = list(result.keys())
    assert keys[0] == "趣味・娯楽"
    print("PASS: test_category_breakdown")


def test_category_breakdown_income():
    result = zaim_client.category_breakdown(SAMPLE_ITEMS, mode="income")
    assert "給与" in result
    assert result["給与"] == 300000
    print("PASS: test_category_breakdown_income")


# --- genre_breakdown ---


def test_genre_breakdown():
    result = zaim_client.genre_breakdown(SAMPLE_ITEMS)
    assert "カフェ" in result
    # カフェ = 1200 + 800 = 2000
    assert result["カフェ"] == 2000
    assert result["ガジェット"] == 15000
    print("PASS: test_genre_breakdown")


# --- find_uncategorized ---


def test_find_uncategorized():
    result = zaim_client.find_uncategorized(SAMPLE_ITEMS)
    assert len(result) == 1
    assert result[0]["id"] == 6
    print("PASS: test_find_uncategorized")


def test_find_uncategorized_none():
    items = [i for i in SAMPLE_ITEMS if i.get("category_name")]
    result = zaim_client.find_uncategorized(items)
    assert len(result) == 0
    print("PASS: test_find_uncategorized_none")


# --- top_expenses ---


def test_top_expenses():
    result = zaim_client.top_expenses(SAMPLE_ITEMS, n=3)
    assert len(result) == 3
    assert result[0]["amount"] == 15000
    assert result[1]["amount"] == 3500
    assert result[2]["amount"] == 2000
    print("PASS: test_top_expenses")


def test_top_expenses_limit():
    result = zaim_client.top_expenses(SAMPLE_ITEMS, n=1)
    assert len(result) == 1
    assert result[0]["id"] == 3
    print("PASS: test_top_expenses_limit")


# --- daily_totals ---


def test_daily_totals():
    result = zaim_client.daily_totals(SAMPLE_ITEMS)
    assert result["2024-03-01"] == 1200
    assert result["2024-03-05"] == 3500
    assert result["2024-03-10"] == 15000
    assert "2024-03-25" not in result  # income, not payment
    # Keys should be sorted
    keys = list(result.keys())
    assert keys == sorted(keys)
    print("PASS: test_daily_totals")


# --- format_money_item ---


def test_format_money_item():
    result = zaim_client.format_money_item(SAMPLE_ITEMS[0])
    assert "2024-03-01" in result
    assert "支出" in result
    assert "1,200" in result
    assert "食費" in result
    assert "カフェ" in result
    assert "スタバ" in result
    print("PASS: test_format_money_item")


def test_format_money_item_income():
    result = zaim_client.format_money_item(SAMPLE_ITEMS[3])
    assert "収入" in result
    assert "300,000" in result
    print("PASS: test_format_money_item_income")


def test_format_money_item_transfer():
    result = zaim_client.format_money_item(SAMPLE_ITEMS[6])
    assert "振替" in result
    assert "50,000" in result
    print("PASS: test_format_money_item_transfer")


# --- API function signatures (mock tests) ---


def test_get_money_params():
    mock_session = MagicMock()
    mock_session.get.return_value.json.return_value = {"money": []}
    mock_session.get.return_value.raise_for_status = MagicMock()

    zaim_client.get_money(mock_session, start_date="2024-03-01", end_date="2024-03-31", type="pay")

    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args
    assert call_args[0][0] == "https://api.zaim.net/v2/home/money"
    params = call_args[1]["params"]
    assert params["start_date"] == "2024-03-01"
    assert params["end_date"] == "2024-03-31"
    assert params["type"] == "pay"
    assert params["mapping"] == 1
    assert params["limit"] == 100
    print("PASS: test_get_money_params")


def test_create_payment_params():
    mock_session = MagicMock()
    mock_session.post.return_value.json.return_value = {"money": {"id": 999}}
    mock_session.post.return_value.raise_for_status = MagicMock()

    zaim_client.create_payment(
        mock_session,
        category_id=101,
        genre_id=10102,
        amount=1200,
        date="2024-03-20",
        comment="テスト",
        place="テスト店",
    )

    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "https://api.zaim.net/v2/home/money/payment"
    data = call_args[1]["data"]
    assert data["category_id"] == 101
    assert data["genre_id"] == 10102
    assert data["amount"] == 1200
    assert data["date"] == "2024-03-20"
    assert data["comment"] == "テスト"
    assert data["place"] == "テスト店"
    print("PASS: test_create_payment_params")


def test_create_income_params():
    mock_session = MagicMock()
    mock_session.post.return_value.json.return_value = {"money": {"id": 999}}
    mock_session.post.return_value.raise_for_status = MagicMock()

    zaim_client.create_income(mock_session, category_id=11, amount=300000, date="2024-03-25")

    call_args = mock_session.post.call_args
    assert call_args[0][0] == "https://api.zaim.net/v2/home/money/income"
    data = call_args[1]["data"]
    assert data["category_id"] == 11
    assert data["amount"] == 300000
    print("PASS: test_create_income_params")


def test_update_payment_params():
    mock_session = MagicMock()
    mock_session.put.return_value.json.return_value = {"money": {"id": 123}}
    mock_session.put.return_value.raise_for_status = MagicMock()

    zaim_client.update_payment(mock_session, 123, category_id=101, genre_id=10102)

    call_args = mock_session.put.call_args
    assert call_args[0][0] == "https://api.zaim.net/v2/home/money/payment/123"
    data = call_args[1]["data"]
    assert data["category_id"] == 101
    assert data["mapping"] == 1
    print("PASS: test_update_payment_params")


def test_delete_money_params():
    mock_session = MagicMock()
    mock_session.delete.return_value.json.return_value = {}
    mock_session.delete.return_value.raise_for_status = MagicMock()

    zaim_client.delete_money(mock_session, 456, mode="payment")

    call_args = mock_session.delete.call_args
    assert call_args[0][0] == "https://api.zaim.net/v2/home/money/payment/456"
    print("PASS: test_delete_money_params")


def test_get_all_money_pagination():
    mock_session = MagicMock()

    page1 = {"money": [{"id": i, "mode": "payment", "amount": 100, "date": "2024-03-01", "category_name": "食費", "genre_name": "外食"} for i in range(100)]}
    page2 = {"money": [{"id": i + 100, "mode": "payment", "amount": 100, "date": "2024-03-01", "category_name": "食費", "genre_name": "外食"} for i in range(50)]}
    page3 = {"money": []}

    mock_session.get.return_value.raise_for_status = MagicMock()
    mock_session.get.return_value.json.side_effect = [page1, page2, page3]

    result = zaim_client.get_all_money(mock_session, "2024-03-01", "2024-03-31")
    assert len(result) == 150
    assert mock_session.get.call_count == 3
    print("PASS: test_get_all_money_pagination")


# --- CLI help ---


def test_cli_help(capsys=None):
    """Verify CLI help doesn't crash."""
    with patch("sys.argv", ["zaim_client.py", "--help"]):
        try:
            zaim_client.main()
        except SystemExit:
            pass
    print("PASS: test_cli_help")


# --- Run all ---

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__}: {e}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    if failed:
        sys.exit(1)
