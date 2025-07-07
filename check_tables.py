#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('pulse_analytics.db')
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

print("Tables in database:")
for table in tables:
    print(f"  - {table}")

# Check if users table exists and show its schema
if 'users' in tables:
    print("\nUsers table schema:")
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check if there are any users
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    print(f"\nTotal users in database: {count}")
else:
    print("\nUsers table does not exist!")

conn.close()
