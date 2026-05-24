# init_db.py
import sqlite3

conn = sqlite3.connect("db.sqlite")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        phone TEXT,
        doctor TEXT,
        day TEXT NOT NULL,
        time TEXT NOT NULL,
        conf_number INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
conn.close()

print("SQLite DB 'db.sqlite' created with 'appointments' table.")