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
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            month TEXT NOT NULL UNIQUE,
            total_budget REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(type, amount, category, description, date):
    conn = get_connection()
    cursor = conn.cursor()
    month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
    cursor.execute('''
        INSERT INTO transactions (type, amount, category, description, date, month)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (type, amount, category, description, date, month))
    conn.commit()
    conn.close()

def get_transactions(month=None):
    conn = get_connection()
    cursor = conn.cursor()
    if month:
        cursor.execute('SELECT * FROM transactions WHERE month = ? ORDER BY date DESC', (month,))
    else:
        cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_transaction(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def set_budget(month, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO budget (month, total_budget)
        VALUES (?, ?)
        ON CONFLICT(month) DO UPDATE SET total_budget = ?
    ''', (month, amount, amount))
    conn.commit()
    conn.close()

def get_budget(month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT total_budget FROM budget WHERE month = ?', (month,))
    row = cursor.fetchone()
    conn.close()
    return row['total_budget'] if row else 0

def get_summary(month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT type, SUM(amount) as total
        FROM transactions
        WHERE month = ?
        GROUP BY type
    ''', (month,))
    rows = cursor.fetchall()
    conn.close()
    summary = {"income": 0, "expense": 0}
    for row in rows:
        summary[row['type']] = row['total']
    return summary

def get_category_breakdown(month):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE month = ? AND type = 'expense'
        GROUP BY category
        ORDER BY total DESC
    ''', (month,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def import_from_csv(filepath):
    import pandas as pd
    df = pd.read_csv(filepath)
    required = {'type', 'amount', 'category', 'description', 'date'}
    if not required.issubset(df.columns):
        return False, "CSV must have columns: type, amount, category, description, date"
    for _, row in df.iterrows():
        add_transaction(row['type'], float(row['amount']),
                        row['category'], row['description'], str(row['date']))
    return True, f"{len(df)} transactions imported successfully"
