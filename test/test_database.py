import os
import unittest
import sqlite3
from datetime import datetime, timedelta

from database.database import Database

TEST_DB = "test_data.db"

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Naudojame testavimo duomenų bazę
        self.db = Database()
        self.db.db_file = TEST_DB
        self.db.create_tables()

    def tearDown(self):
        # Išvalome po kiekvieno testo
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_create_tables(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Product'")
        table = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(table)

    def test_add_product(self):
        self.db.add_product("Apple", "Fruit")
        products = self.db.get_all_products()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_name'], 'Apple')
        self.assertEqual(products[0]['category'], 'Fruit')

    def test_get_all_products_empty(self):
        products = self.db.get_all_products()
        self.assertEqual(len(products), 0)

    def test_add_multiple_products(self):
        self.db.add_product("Apple", "Fruit")
        self.db.add_product("Banana", "Fruit")
        products = self.db.get_all_products()
        self.assertEqual(len(products), 2)
        self.assertEqual(products[1]['product_name'], 'Banana')

    def test_database_integrity(self):
        self.db.add_product("Orange", "Fruit")
        products = self.db.get_all_products()
        self.assertEqual(products[0]['product_name'], 'Orange')
        self.assertEqual(products[0]['category'], 'Fruit')

        #  Testas: Patikriname produkto ištrynimą

    def test_delete_product(self):
        self.db.add_product("Apple", "Fruit")
        products = self.db.get_all_products()
        self.assertEqual(len(products), 1)

        product_id = products[0]['id']
        self.db.delete_product(product_id)

        products = self.db.get_all_products()
        self.assertEqual(len(products), 0)  # Produktas turi būti ištrintas

        #  Testas: Patikriname filtrą pagal dieną

    def test_get_products_today(self):
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.add_product("Apple", "Fruit")

        products = self.db.get_products_today()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_name'], "Apple")

        #  Testas: Patikriname filtrą pagal savaitę

    def test_get_products_this_week(self):
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.add_product("Apple", "Fruit")

        products = self.db.get_products_this_week()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_name'], "Apple")

        #  Pridėkime produktą iš kitos savaitės (testavimui)
        past_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Product (product_name, category, created_at) VALUES (?, ?, ?)',
            ("Old Apple", "Fruit", past_date)
        )
        conn.commit()
        conn.close()

        products = self.db.get_products_this_week()
        self.assertEqual(len(products), 1)  # Senas produktas neturėtų būti rodomas

        #  Testas: Patikriname filtrą pagal mėnesį

    def test_get_products_this_month(self):
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.db.add_product("Apple", "Fruit")

        products = self.db.get_products_this_month()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]['product_name'], "Apple")

        #  Pridėkime produktą iš kito mėnesio (testavimui)
        past_date = (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d %H:%M:%S')
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Product (product_name, category, created_at) VALUES (?, ?, ?)',
            ("Old Apple", "Fruit", past_date)
        )
        conn.commit()
        conn.close()

        products = self.db.get_products_this_month()
        self.assertEqual(len(products), 1)  # Senas produktas neturėtų būti rodomas

        # Testas: Patikriname, ar duomenų nėra pagal dieną

    def test_get_products_today_empty(self):
        products = self.db.get_products_today()
        self.assertEqual(len(products), 0)

        #  Testas: Patikriname, ar duomenų nėra pagal savaitę

    def test_get_products_this_week_empty(self):
        products = self.db.get_products_this_week()
        self.assertEqual(len(products), 0)

        #  Testas: Patikriname, ar duomenų nėra pagal mėnesį

    def test_get_products_this_month_empty(self):
        products = self.db.get_products_this_month()
        self.assertEqual(len(products), 0)

if __name__ == '__main__':
    unittest.main()
