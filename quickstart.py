#!/usr/bin/env python3
"""
Quick start script for Hive Ecuador Pulse Bot
Initializes the bot and runs a quick test
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Quick start the bot"""
    print("🇪🇨 Hive Ecuador Pulse Bot - Quick Start")
    print("=" * 50)
    
    try:
        # Import main bot class
        from main import HiveEcuadorPulse
        
        print("✅ Bot modules imported successfully")
        
        # Create bot instance
        bot = HiveEcuadorPulse()
        
        print("✅ Bot initialized successfully")
        print(f"   Bot name: {bot.config['bot_name']}")
        print(f"   Version: {bot.config['version']}")
        print(f"   Community: {bot.config['community']}")
        print(f"   Dry run mode: {bot.config.get('dry_run', False)}")
        
        # Initialize database
        bot.db_manager.initialize_database()
        print("✅ Database initialized")
        
        # Get database stats
        stats = bot.db_manager.get_database_stats()
        print(f"   Database tables created: {len(stats)}")
        
        # Test configuration
        print("\n🔧 Configuration:")
        print(f"   Report time: {bot.config['report_time']}")
        print(f"   Timezone: {bot.config['timezone']}")
        print(f"   Charts directory: {bot.config['charts_directory']}")
        
        # Test user management
        print("\n👥 Testing user management:")
        success, message = bot.user_manager.add_user("testuser")
        print(f"   Add user: {message}")
        
        success, message = bot.user_manager.list_tracked_users()
        print(f"   List users: {len(message.split(','))} users tracked")
        
        # Test business management
        print("\n🏢 Testing business management:")
        success, message = bot.user_manager.add_business("testbusiness", "Test Business", "Technology")
        print(f"   Add business: {message}")
        
        success, message = bot.user_manager.list_businesses()
        print(f"   List businesses: Business list generated")
        
        print("\n🎯 Quick start completed successfully!")
        print("   The bot is ready to use.")
        print("   To run the full bot, use: python main.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready to launch! Use 'python main.py' to start the bot.")
    else:
        print("\n⚠️ Please fix the issues above before running the bot.")
    
    sys.exit(0 if success else 1)
