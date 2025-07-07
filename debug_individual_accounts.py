#!/usr/bin/env python3

"""
Debug script to test blockchain activity collection for specific users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.hive_api import HiveAPIClient
from analytics.collector import AnalyticsCollector  
from database.manager import DatabaseManager

def test_blockchain_activity():
    """Test blockchain activity collection for specific users"""
    
    config = {
        'HIVE_ACCOUNT_NAME': 'hiveecuador',
        'IMAGE_UPLOAD_SERVICE': 'https://images.hive.blog'
    }
    
    api_client = HiveAPIClient(config)
    db_manager = DatabaseManager('pulse_analytics.db')
    
    # Test a few known active users
    test_users = ['aliento', 'angelica7', 'andymusic', 'almagrande']
    
    print("🔍 Testing blockchain activity collection for specific users...")
    
    for username in test_users:
        print(f"\n👤 Testing user: {username}")
        
        try:
            # Test getting blockchain activity for the last 7 days
            activities = api_client.get_user_blockchain_activity(username, days=7)
            
            print(f"  📊 Found {len(activities)} blockchain operations")
            
            if activities:
                # Count different operation types
                op_types = {}
                for activity in activities:
                    op_type = activity.get('type', 'unknown')
                    op_types[op_type] = op_types.get(op_type, 0) + 1
                
                print(f"  � Operation types:")
                for op_type, count in sorted(op_types.items()):
                    print(f"    • {op_type}: {count}")
                
                # Show some sample operations
                print(f"  📄 Sample operations (first 3):")
                for i, activity in enumerate(activities[:3]):
                    timestamp = activity.get('timestamp', 'N/A')
                    op_type = activity.get('type', 'unknown')
                    print(f"    {i+1}. {timestamp} - {op_type}")
            else:
                print(f"  ❌ No blockchain activities found for {username}")
                
        except Exception as e:
            print(f"  💥 Error getting activity for {username}: {e}")
    
    print(f"\n🏁 Blockchain activity test completed")

if __name__ == "__main__":
    test_blockchain_activity()
