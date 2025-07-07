#!/usr/bin/env python3
"""
Debug script to inspect the actual API response and compare with our database
"""

import requests
import json
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.manager import DatabaseManager

def debug_api_vs_database():
    """Compare API response with database to find discrepancies"""
    
    print("🔍 DEBUGGING API vs DATABASE DISCREPANCIES")
    print("=" * 60)
    
    # 1. Test API directly
    print("\n1. Testing API Response:")
    payload = {
        "jsonrpc": "2.0",
        "method": "bridge.list_subscribers",
        "params": {"community": "hive-115276", "limit": 10},
        "id": 1
    }
    
    response = requests.post('https://api.hive.blog', json=payload, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            print(f"✅ API returned {len(data['result'])} subscribers")
            print("First 10 subscribers from API:")
            for i, subscriber in enumerate(data['result'][:10]):
                if isinstance(subscriber, list):
                    username = subscriber[0]
                    role = subscriber[1] if len(subscriber) > 1 else 'unknown'
                    print(f"  {i+1}. {username} ({role})")
                else:
                    print(f"  {i+1}. {subscriber}")
        else:
            print(f"❌ API Error: {data}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
    
    # 2. Check database
    print("\n2. Checking Database:")
    try:
        db = DatabaseManager("pulse_analytics.db")
        tracked_users = db.get_tracked_users()
        print(f"✅ Database has {len(tracked_users)} tracked users")
        print("First 10 users from database:")
        for i, user in enumerate(tracked_users[:10]):
            print(f"  {i+1}. {user}")
            
        # Check for problem usernames
        problem_users = ['negan-ali', 'chiagoziee444']
        print(f"\n3. Checking for problem usernames:")
        for user in problem_users:
            if user in tracked_users:
                print(f"❌ Found problem user in DB: {user}")
            else:
                print(f"✅ Problem user NOT in DB: {user}")
                
    except Exception as e:
        print(f"❌ Database error: {e}")

def test_specific_account_activity():
    """Test blockchain activity for a known active account"""
    print("\n4. Testing Blockchain Activity for Known Active Account:")
    
    # Test with a known active account from our list
    test_username = "aliento"  # Should be active
    
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": ["account_history_api", "get_account_history", [test_username, -1, 10]],
        "id": 1
    }
    
    response = requests.post('https://api.hive.blog', json=payload, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data and data['result']:
            print(f"✅ Found {len(data['result'])} recent operations for @{test_username}")
            print("Recent activity:")
            for i, op in enumerate(data['result'][-5:]):  # Last 5 operations
                if len(op) >= 2:
                    timestamp = op[1].get('timestamp', 'unknown')
                    op_type = op[1].get('op', ['unknown'])[0]
                    print(f"  {i+1}. {timestamp}: {op_type}")
        else:
            print(f"❌ No activity found for @{test_username}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

if __name__ == "__main__":
    debug_api_vs_database()
    test_specific_account_activity()
