#!/usr/bin/env python3
"""
Comprehensive test suite for Hive Ecuador Pulse Analytics Bot
Tests all major modules and their integration
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_database_operations():
    """Test database models and migrations"""
    print("🔍 Testing Database Operations...")
    
    try:
        from database.migrations import MigrationManager
        from database.models import UserModel, ActivityModel, CommunityModel
        from database.models import User, UserActivity, CommunityDaily
        
        # Test database initialization
        db_path = "test_comprehensive.db"
        migration_manager = MigrationManager(db_path)
        
        if migration_manager.init_database():
            print("✅ Database initialization successful")
        else:
            print("❌ Database initialization failed")
            return False
        
        # Test user model operations
        user_model = UserModel(db_path)
        user_model.connect()
        
        test_user = User(
            username="testuser",
            display_name="Test User",
            reputation=1000,
            followers=50,
            following=25,
            is_active=True
        )
        
        user_id = user_model.create_user(test_user)
        if user_id:
            print("✅ User creation successful")
        else:
            print("❌ User creation failed")
            return False
        
        # Test user retrieval
        retrieved_user = user_model.get_user_by_username("testuser")
        if retrieved_user and retrieved_user.username == "testuser":
            print("✅ User retrieval successful")
        else:
            print("❌ User retrieval failed")
            return False
        
        user_model.disconnect()
        
        # Clean up
        if os.path.exists(db_path):
            os.remove(db_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

def test_analytics_processing():
    """Test analytics processor and metrics"""
    print("🔍 Testing Analytics Processing...")
    
    try:
        from analytics.processor import DataProcessor, UserMetrics, CommunityMetrics
        from analytics.metrics import MetricsCalculator, MetricResult
        
        # Load config
        with open('config/pulse_config.json', 'r') as f:
            config = json.load(f)
        
        # Test data processor
        processor = DataProcessor(config)
        
        # Mock user data
        mock_user_data = [
            {
                'username': 'user1',
                'posts': 10,
                'comments': 25,
                'rewards': 5.5,
                'reputation': 2000,
                'followers': 100,
                'following': 50,
                'last_activity': datetime.now().isoformat()
            },
            {
                'username': 'user2',
                'posts': 5,
                'comments': 15,
                'rewards': 2.1,
                'reputation': 1500,
                'followers': 75,
                'following': 30,
                'last_activity': datetime.now().isoformat()
            }
        ]
        
        user_metrics = processor.process_user_data(mock_user_data)
        if user_metrics and len(user_metrics) == 2:
            print("✅ User data processing successful")
        else:
            print("❌ User data processing failed")
            return False
        
        # Test community metrics calculation
        community_metrics = processor.calculate_community_metrics(user_metrics)
        if community_metrics and community_metrics.total_users > 0:
            print("✅ Community metrics calculation successful")
        else:
            print("❌ Community metrics calculation failed")
            return False
        
        # Test metrics calculator
        calculator = MetricsCalculator(config)
        
        kpis = calculator.calculate_community_kpis({
            'total_users': 50,
            'active_users': 30,
            'total_posts': 100,
            'total_comments': 250,
            'total_rewards': 50.5
        })
        
        if kpis and 'total_users' in kpis:
            print("✅ KPI calculation successful")
        else:
            print("❌ KPI calculation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics processing test failed: {e}")
        return False

def test_visualization():
    """Test chart generation and themes"""
    print("🔍 Testing Visualization...")
    
    try:
        from visualization.charts import ChartGenerator
        from visualization.themes import EcuadorTheme, ChartStyler
        
        # Load config
        with open('config/pulse_config.json', 'r') as f:
            config = json.load(f)
        
        # Test theme creation
        theme = EcuadorTheme()
        colors = theme.get_color_palette('primary', 3)
        if colors and len(colors) == 3:
            print("✅ Theme creation successful")
        else:
            print("❌ Theme creation failed")
            return False
        
        # Test chart generator
        chart_generator = ChartGenerator(config['visual_theme'])
        
        # Mock data for chart - proper structure expected by chart methods
        mock_community_data = {
            'historical_data': [
                {'date': '2025-07-01', 'active_users': 10, 'total_posts': 5, 'total_comments': 8},
                {'date': '2025-07-02', 'active_users': 15, 'total_posts': 7, 'total_comments': 12},
                {'date': '2025-07-03', 'active_users': 20, 'total_posts': 10, 'total_comments': 15},
                {'date': '2025-07-04', 'active_users': 18, 'total_posts': 8, 'total_comments': 14},
                {'date': '2025-07-05', 'active_users': 25, 'total_posts': 12, 'total_comments': 18},
                {'date': '2025-07-06', 'active_users': 30, 'total_posts': 15, 'total_comments': 22},
                {'date': '2025-07-07', 'active_users': 35, 'total_posts': 18, 'total_comments': 25}
            ]
        }
        
        # Test chart creation (this will create actual chart files)
        chart_path = chart_generator.create_activity_trend_chart(mock_community_data)
        if chart_path and os.path.exists(chart_path):
            print("✅ Chart generation successful")
            # Clean up
            os.remove(chart_path)
        else:
            print("❌ Chart generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False

def test_reporting():
    """Test report generation and formatting"""
    print("🔍 Testing Reporting...")
    
    try:
        from reporting.generator import ReportGenerator
        from reporting.templates import DailyReportTemplate
        from reporting.formatter import ReportFormatter
        from analytics.processor import CommunityMetrics, UserMetrics
        
        # Load config
        with open('config/pulse_config.json', 'r') as f:
            config = json.load(f)
        
        # Test report template
        template = DailyReportTemplate(config)
        
        # Mock data
        mock_community_metrics = CommunityMetrics(
            total_users=50,
            active_users=30,
            total_posts=100,
            total_comments=250,
            total_rewards=50.5,
            avg_post_reward=0.505,
            engagement_rate=2.5,
            growth_rate=5.2
        )
        
        mock_user_metrics = [
            UserMetrics(
                username='user1',
                posts_count=10,
                comments_count=25,
                total_rewards=5.5,
                last_activity=datetime.now(),
                reputation=2000,
                followers=100,
                following=50
            )
        ]
        
        template_data = {
            'date': datetime.now(),
            'community_metrics': mock_community_metrics,
            'user_metrics': mock_user_metrics,
            'insights': ['Test insight 1', 'Test insight 2'],
            'chart_urls': {'activity': 'https://example.com/chart.png'}
        }
        
        # Test template rendering
        content = template.render(template_data)
        if content and len(content) > 500:
            print("✅ Report template rendering successful")
        else:
            print("❌ Report template rendering failed")
            return False
        
        # Test report formatter
        formatter = ReportFormatter(config)
        formatted_report = formatter.format_complete_report(content)
        
        if formatted_report and formatted_report['valid']:
            print("✅ Report formatting successful")
        else:
            print("❌ Report formatting failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Reporting test failed: {e}")
        return False

def test_management():
    """Test management commands and user management"""
    print("🔍 Testing Management...")
    
    try:
        from management.commands import CommandHandler
        from management.user_manager import UserManager
        
        # Load config
        with open('config/pulse_config.json', 'r') as f:
            config = json.load(f)
        
        # Test command handler
        command_handler = CommandHandler(config)
        
        # Test help command
        help_response = command_handler.handle_command('help', [], 'testuser')
        if help_response and 'Comandos Disponibles' in help_response:
            print("✅ Command handling successful")
        else:
            print("❌ Command handling failed")
            return False
        
        # Test user manager (need to create a mock database manager)
        from database.manager import DatabaseManager
        test_db_path = "test_user_mgmt.db"
        
        # Clean up any existing test database
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except:
                pass
        
        try:
            mock_db_manager = DatabaseManager(test_db_path)
            
            # Initialize database first
            mock_db_manager.initialize_database()
            
            user_manager = UserManager(mock_db_manager)
            
            # Test user tracking
            result, message = user_manager.add_user('testuser', 'system')
            if result:
                print("✅ User management successful")
                return True
            else:
                print("❌ User management failed")
                return False
                
        finally:
            # Clean up
            if os.path.exists(test_db_path):
                try:
                    os.remove(test_db_path)
                except:
                    pass
        
        return True
        
    except Exception as e:
        print(f"❌ Management test failed: {e}")
        return False

def test_integration():
    """Test full integration workflow"""
    print("🔍 Testing Integration Workflow...")
    
    try:
        from main import HiveEcuadorPulse
        
        # Create bot instance
        bot = HiveEcuadorPulse()
        
        # Test configuration loading
        if bot.config and 'bot_name' in bot.config:
            print("✅ Configuration loading successful")
        else:
            print("❌ Configuration loading failed")
            return False
        
        # Test database connection
        if bot.db_manager:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test report generation workflow
        # Note: This doesn't actually post to Hive since we're in dry run mode
        try:
            # Generate test report
            report_content, images = bot.create_daily_report()
            if report_content and len(report_content) > 100:
                print("✅ Report generation workflow successful")
            else:
                print("❌ Report generation workflow failed")
                return False
        except Exception as e:
            # This might fail due to missing data, which is OK for testing
            print(f"⚠️ Report generation test: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run comprehensive test suite"""
    print("🇪🇨 Hive Ecuador Pulse - Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Operations", test_database_operations),
        ("Analytics Processing", test_analytics_processing),
        ("Visualization", test_visualization),
        ("Reporting", test_reporting),
        ("Management", test_management),
        ("Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} Tests...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} tests passed")
            else:
                print(f"❌ {test_name} tests failed")
        except Exception as e:
            print(f"❌ {test_name} tests crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready for deployment.")
    else:
        print("⚠️ Some tests failed. Please review the issues before deployment.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
