import csv
import io

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture(autouse=True)
def clear_expenses():
    main.expenses.clear()


@pytest.fixture
def client():
    return TestClient(main.app)


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Split shared expenses" in response.text
    assert "Settle up with confidence." in response.text
    assert 'id="settlements"' in response.text


def test_home_page_uses_mobile_expense_layout(client):
    response = client.get("/")
    assert 'class="balance-card"' in response.text
    assert 'class="expense-card"' in response.text
    assert "@media (max-width: 480px)" in response.text


def test_split_expense_between_roommates(client):
    response = client.post("/expenses", data={"description": "Dinner", "amount": "300", "paid_by": "Ana", "shares": "Ana, Ben, Cara"})
    assert response.status_code == 200
    assert response.json()["settlements"] == [{"from": "Ben", "to": "Ana", "amount": "PHP 100.00"}, {"from": "Cara", "to": "Ana", "amount": "PHP 100.00"}]


def test_rejects_non_positive_expenses(client):
    response = client.post("/expenses", data={"description": "Coffee", "amount": "0", "paid_by": "Ana", "shares": "Ben"})
    assert response.status_code == 422


def test_rejects_non_finite_expenses(client):
    response = client.post("/expenses", data={"description": "Coffee", "amount": "NaN", "paid_by": "Ana", "shares": "Ben"})
    assert response.status_code == 422


def test_settlement_rendering_uses_text_content(client):
    response = client.get("/")
    assert 'document.createElement("li")' in response.text
    assert "copy.textContent =" in response.text
    assert "amount.textContent =" in response.text


def test_export_expenses_returns_csv_attachment(client):
    client.post("/expenses", data={"description": 'Dinner, "late"', "amount": "300", "paid_by": "Ana", "shares": "Ana, Ben"})
    response = client.post("/expenses/export")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == 'attachment; filename="expenses.csv"'
    assert list(csv.reader(io.StringIO(response.text))) == [["description", "amount", "paid_by", "shares"], ['Dinner, "late"', "300.00", "Ana", "Ana, Ben"]]


def test_export_expenses_when_empty_returns_header_only(client):
    response = client.post("/expenses/export")
    assert list(csv.reader(io.StringIO(response.text))) == [["description", "amount", "paid_by", "shares"]]


def test_export_expenses_does_not_mutate_expenses(client):
    client.post("/expenses", data={"description": "Dinner", "amount": "300", "paid_by": "Ana", "shares": "Ana, Ben"})
    original_expenses = list(main.expenses)
    client.post("/expenses/export")
    client.post("/expenses/export")
    assert main.expenses == original_expenses
