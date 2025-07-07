#!/usr/bin/env python3
"""
Test script to generate a real daily report and verify all components work
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import HiveEcuadorPulse


def test_real_report_generation():
    """Test generating a real daily report with actual data"""
    print("🇪🇨 Testing Real Daily Report Generation")
    print("=" * 50)
    
    try:
        # Initialize the bot
        print("1. Initializing Hive Ecuador Pulse Bot...")
        bot = HiveEcuadorPulse()
        print("   ✅ Bot initialized successfully")
        
        # Check database connection
        print("\n2. Checking database...")
        with bot.db_manager.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            print(f"   ✅ Found {active_users} active users in database")
        
        # Test API connectivity
        print("\n3. Testing API connectivity...")
        community_followers = bot.hive_api.get_community_followers("hive-115276")
        print(f"   ✅ Found {len(community_followers)} community members via API")
        
        # Test individual user data collection
        print("\n4. Testing individual user data collection...")
        if community_followers:
            test_user = community_followers[0]
            print(f"   Testing with user: {test_user}")
            
            # Get account info
            account_info = bot.hive_api.get_account_info_extended(test_user)
            if account_info:
                print(f"   ✅ Got account info for {test_user}")
                print(f"      - Posts: {account_info.get('post_count', 0)}")
                print(f"      - Reputation: {account_info.get('reputation', 0)}")
            else:
                print(f"   ⚠️ Could not get account info for {test_user}")
            
            # Get blockchain activity
            activity = bot.hive_api.get_user_blockchain_activity(test_user, days=7)
            print(f"   ✅ Found {len(activity)} blockchain activities for {test_user}")
        
        # Generate actual daily report
        print("\n5. Generating real daily report...")
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Force generate a report
        report_data = bot.create_daily_report()
        
        if report_data:
            print("   ✅ Daily report generated successfully!")
            
            # Check if charts were created
            import glob
            chart_files = glob.glob(f"charts/*{datetime.now().strftime('%Y%m%d')}*.png")
            print(f"   ✅ Generated {len(chart_files)} chart files")
            
            # Check if report file was created
            report_files = glob.glob(f"report_{today}*.md")
            if report_files:
                latest_report = max(report_files, key=os.path.getctime)
                print(f"   ✅ Report file created: {latest_report}")
                
                # Show report size and sample content
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"   ✅ Report size: {len(content)} characters")
                    
                    # Show first few lines
                    lines = content.split('\n')[:10]
                    print("   📄 Report preview:")
                    for line in lines:
                        print(f"      {line}")
                    
                    if len(lines) > 10:
                        print("      ...")
            else:
                print("   ⚠️ No report file found")
        else:
            print("   ❌ Failed to generate daily report")
        
        print("\n" + "=" * 50)
        print("🎉 Real report generation test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during report generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_real_report_generation()
    sys.exit(0 if success else 1)
