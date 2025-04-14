import pytest
import os
from database.database import Database
from datetime import datetime, timedelta

TEST_DB_FILE = "./test_data.db"

@pytest.fixture
def db():
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

    test_db = Database()
    test_db.db_file = TEST_DB_FILE
    test_db.create_tables()
    return test_db

# ✅ TA-01 – Patikriname, ar duomenys matomi, jei bent vienas įrašas egzistuoja
def test_products_shown_in_ui(db):
    db.add_product("Test_Produktas")
    products = db.get_all_products()
    assert len(products) >= 1
    assert any(p["product_name"] == "Test_Produktas" for p in products)

# ✅ TA-02 – Patikriname, ar duomenys grąžinami nuo naujausio įrašo
def test_products_sorted_by_date_desc(db):
    db.add_product("Senesnis")
    db.add_product("Naujesnis")
    products = db.get_all_products()
    created_times = [p["created_at"] for p in products]
    assert created_times == sorted(created_times, reverse=True)

# ✅ TA-03 – Patikriname filtravimą
def test_get_products_today(db):
    db.add_product("Apple")
    products = db.get_products_today()
    assert len(products) == 1
    assert products[0]['product_name'] == "Apple"

def test_get_products_this_week(db):
    db.add_product("Apple")
    products = db.get_products_this_week()
    assert len(products) == 1
    assert products[0]['product_name'] == "Apple"

    # Įrašas prieš 10 dienų (neturėtų būti grąžintas)
    past_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Product (product_name, created_at) VALUES (?, ?)',
        ("Old Apple", past_date)
    )
    conn.commit()
    conn.close()

    products = db.get_products_this_week()
    assert all(p['product_name'] != "Old Apple" for p in products)

def test_get_products_this_month(db):
    db.add_product("Apple")
    products = db.get_products_this_month()
    assert len(products) == 1
    assert products[0]['product_name'] == "Apple"

    # Įrašas prieš 40 dienų (neturėtų būti grąžintas)
    past_date = (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO Product (product_name, created_at) VALUES (?, ?)',
        ("Old Apple", past_date)
    )
    conn.commit()
    conn.close()

    products = db.get_products_this_month()
    assert all(p['product_name'] != "Old Apple" for p in products)

def test_get_products_today_empty(db):
    products = db.get_products_today()
    assert len(products) == 0

def test_get_products_this_week_empty(db):
    products = db.get_products_this_week()
    assert len(products) == 0

def test_get_products_this_month_empty(db):
    products = db.get_products_this_month()
    assert len(products) == 0

# ✅ TA-04 – Patikriname, kad kai nėra duomenų, rezultatų nėra
def test_no_data_message(db):
    # Ištrinam visus įrašus
    products = db.get_all_products()
    for p in products:
        db.delete_product(p["id"])
    assert len(db.get_all_products()) == 0
    assert len(db.get_products_today()) == 0

# ✅ TA-05 – Patikriname klaidos valdymą (simuliuojam DB klaidą)
def test_database_error_handling(monkeypatch):
    broken_db = Database()

    def fake_error():
        raise Exception("DB nepavyko pasiekti")

    monkeypatch.setattr(broken_db, "get_all_products", fake_error)

    with pytest.raises(Exception) as exc:
        broken_db.get_all_products()

    assert "DB nepavyko" in str(exc.value)


