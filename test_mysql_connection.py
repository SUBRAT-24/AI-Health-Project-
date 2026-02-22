#!/usr/bin/env python
"""
MySQL connection test with multiple connection methods
"""

import mysql.connector
import sys

print("Attempting to connect to MySQL...\n")

# Try different connection methods
connection_methods = [
    {
        'name': 'TCP localhost',
        'config': {'host': 'localhost', 'user': 'root', 'password': 'Subrat@1234', 'port': 3306}
    },
    {
        'name': 'TCP 127.0.0.1',
        'config': {'host': '127.0.0.1', 'user': 'root', 'password': 'Subrat@1234', 'port': 3306}
    },
    {
        'name': 'Unix Socket',
        'config': {'unix_socket': '/var/run/mysqld/mysqld.sock', 'user': 'root', 'password': 'Subrat@1234'}
    },
    {
        'name': 'Named Pipe',
        'config': {'host': '.', 'user': 'root', 'password': 'Subrat@1234'}
    },
]

for method in connection_methods:
    try:
        print(f"Trying: {method['name']}...", end=' ')
        conn = mysql.connector.connect(**method['config'])
        cursor = conn.cursor()
        cursor.execute('SELECT VERSION()')
        version = cursor.fetchone()
        print(f"✓ Success!\n  MySQL Version: {version[0]}")
        cursor.close()
        conn.close()
        sys.exit(0)
    except Exception as e:
        print(f"✗ Failed\n  Error: {str(e)[:80]}")

print("\n❌ Could not connect using any method.")
print("\nTroubleshooting steps:")
print("1. Ensure MySQL service is running: Get-Service MySQL80")
print("2. Check MySQL listens on TCP: netstat -ano | findstr 3306")
print("3. Verify MySQL password is correct")
print("4. Check MySQL configuration file for bind-address")
