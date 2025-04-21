import sqlite3
import time
from utils import normalize_plate

DB_NAME = "plates.db"

def init_db():
    try:
        # Set a timeout for database connections and configure busy timeout
        conn = sqlite3.connect(DB_NAME, timeout=10)  # Timeout is in seconds
        conn.execute("PRAGMA busy_timeout = 3000")  # Retry for 3 seconds if the DB is locked
        c = conn.cursor()
        
        # Plates table
        c.execute('''
            CREATE TABLE IF NOT EXISTS plates (
                id INTEGER PRIMARY KEY,
                plate TEXT UNIQUE
            )
        ''')

        # Users table (now includes role)
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        # Add role column if it doesn't exist
        try:
            c.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # OTP settings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS otp_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT
            )
        ''')

        # Audit log
        c.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


def get_all_plates():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('SELECT plate FROM plates')
        plates = [row[0] for row in c.fetchall()]
        conn.close()
        return plates
    except sqlite3.Error as e:
        print(f"Error fetching plates from the database: {e}")
        return []

def add_plate(plate: str):
    try:
        normalized_plate = normalize_plate(plate)

        conn = sqlite3.connect(DB_NAME, timeout=10)
        cursor = conn.cursor()

        # Check if the plate already exists
        cursor.execute("SELECT id FROM plates WHERE plate = ?", (normalized_plate,))
        if cursor.fetchone():
            raise ValueError(f"Plate '{normalized_plate}' already exists.")

        # Insert the new plate
        cursor.execute("INSERT INTO plates (plate) VALUES (?)", (normalized_plate,))
        conn.commit()
        print(f"Plate '{normalized_plate}' added successfully")
        conn.close()

    except sqlite3.IntegrityError as e:
        print(f"Integrity error: {e}")
        raise ValueError(f"Plate '{plate}' already exists.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        raise

def delete_plate(plate):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('DELETE FROM plates WHERE plate = ?', (plate,))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error deleting plate from the database: {e}")

def log_action(username, action, details=None):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO audit_logs (username, action, details) VALUES (?, ?, ?)",
            (username, action, details)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[AUDIT LOG ERROR] {e}")