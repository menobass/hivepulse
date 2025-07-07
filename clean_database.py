#!/usr/bin/env python3

"""
Clean up database by removing invalid usernames and re-syncing from API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.manager import DatabaseManager
from utils.hive_api import HiveAPIClient
import sqlite3

def clean_invalid_users():
    """Remove users with invalid usernames from the database"""
    
    # Initialize components
    config = {
        'HIVE_ACCOUNT_NAME': 'hiveecuador',
        'IMAGE_UPLOAD_SERVICE': 'https://images.hive.blog'
    }
    
    api_client = HiveAPIClient(config)
    db_manager = DatabaseManager('pulse_analytics.db')
    
    print("🧹 Cleaning invalid usernames from database...")
    
    # Get all users from database
    connection = sqlite3.connect('pulse_analytics.db')
    cursor = connection.cursor()
    
    cursor.execute("SELECT username FROM users WHERE is_active = 1")
    all_users = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(all_users)} active users in database")
    
    invalid_users = []
    valid_users = []
    
    for username in all_users:
        if not api_client._is_valid_hive_username(username):
            print(f"❌ Invalid username format: {username}")
            invalid_users.append(username)
        else:
            valid_users.append(username)
    
    print(f"\nFound {len(invalid_users)} invalid usernames:")
    for user in invalid_users:
        print(f"  - {user}")
    
    print(f"Found {len(valid_users)} valid usernames")
    
    # Remove invalid users
    if invalid_users:
        print(f"\n🗑️ Removing {len(invalid_users)} invalid users...")
        for username in invalid_users:
            cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
            print(f"  Deactivated: {username}")
        
        connection.commit()
        print("✅ Invalid users removed")
    
    connection.close()
    
    print(f"\n📊 Database now has {len(valid_users)} valid active users")

if __name__ == "__main__":
    clean_invalid_users()
