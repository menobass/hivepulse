#!/usr/bin/env python3

"""
Test blockchain activity collection for a specific user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.hive_api import HiveAPIClient
from analytics.collector import AnalyticsCollector
from database.manager import DatabaseManager

def test_activity_collection():
    """Test activity collection for a specific user"""
    
    config = {
        'HIVE_ACCOUNT_NAME': 'hiveecuador',
        'IMAGE_UPLOAD_SERVICE': 'https://images.hive.blog'
    }
    
    api_client = HiveAPIClient(config)
    db_manager = DatabaseManager('pulse_analytics.db')
    collector = AnalyticsCollector(api_client, db_manager)
    
    # Test with a known active user
    test_username = 'angelica7'
    
    print(f"🔍 Testing activity collection for: {test_username}")
    
    # Test the fixed method
    try:
        user_activity = collector.get_user_blockchain_activity(test_username, '2025-07-07')
        print(f"✅ Successfully collected activity:")
        print(f"  Posts: {user_activity.posts_count}")
        print(f"  Comments: {user_activity.comments_count}")
        print(f"  Upvotes given: {user_activity.upvotes_given}")
        print(f"  Upvotes received: {user_activity.upvotes_received}")
        print(f"  Engagement score: {user_activity.engagement_score}")
        
        # Test storing in database
        activities = [user_activity]
        try:
            db_manager.store_user_activities(activities, '2025-07-07')
            print(f"✅ Successfully stored activity in database")
        except Exception as store_error:
            print(f"❌ Error storing in database: {str(store_error)}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_activity_collection()
