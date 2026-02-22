#!/usr/bin/env python
"""
Database setup script - Creates the health_assistant database and loads schema
"""

import mysql.connector
from pathlib import Path

# Database credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Subrat@1234',
}

def create_database():
    """Create the health_assistant database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to MySQL")
        
        # Create database
        cursor.execute('CREATE DATABASE IF NOT EXISTS health_assistant')
        print("✓ Database 'health_assistant' created")
        
        # Show databases
        cursor.execute('SHOW DATABASES')
        print("\n📊 Available databases:")
        for db in cursor:
            print(f"  - {db[0]}")
        
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
        return False

def load_schema():
    """Load the database schema"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG, database='health_assistant')
        cursor = conn.cursor()
        
        schema_path = Path('database/schema.sql')
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute each SQL statement
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                conn.commit()
        
        print("✓ Database schema loaded successfully")
        
        # Show tables
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        print(f"\n📋 Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"❌ Error loading schema: {e}")
        return False

if __name__ == '__main__':
    print("🔧 Setting up database...\n")
    
    if create_database():
        print()
        if load_schema():
            print("\n✅ Database setup complete!")
        else:
            print("\n⚠️ Database created but schema loading failed")
    else:
        print("\n❌ Database setup failed")
