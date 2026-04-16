import sqlite3

DB_NAME = "agri.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        city TEXT,
        crop TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_farmer(name, phone, city, crop):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO farmers (name, phone, city, crop) VALUES (?,?,?,?)",
                   (name, phone, city, crop))

    conn.commit()
    conn.close()


def get_farmers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name, phone, city, crop FROM farmers")
    data = cursor.fetchall()

    conn.close()
    return data
