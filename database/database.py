import sqlite3

DB_FILE = "data.db"

# Funkcija prisijungimui prie duomenų bazės
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Funkcija lentelių sukūrimui
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Lentelė įrašų saugojimui
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Recording (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT NOT NULL,
        duration REAL NOT NULL,
        size INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Lentelė transkripcijų saugojimui
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

    # Lentelė produktų saugojimui
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transcription_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(transcription_id) REFERENCES Transcription(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()

def add_recording(file_path, duration, size):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Recording (file_path, duration, size) VALUES (?, ?, ?)',
                   (file_path, duration, size))
    conn.commit()
    conn.close()

def add_transcription(recording_id, text, confidence, language):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Transcription (recording_id, text, confidence, language_detected) VALUES (?, ?, ?, ?)',
                   (recording_id, text, confidence, language))
    conn.commit()
    conn.close()


def add_product(transcription_id, product_name, category, confidence):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Product (transcription_id, product_name, category, confidence) VALUES (?, ?, ?, ?)',
                   (transcription_id, product_name, category, confidence))
    conn.commit()
    conn.close()

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Product')
    products = cursor.fetchall()
    conn.close()
    return [dict(p) for p in products]

def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Product WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

def get_products_today():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Product WHERE DATE(created_at) = DATE('now')")
    products = cursor.fetchall()
    conn.close()
    return [dict(p) for p in products]

create_tables()
