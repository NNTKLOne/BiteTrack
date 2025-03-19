import sqlite3

DB_FILE = "data.db"

class Database:

    def __init__(self):
        self.db_file = DB_FILE
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Recording (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            duration REAL NOT NULL,
            file_size INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transcription (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recording_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            confidence REAL NOT NULL,
            language_detected TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(recording_id) REFERENCES Recording(id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.commit()
        conn.close()

    def add_recording(self, file_path, duration, size):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Recording (file_path, duration, file_size) VALUES (?, ?, ?)',
                       (file_path, duration, size))
        conn.commit()
        conn.close()

    def add_transcription(self, recording_id, text, confidence, language):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Transcription (recording_id, text, confidence, language_detected) VALUES (?, ?, ?, ?)',
            (recording_id, text, confidence, language))
        conn.commit()
        conn.close()


    def add_product(self, product_name, category):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Product (product_name, category) VALUES (?, ?)',
                       (product_name, category))
        conn.commit()
        conn.close()


    def get_all_products(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Product')
        products = cursor.fetchall()
        conn.close()
        return [dict(p) for p in products]


    def delete_product(self, product_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Product WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()

    def get_products_today(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Product WHERE DATE(created_at) = DATE('now')")
        products = cursor.fetchall()
        conn.close()
        return [dict(p) for p in products]
