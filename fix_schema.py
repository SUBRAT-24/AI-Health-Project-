#!/usr/bin/env python
"""Migrate SQLite schema to match current models."""
import os, sys
sys.path.insert(0, 'backend')

from flask_app import create_flask_app
from flask_app.models import db
from sqlalchemy import text, inspect

app = create_flask_app()
with app.app_context():
    insp = inspect(db.engine)

    print("=== CURRENT SCHEMA ===")
    for t in insp.get_table_names():
        cols = [c['name'] for c in insp.get_columns(t)]
        print(f"  {t}: {cols}")

    migrations = [
        ("appointments", "doctor_specialization", "VARCHAR(120)"),
        ("appointments", "duration_minutes", "INTEGER DEFAULT 30"),
        ("appointments", "notes", "TEXT"),
        ("appointments", "reason", "TEXT"),
        ("health_records", "blood_glucose", "FLOAT"),
        ("health_records", "oxygen_saturation", "FLOAT"),
        ("health_records", "timestamp", "DATETIME"),
    ]

    with db.engine.connect() as conn:
        for table, col, coltype in migrations:
            if table in [t for t in insp.get_table_names()]:
                existing = [c['name'] for c in insp.get_columns(table)]
                if col not in existing:
                    try:
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {coltype}"))
                        conn.commit()
                        print(f"  + Added {table}.{col}")
                    except Exception as e:
                        print(f"  ! Skip {table}.{col}: {e}")
                else:
                    print(f"  = {table}.{col} already exists")

    db.create_all()
    print("\n  db.create_all() done")

    insp2 = inspect(db.engine)
    print("\n=== FINAL SCHEMA ===")
    for t in insp2.get_table_names():
        cols = [c['name'] for c in insp2.get_columns(t)]
        print(f"  {t}: {cols}")
    print("\nDone!")
