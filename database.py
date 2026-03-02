import sqlite3
import datetime
import os

DB_NAME = "metro_history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            command TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_command(source, command):
    if not command:
        return
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO history (timestamp, source, command) VALUES (?, ?, ?)", (timestamp, source, command))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging command: {e}")

def get_history(limit=20):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, source, command FROM history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

if __name__ == "__main__":
    init_db()
