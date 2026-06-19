import sqlite3
from datetime import datetime

DB_NAME = "finance_tracker.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            month TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            total_budget REAL NOT NULL,
            UNIQUE(user_id, month)
        )
    ''')

    conn.commit()
    conn.close()

def create_user(username, password_hash):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
        ''', (username, password_hash, datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_transaction(user_id, type, amount, category, description, date):
    conn = get_connection()
    cursor = conn.cursor()
    month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
    cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, category, description, date, month)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, type, amount, category, description, date, month))
    conn.commit()
    conn.close()

def get_transactions(user_id, month=None):
    conn = get_connection()
    cursor = conn.cursor()
    if month:
        cursor.execute('SELECT * FROM transactions WHERE user_id = ? AND month = ? ORDER BY date DESC', (user_id, month))
    else:
        cursor.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_transaction(user_id, id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (id, user_id))
    conn.commit()
    conn.close()

def set_budget(user_id, month, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO budget (user_id, month, total_budget)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, month) DO UPDATE SET total_budget = ?
    ''', (user_id, month, amount, amount))
    conn.commit()
    conn.close()

def get_budget(user_id, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT total_budget FROM budget WHERE user_id = ? AND month = ?', (user_id, month))
    row = cursor.fetchone()
    conn.close()
    return row['total_budget'] if row else 0

def get_summary(user_id, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT type, SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND month = ?
        GROUP BY type
    ''', (user_id, month))
    rows = cursor.fetchall()
    conn.close()
    summary = {"income": 0, "expense": 0}
    for row in rows:
        summary[row['type']] = row['total']
    return summary

def get_category_breakdown(user_id, month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE user_id = ? AND month = ? AND type = 'expense'
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id, month))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def import_from_csv(user_id, filepath):
    import pandas as pd
    df = pd.read_csv(filepath)
    required = {'type', 'amount', 'category', 'description', 'date'}
    if not required.issubset(df.columns):
        return False, "CSV must have columns: type, amount, category, description, date"
    for _, row in df.iterrows():
        add_transaction(user_id, row['type'], float(row['amount']),
                        row['category'], row['description'], str(row['date']))
    return True, f"{len(df)} transactions imported successfully"
