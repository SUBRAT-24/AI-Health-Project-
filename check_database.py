#!/usr/bin/env python
"""
Database connection and storage check.
Verifies: users (login), appointments, admin (role + password) storage.
"""
import os
import sys

# Use same DB as Flask app when run from project root
DB_NAME = 'health_assistant.db'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, DB_NAME)

def main():
    import sqlite3

    print('\n' + '='*70)
    print('DATABASE CHECK – Login, Appointments, Admin storage')
    print('='*70 + '\n')

    if not os.path.exists(DB_PATH):
        print(f'[INFO] Database not yet created: {DB_PATH}')
        print('       Run the app once (python run_backend.py) or: python create_admin.py')
        print('='*70 + '\n')
        return

    print(f'Database: {DB_PATH}')
    print(f'Size: {os.path.getsize(DB_PATH)} bytes\n')

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print('--- Tables ---')
    for t in tables:
        cur.execute(f'SELECT COUNT(*) FROM [{t}]')
        print(f'  {t}: {cur.fetchone()[0]} rows')
    print()

    # Users (login storage)
    print('--- 1. USER LOGIN (users table) ---')
    if 'users' in tables:
        cur.execute("PRAGMA table_info(users)")
        cols = [r[1] for r in cur.fetchall()]
        has_role = 'role' in cols
        has_password = 'password_hash' in cols
        print(f'  Columns include: email, name, password_hash={has_password}, role={has_role}')
        cur.execute('SELECT id, email, name FROM users LIMIT 5')
        for row in cur.fetchall():
            print(f'  ID={row["id"]}  email={row["email"]}  name={row["name"]}')
        if has_role:
            cur.execute("SELECT id, email FROM users WHERE role='admin'")
            admins = cur.fetchall()
            print(f'  Admin accounts: {len(admins)}')
            for a in admins:
                print(f'    Admin ID={a["id"]}  email={a["email"]}')
    else:
        print('  users table missing')
    print()

    # Appointments
    print('--- 2. APPOINTMENTS (appointments table) ---')
    if 'appointments' in tables:
        cur.execute('SELECT id, user_id, doctor_name, appointment_date, status FROM appointments ORDER BY id DESC LIMIT 5')
        rows = cur.fetchall()
        print(f'  Sample rows: {len(rows)}')
        for r in rows:
            print(f'  ID={r["id"]}  user_id={r["user_id"]}  doctor={r["doctor_name"]}  date={r["appointment_date"]}  status={r["status"]}')
    else:
        print('  appointments table missing')
    print()

    conn.close()

    print('='*70)
    print('Summary: Login and Admin use "users" (password hashed). Appointments in "appointments".')
    print('='*70 + '\n')

if __name__ == '__main__':
    main()
