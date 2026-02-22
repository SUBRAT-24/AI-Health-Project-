#!/usr/bin/env python
"""
Create an admin user. Run from project root:
  python create_admin.py
  python create_admin.py --email admin@example.com --password mypassword
"""
import os
import sys
import argparse

# Run from project root; backend must be on path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from flask_app import create_flask_app, db
from flask_app.models import User
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser(description='Create an admin user')
    parser.add_argument('--email', default='admin@healthassistant.com', help='Admin email')
    parser.add_argument('--password', default='admin123', help='Admin password')
    parser.add_argument('--name', default='Admin', help='Admin display name')
    args = parser.parse_args()

    app = create_flask_app()
    with app.app_context():
        db.create_all()
        # Add role/is_active columns if missing (SQLite: ALTER TABLE)
        try:
            from sqlalchemy import text, inspect
            insp = inspect(db.engine)
            if 'users' in insp.get_table_names():
                cols = [c['name'] for c in insp.get_columns('users')]
                with db.engine.connect() as conn:
                    if 'role' not in cols:
                        conn.execute(text('ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT \'user\''))
                        conn.commit()
                        print('Added column: role')
                    if 'is_active' not in cols:
                        conn.execute(text('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1'))
                        conn.commit()
                        print('Added column: is_active')
        except Exception as e:
            print('Note: migration skip (may already be applied):', e)
        existing = User.query.filter_by(email=args.email).first()
        if existing:
            if getattr(existing, 'role', None) == 'admin':
                print(f'Admin already exists: {args.email}')
                return
            existing.role = 'admin'
            existing.is_active = True
            db.session.commit()
            print(f'Updated user to admin: {args.email}')
            return
        user = User(
            email=args.email,
            name=args.name,
            phone='0000000000',
            date_of_birth=datetime.now(timezone.utc).date(),
            gender='other',
            role='admin',
            is_active=True
        )
        user.set_password(args.password)
        db.session.add(user)
        db.session.commit()
        print(f'Admin created: {args.email}')
        print('Login at: frontend/pages/admin-login.html')


if __name__ == '__main__':
    main()
