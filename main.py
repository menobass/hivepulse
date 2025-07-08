#!/usr/bin/env python3
"""
Hive Ecuador Pulse Analytics Bot
Main entry point for the bot application
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics.collector import AnalyticsCollector
from visualization.charts import ChartGenerator
from reporting.generator import ReportGenerator
from database.manager import DatabaseManager
from database.migrations import InitialMigration, AddUserTagsMigration
from management.user_manager import UserManager
from management.scheduler import ReportScheduler
from utils.hive_api import HiveAPIClient
from utils.helpers import load_config, setup_logging


class HiveEcuadorPulse:
    """Main bot class that orchestrates all components"""
    
    def __init__(self, config_path: str = "config/pulse_config.json"):
        """Initialize the bot with configuration"""
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config.get('log_level', 'INFO'))
        
        # Initialize components
        self.db_manager = DatabaseManager(self.config['database_file'])
        self.hive_api = HiveAPIClient(self.config)
        self.analytics_collector = AnalyticsCollector(self.hive_api, self.db_manager, self.config)
        self.chart_generator = ChartGenerator(self.config['visual_theme'])
        self.report_generator = ReportGenerator(self.config['post_template'])
        self.user_manager = UserManager(self.db_manager)
        self.scheduler = ReportScheduler(self)
        
        self.logger.info("Hive Ecuador Pulse Bot initialized successfully")
    
    def initialize_database(self):
        """Initialize database using migrations"""
        self.logger.info("Initializing database using migrations...")
        
        try:
            # Run initial migration
            initial_migration = InitialMigration()
            with self.db_manager.get_connection() as conn:
                if initial_migration.up(conn):
                    self.logger.info("Initial migration completed successfully")
                else:
                    self.logger.error("Initial migration failed")
                    return False
            
            # Run additional migrations
            tags_migration = AddUserTagsMigration()
            with self.db_manager.get_connection() as conn:
                if tags_migration.up(conn):
                    self.logger.info("User tags migration completed successfully")
                else:
                    self.logger.error("User tags migration failed")
                    return False
            
            self.logger.info("Database initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            return False

    def collect_daily_data(self, date: Optional[str] = None) -> Dict:
        """Collect all daily analytics data with automatic member sync"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.logger.info(f"Collecting daily data with member sync for {date}")
        
        try:
            # Use the new collection system with automatic member discovery
            return self.analytics_collector.collect_daily_data_with_member_sync(date)
            
        except Exception as e:
            self.logger.error(f"Error collecting daily data: {str(e)}")
            raise
    
    def generate_charts(self, data: Dict) -> List[str]:
        """Generate all charts for the daily report"""
        self.logger.info("Generating charts for daily report")
        
        try:
            chart_files = []
            
            # Generate header image
            header_image = self.chart_generator.create_header_image(data['date'])
            chart_files.append(header_image)
            
            # Generate community health charts
            activity_chart = self.chart_generator.create_activity_trend_chart(data['community_stats'])
            chart_files.append(activity_chart)
            
            posts_chart = self.chart_generator.create_posts_volume_chart(data['community_stats'])
            chart_files.append(posts_chart)
            
            comments_chart = self.chart_generator.create_comments_chart(data['community_stats'])
            chart_files.append(comments_chart)
            
            upvotes_chart = self.chart_generator.create_upvotes_chart(data['community_stats'])
            chart_files.append(upvotes_chart)
            
            # Generate financial charts if business data exists
            # TODO: Implement business data collection
            # if data.get('business', {}).get('transactions'):
            #     hbd_chart = self.chart_generator.create_hbd_flow_chart(data['business'])
            #     chart_files.append(hbd_chart)
            
            self.logger.info(f"Generated {len(chart_files)} charts successfully")
            return chart_files
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
            raise
    
    def create_daily_report(self, date: Optional[str] = None) -> tuple:
        """Create the complete daily report with content and images"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.logger.info(f"Creating daily report for {date}")
        
        try:
            # Collect data
            data = self.collect_daily_data(date)
            
            # Generate charts
            chart_files = self.generate_charts(data)
            
            # Generate report content
            report_content = self.report_generator.generate_full_report(data, chart_files)
            
            self.logger.info("Daily report created successfully")
            return report_content, chart_files
            
        except Exception as e:
            self.logger.error(f"Error creating daily report: {str(e)}")
            raise
    
    def post_daily_report(self, report_content: str, images: List[str]) -> bool:
        """Post the daily report to Hive blockchain"""
        self.logger.info("Posting daily report to Hive blockchain")
        
        try:
            # Upload images first
            uploaded_images = []
            for image_path in images:
                uploaded_url = self.hive_api.upload_image(image_path)
                uploaded_images.append(uploaded_url)
            
            # Replace local image paths with uploaded URLs in content
            final_content = self.report_generator.replace_image_urls(report_content, uploaded_images)
            
            # Post to Hive
            post_result = self.hive_api.post_content(
                title=f"🇪🇨 Hive Ecuador Pulse - Daily Report {datetime.now().strftime('%B %d, %Y')}",
                body=final_content,
                tags=['hive-ecuador', 'analytics', 'community', 'daily-report', 'pulse']
            )
            
            if post_result:
                # Record successful report in database
                self.db_manager.record_generated_report(
                    date=datetime.now().strftime('%Y-%m-%d'),
                    post_author=self.config.get('posting_account', 'hiveecuador'),
                    post_permlink=f"pulse-{datetime.now().strftime('%Y-%m-%d')}",  # Generate permlink
                    charts_generated=len(images),
                    success=True
                )
                
                self.logger.info("Daily report posted successfully")
                return True
            else:
                self.logger.error("Failed to post daily report")
                return False
                
        except Exception as e:
            self.logger.error(f"Error posting daily report: {str(e)}")
            return False
    
    def schedule_daily_reports(self):
        """Start the scheduler for daily reports"""
        self.logger.info("Starting daily report scheduler")
        self.scheduler.start()
    
    def run(self):
        """Main run method to start the bot"""
        self.logger.info("Starting Hive Ecuador Pulse Bot")
        
        try:
            # Initialize database
            self.db_manager.initialize_database()
            
            # Start scheduler
            self.schedule_daily_reports()
            
            # Keep the bot running
            self.logger.info("Bot is running. Press Ctrl+C to stop.")
            
            # For testing purposes, generate a report now
            if self.config.get('generate_test_report', False):
                self.logger.info("Generating test report...")
                content, images = self.create_daily_report()
                
                if not self.config.get('dry_run', True):
                    self.post_daily_report(content, images)
                else:
                    self.logger.info("Dry run mode - report not posted")
                    print("Test report generated successfully!")
            
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Error running bot: {str(e)}")
            raise


def main():
    """Main function to run the bot"""
    parser = argparse.ArgumentParser(description='Hive Ecuador Pulse Analytics Bot')
    parser.add_argument('--init-db', action='store_true', 
                       help='Initialize database with required tables')
    parser.add_argument('--config', type=str, default='config/pulse_config.json',
                       help='Path to configuration file')
    parser.add_argument('--generate-report', action='store_true',
                       help='Generate a test report')
    parser.add_argument('--add-user', type=str, metavar='USERNAME',
                       help='Add a user to tracking')
    parser.add_argument('--list-users', action='store_true',
                       help='List all tracked users')
    parser.add_argument('--sync-members', action='store_true',
                       help='Sync community members from Hive followers')
    parser.add_argument('--member-stats', action='store_true',
                       help='Show community membership statistics')
    parser.add_argument('--force-resync', action='store_true',
                       help='Force complete resync of all members (use carefully!)')
    parser.add_argument('--status', action='store_true',
                       help='Show bot status and configuration')
    
    args = parser.parse_args()
    
    try:
        # Create bot instance
        bot = HiveEcuadorPulse(args.config)
        
        # Handle command-line operations
        if args.init_db:
            print("Initializing database...")
            if bot.initialize_database():
                print("Database initialized successfully!")
            else:
                print("Database initialization failed!")
                sys.exit(1)
            return
            
        if args.sync_members:
            print("Syncing community members from Hive followers...")
            from management.community_manager import CommunityMemberManager
            member_manager = CommunityMemberManager(bot.hive_api, bot.db_manager)
            sync_results = member_manager.sync_community_members()
            print(f"✅ Sync completed:")
            print(f"   Total followers: {sync_results['total_followers']}")
            print(f"   Total tracked: {sync_results['total_tracked']}")
            print(f"   New members: {sync_results['new_members']}")
            print(f"   Left members: {sync_results['left_members']}")
            print(f"   Rejoined: {sync_results['rejoined_members']}")
            return
            
        if args.member_stats:
            print("Community membership statistics:")
            from management.community_manager import CommunityMemberManager
            member_manager = CommunityMemberManager(bot.hive_api, bot.db_manager)
            stats = member_manager.get_membership_stats()
            print(f"   Total members: {stats['total_members']}")
            print(f"   Active today: {stats['active_today']}")
            print(f"   Active this week: {stats['active_this_week']}")
            print(f"   New this week: {stats['new_this_week']}")
            print(f"   Engagement rate: {stats['engagement_rate']:.1f}%")
            return
            
        if args.force_resync:
            print("⚠️  FORCE RESYNC: This will clear all current members and re-add from followers!")
            response = input("Are you sure? Type 'yes' to continue: ")
            if response.lower() == 'yes':
                from management.community_manager import CommunityMemberManager
                member_manager = CommunityMemberManager(bot.hive_api, bot.db_manager)
                if member_manager.force_resync_all_members():
                    print("✅ Force resync completed successfully!")
                else:
                    print("❌ Force resync failed!")
                    sys.exit(1)
            else:
                print("Force resync cancelled.")
            return
            
        if args.status:
            print("🤖 Hive Ecuador Pulse Bot Status")
            print("=" * 40)
            
            # Configuration status
            print("\n📋 Configuration:")
            print(f"   Config file: {args.config}")
            print(f"   Database: {bot.config['database_file']}")
            print(f"   Community: {bot.config.get('community_account', 'hive-ecuador')}")
            print(f"   Posting account: {bot.config.get('posting_account', 'hiveecuador')}")
            print(f"   Dry run mode: {bot.config.get('dry_run', True)}")
            print(f"   Log level: {bot.config.get('log_level', 'INFO')}")
            
            # Database status
            print("\n💾 Database Status:")
            try:
                users = bot.db_manager.get_tracked_users()
                print(f"   Tracked users: {len(users)}")
                
                # Get recent activity count (using user_activity_history)
                total_activities = 0
                for user in users[:5]:  # Check first 5 users to avoid slow queries
                    activities = bot.db_manager.get_user_activity_history(user, days=7)
                    total_activities += len(activities)
                print(f"   Recent activities (sample): {total_activities}")
                
                # Check last report
                with bot.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT date, success FROM generated_reports ORDER BY date DESC LIMIT 1")
                    last_report = cursor.fetchone()
                    if last_report:
                        print(f"   Last report: {last_report[0]} ({'✅ Success' if last_report[1] else '❌ Failed'})")
                    else:
                        print("   Last report: None")
                    
            except Exception as e:
                print(f"   ❌ Database error: {str(e)}")
            
            # Hive API status
            print("\n🔗 Hive API Status:")
            try:
                # Test API connection with posting account (should exist)
                test_account = bot.config.get('posting_account', 'hiveecuador')
                account_info = bot.hive_api.get_account_info_extended(test_account)
                if account_info:
                    print(f"   ✅ API connection working")
                    print(f"   Test account: @{test_account}")
                else:
                    print(f"   ❌ API connection failed (account @{test_account} not found)")
            except Exception as e:
                print(f"   ❌ API error: {str(e)}")
            
            # Scheduler status
            print("\n⏰ Scheduler Status:")
            schedule_time = bot.config.get('schedule_time', '21:00')
            timezone = bot.config.get('timezone', 'America/Guayaquil')
            print(f"   Report time: {schedule_time} ({timezone})")
            
            # Current time
            try:
                import pytz
                tz = pytz.timezone(timezone)
                current_time = datetime.now(tz)
                print(f"   Current time: {current_time.strftime('%H:%M:%S %Z')}")
                print(f"   Current date: {current_time.strftime('%Y-%m-%d')}")
            except Exception as e:
                print(f"   Current time: {datetime.now().strftime('%H:%M:%S')} (local)")
            
            # Patacoin system status
            print("\n🪙 Patacoin System:")
            patacoin_config = bot.config.get('patacoin_system', {})
            if patacoin_config.get('enabled', False):
                print(f"   ✅ Enabled")
                print(f"   Base reward: {patacoin_config.get('base_reward', 1)} PC")
                print(f"   Post bonus: {patacoin_config.get('post_bonus', 2)} PC")
                print(f"   Comment bonus: {patacoin_config.get('comment_bonus', 1)} PC")
                print(f"   Vote bonus: {patacoin_config.get('vote_bonus', 0.5)} PC")
                
                # Get total Patacoins in circulation
                try:
                    with bot.db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT SUM(total_balance) FROM patacoins_balances")
                        total_patacoins = cursor.fetchone()[0] or 0
                        print(f"   Total in circulation: {total_patacoins:.1f} PC")
                except Exception as e:
                    print(f"   ❌ Could not get circulation data: {str(e)}")
            else:
                print(f"   ❌ Disabled")
            
            # Environment variables check
            print("\n🔐 Environment:")
            posting_key_set = bool(os.getenv('HIVE_POSTING_KEY'))
            print(f"   Posting key: {'✅ Set' if posting_key_set else '❌ Not set'}")
            
            print("\n✅ Status check complete!")
            return
            
        if args.add_user:
            print(f"Adding user '{args.add_user}' to tracking...")
            if bot.user_manager.add_user(args.add_user):
                print(f"User '{args.add_user}' added successfully!")
            else:
                print(f"Failed to add user '{args.add_user}'")
                sys.exit(1)
            return
            
        if args.list_users:
            users = bot.db_manager.get_tracked_users()
            if users:
                print("Tracked users:")
                for username in users:
                    print(f"  - @{username}")
            else:
                print("No users being tracked yet.")
            return
            
        if args.generate_report:
            print("Generating test report...")
            content, images = bot.create_daily_report()
            
            # Save report to file
            date_str = datetime.now().strftime('%Y-%m-%d')
            report_filename = f"report_{date_str}_{datetime.now().strftime('%H%M%S')}.md"
            
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("Test report generated successfully!")
            print(f"Report saved to: {report_filename}")
            if images:
                print(f"Generated {len(images)} charts:")
                for img in images:
                    print(f"  - {img}")
            
            # Display a preview of the report
            print("\n" + "="*60)
            print("REPORT PREVIEW:")
            print("="*60)
            print(content[:1000] + "..." if len(content) > 1000 else content)
            print("="*60)
            return
        
        # Run the bot normally
        bot.run()
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
