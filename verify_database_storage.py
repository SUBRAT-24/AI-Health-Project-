#!/usr/bin/env python
"""
Verify database stores: User login, Appointments, Admin login (id/password).
Uses the same Flask app and DB as run_backend.py.
Run from project root: python verify_database_storage.py
"""
import os
import sys

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

def main():
    from flask_app import create_flask_app, db
    from flask_app.models import User, Appointment

    app = create_flask_app()
    with app.app_context():
        db.create_all()

        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        db_path = db_uri.replace('sqlite:///', '').lstrip('/')
        if not db_path or not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path or 'health_assistant.db')

        print('\n' + '='*70)
        print('DATABASE STORAGE VERIFICATION')
        print('='*70)
        print(f'\nDatabase: {db_path}')
        print(f'Exists: {os.path.exists(db_path)}')
        if os.path.exists(db_path):
            print(f'Size: {os.path.getsize(db_path)} bytes')

        # 1. Users table (login storage)
        print('\n--- 1. USER LOGIN STORAGE (users table) ---')
        users = User.query.all()
        print(f'Total users: {len(users)}')
        for u in users:
            role = getattr(u, 'role', None) or 'user'
            has_pass = bool(getattr(u, 'password_hash', None))
            print(f'  ID={u.id}  email={u.email}  name={u.name}  role={role}  password_stored={has_pass}')

        # 2. Admin login (same table, role=admin)
        print('\n--- 2. ADMIN LOGIN (same users table, role=admin) ---')
        try:
            admins = User.query.filter_by(role='admin').all()
        except Exception:
            admins = [u for u in users if getattr(u, 'role', None) == 'admin']
        if admins:
            for a in admins:
                print(f'  Admin ID={a.id}  email={a.email}  password_hash_stored={bool(a.password_hash)}')
            print('  -> Admin uses same login endpoint; password stored hashed (bcrypt).')
        else:
            print('  No admin user yet. Run: python create_admin.py')

        # 3. Appointments table
        print('\n--- 3. APPOINTMENTS STORAGE (appointments table) ---')
        appointments = Appointment.query.order_by(Appointment.id.desc()).limit(10).all()
        print(f'Total appointments in DB: {Appointment.query.count()}')
        for apt in appointments:
            print(f'  ID={apt.id}  user_id={apt.user_id}  doctor={apt.doctor_name}  date={apt.appointment_date}  status={apt.status}')

        print('\n' + '='*70)
        print('SUMMARY')
        print('='*70)
        print('  Login:     Stored in "users" (email, password_hash, name, phone, etc.)')
        print('  Admin:     Same "users" table with role="admin"; password hashed.')
        print('  Appointments: Stored in "appointments" (user_id, doctor_name, date, status).')
        print('='*70 + '\n')

if __name__ == '__main__':
    main()
