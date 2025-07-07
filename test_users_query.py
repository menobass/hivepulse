#!/usr/bin/env python3
import sqlite3

# Connect to database
conn = sqlite3.connect('pulse_analytics.db')
cursor = conn.cursor()

# Test the query that was failing
cursor.execute("SELECT * FROM users;")
users = cursor.fetchall()

print("All users in database:")
for user in users:
    print(f"  ID: {user[0]}, Username: {user[1]}, Active: {user[8]}, Business: {user[9]}")

print(f"\nTotal users: {len(users)}")

# Test the query used by get_tracked_users
cursor.execute("SELECT username FROM users WHERE is_active = 1;")
active_users = cursor.fetchall()

print(f"\nActive users: {len(active_users)}")
for user in active_users:
    print(f"  - @{user[0]}")

conn.close()
