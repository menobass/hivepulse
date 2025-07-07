#!/usr/bin/env python3
"""
Debug script to check the exact data being passed to the report generator
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import HiveEcuadorPulse


def debug_report_data():
    """Debug the data being passed to the report generator"""
    print("🔍 Debugging Report Data Generation")
    print("=" * 50)
    
    try:
        # Initialize the bot
        bot = HiveEcuadorPulse()
        
        # Collect daily data
        print("\n1. Collecting daily data...")
        daily_data = bot.analytics_collector.collect_daily_data_with_member_sync()
        
        print(f"✅ Daily data collected for {daily_data['date']}")
        print(f"📊 Data structure keys: {list(daily_data.keys())}")
        
        # Show community stats
        print("\n2. Community Stats:")
        community_stats = daily_data.get('community_stats', {})
        print(f"   Community stats keys: {list(community_stats.keys())}")
        
        for key, value in community_stats.items():
            if key != 'historical_data':  # Skip historical data for now
                print(f"   {key}: {value}")
        
        # Show user activities
        print(f"\n3. User Activities:")
        user_activities = daily_data.get('user_activities', [])
        print(f"   Total user activities: {len(user_activities)}")
        
        if user_activities:
            print("   Sample activities:")
            for i, activity in enumerate(user_activities[:3]):
                print(f"   User {i+1}: {activity.username}")
                print(f"     Posts: {activity.posts_count}")
                print(f"     Comments: {activity.comments_count}")
                print(f"     Upvotes given: {activity.upvotes_given}")
                print(f"     Engagement score: {activity.engagement_score}")
        
        # Show top performers
        print(f"\n4. Top Performers:")
        top_performers = daily_data.get('top_performers', {})
        print(f"   Top performers keys: {list(top_performers.keys())}")
        
        # Test report generation with this data
        print("\n5. Testing report generation...")
        
        # Generate charts
        chart_files = bot.generate_charts(daily_data)
        print(f"   ✅ Generated {len(chart_files)} charts")
        
        # Generate report
        report_content = bot.report_generator.generate_full_report(daily_data, chart_files)
        print(f"   ✅ Generated report ({len(report_content)} characters)")
        
        # Save debug data to file
        debug_data = {
            'date': daily_data['date'],
            'community_stats': community_stats,
            'user_activities_count': len(user_activities),
            'top_performers': top_performers,
            'chart_files_count': len(chart_files)
        }
        
        with open('debug_report_data.json', 'w') as f:
            json.dump(debug_data, f, indent=2, default=str)
        
        print(f"\n✅ Debug data saved to debug_report_data.json")
        
        # Show key metrics that should appear in report
        print(f"\n6. Key Metrics for Report:")
        print(f"   📊 Active Users: {community_stats.get('active_users', 0)}")
        print(f"   📝 Total Posts: {community_stats.get('total_posts', 0)}")
        print(f"   💬 Total Comments: {community_stats.get('total_comments', 0)}")
        print(f"   👍 Total Upvotes: {community_stats.get('total_upvotes', 0)}")
        print(f"   📈 Engagement Rate: {community_stats.get('engagement_rate', 0):.2f}%")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    debug_report_data()
