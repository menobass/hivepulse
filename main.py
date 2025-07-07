#!/usr/bin/env python3
"""
Hive Ecuador Pulse Analytics Bot
Main entry point for the bot application
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analytics.collector import AnalyticsCollector
from visualization.charts import ChartGenerator
from reporting.generator import ReportGenerator
from database.manager import DatabaseManager
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
        self.analytics_collector = AnalyticsCollector(self.hive_api, self.db_manager)
        self.chart_generator = ChartGenerator(self.config['visual_theme'])
        self.report_generator = ReportGenerator(self.config['post_template'])
        self.user_manager = UserManager(self.db_manager)
        self.scheduler = ReportScheduler(self)
        
        self.logger.info("Hive Ecuador Pulse Bot initialized successfully")
    
    def collect_daily_data(self, date: Optional[str] = None) -> Dict:
        """Collect all daily analytics data"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.logger.info(f"Collecting daily data for {date}")
        
        try:
            # Collect community activity data
            community_data = self.analytics_collector.get_community_activity(date)
            
            # Collect individual user activities
            user_activities = self.analytics_collector.get_user_activities(date)
            
            # Collect business transaction data
            business_data = self.analytics_collector.track_business_activity(date)
            
            # Calculate engagement metrics
            engagement_metrics = self.analytics_collector.calculate_engagement_metrics({
                'community': community_data,
                'users': user_activities,
                'business': business_data
            })
            
            # Identify top performers
            top_performers = self.analytics_collector.identify_top_performers(user_activities)
            
            return {
                'date': date,
                'community': community_data,
                'users': user_activities,
                'business': business_data,
                'engagement': engagement_metrics,
                'top_performers': top_performers
            }
            
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
            activity_chart = self.chart_generator.create_activity_trend_chart(data['community'])
            chart_files.append(activity_chart)
            
            posts_chart = self.chart_generator.create_posts_volume_chart(data['community'])
            chart_files.append(posts_chart)
            
            comments_chart = self.chart_generator.create_comments_chart(data['community'])
            chart_files.append(comments_chart)
            
            upvotes_chart = self.chart_generator.create_upvotes_chart(data['community'])
            chart_files.append(upvotes_chart)
            
            # Generate financial charts if business data exists
            if data['business']['transactions']:
                hbd_chart = self.chart_generator.create_hbd_flow_chart(data['business'])
                chart_files.append(hbd_chart)
            
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
                tags=['hive-ecuador', 'analytics', 'community', 'daily-report', 'pulse'],
                community='hive-115276'
            )
            
            if post_result:
                # Record successful report in database
                self.db_manager.record_generated_report(
                    date=datetime.now().strftime('%Y-%m-%d'),
                    post_author=self.config['posting_account'],
                    post_permlink=post_result['permlink'],
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
    try:
        # Create bot instance
        bot = HiveEcuadorPulse()
        
        # Run the bot
        bot.run()
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
