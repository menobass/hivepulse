#!/usr/bin/env python3
"""
Debug script to check why user activities are zero
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import HiveEcuadorPulse


def debug_user_activities():
    """Debug why user activities are returning zero"""
    print("🔍 Debugging User Activities Collection")
    print("=" * 50)
    
    try:
        # Initialize the bot
        bot = HiveEcuadorPulse()
        
        # Check tracked users
        print("\n1. Checking tracked users...")
        tracked_users = bot.db_manager.get_tracked_users()
        print(f"   📊 Total tracked users: {len(tracked_users)}")
        print(f"   👥 Sample users: {tracked_users[:5] if tracked_users else 'None'}")
        
        # Check join dates for a few users
        print("\n2. Checking join dates...")
        today = datetime.now().strftime('%Y-%m-%d')
        
        for i, username in enumerate(tracked_users[:3]):
            join_date = bot.analytics_collector.member_manager.get_member_join_date(username)
            print(f"   User {i+1}: {username}")
            print(f"     Join date: {join_date}")
            
            if join_date:
                join_datetime = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
                date_datetime = datetime.strptime(today, '%Y-%m-%d')
                should_collect = date_datetime >= join_datetime.replace(tzinfo=None)
                print(f"     Should collect for {today}: {should_collect}")
                
                # Test individual activity collection
                print(f"     Testing activity collection...")
                activity = bot.analytics_collector.get_user_blockchain_activity(username, today)
                print(f"     Activity result: Posts={activity.posts_count}, Comments={activity.comments_count}, Votes={activity.upvotes_given}")
        
        # Check what's in the database for existing activities
        print("\n3. Checking database for existing activities...")
        with bot.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT username, posts_count, comments_count, upvotes_given, upvotes_received
                FROM daily_activity 
                WHERE date = ? 
                ORDER BY engagement_score DESC 
                LIMIT 5
            """, (today,))
            
            activities = cursor.fetchall()
            print(f"   📊 Activities in DB for {today}: {len(activities)}")
            
            for activity in activities:
                print(f"     {activity['username']}: Posts={activity['posts_count']}, Comments={activity['comments_count']}, Votes={activity['upvotes_given']}")
        
        # Test the actual function that's failing
        print("\n4. Testing get_user_activities_blockchain_wide...")
        user_activities = bot.analytics_collector.get_user_activities_blockchain_wide(today)
        print(f"   📊 Returned activities: {len(user_activities)}")
        
        for activity in user_activities[:3]:
            print(f"     {activity.username}: Posts={activity.posts_count}, Comments={activity.comments_count}, Votes={activity.upvotes_given}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_user_activities()
