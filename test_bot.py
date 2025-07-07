#!/usr/bin/env python3
"""
Test script for Hive Ecuador Pulse Bot
Quick verification that all components work correctly
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from analytics.collector import AnalyticsCollector
        print("✅ Analytics collector imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import analytics collector: {e}")
        return False
    
    try:
        from visualization.charts import ChartGenerator
        print("✅ Chart generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chart generator: {e}")
        return False
    
    try:
        from reporting.generator import ReportGenerator
        print("✅ Report generator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import report generator: {e}")
        return False
    
    try:
        from database.manager import DatabaseManager
        print("✅ Database manager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database manager: {e}")
        return False
    
    try:
        from management.user_manager import UserManager
        print("✅ User manager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import user manager: {e}")
        return False
    
    try:
        from management.scheduler import ReportScheduler
        print("✅ Report scheduler imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import report scheduler: {e}")
        return False
    
    try:
        from utils.hive_api import HiveAPIClient
        print("✅ Hive API client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Hive API client: {e}")
        return False
    
    try:
        from utils.helpers import load_config, setup_logging
        print("✅ Helper functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import helper functions: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from utils.helpers import load_config
        
        config = load_config("config/pulse_config.json")
        
        required_keys = ['bot_name', 'community', 'posting_account', 'report_time']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required config key: {key}")
                return False
        
        print("✅ Configuration loaded successfully")
        print(f"   Bot name: {config['bot_name']}")
        print(f"   Community: {config['community']}")
        print(f"   Report time: {config['report_time']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🗃️ Testing database...")
    
    try:
        from database.manager import DatabaseManager
        
        # Use a test database
        db = DatabaseManager("test_pulse_analytics.db")
        
        # Initialize database
        db.initialize_database()
        print("✅ Database initialized successfully")
        
        # Test basic operations
        success = db.add_user("testuser")
        if success:
            print("✅ User addition test passed")
        else:
            print("❌ User addition test failed")
            return False
        
        users = db.get_tracked_users()
        if "testuser" in users:
            print("✅ User retrieval test passed")
        else:
            print("❌ User retrieval test failed")
            return False
        
        # Clean up
        os.remove("test_pulse_analytics.db")
        print("✅ Database test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_chart_generation():
    """Test chart generation"""
    print("\n📊 Testing chart generation...")
    
    try:
        from visualization.charts import ChartGenerator
        
        # Test configuration
        theme_config = {
            'ecuador_colors': {
                'yellow': '#FFDD00',
                'blue': '#0052CC',
                'red': '#FF0000'
            },
            'chart_style': 'professional',
            'font_family': 'Arial'
        }
        
        chart_gen = ChartGenerator(theme_config)
        print("✅ Chart generator initialized successfully")
        
        # Test header image creation
        header_image = chart_gen.create_header_image("2025-01-01")
        if header_image and os.path.exists(header_image):
            print("✅ Header image generation test passed")
            # Clean up
            os.remove(header_image)
        else:
            print("❌ Header image generation test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Chart generation test failed: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("\n📝 Testing report generation...")
    
    try:
        from reporting.generator import ReportGenerator
        
        template_config = {
            'header_image': True,
            'include_charts': True,
            'max_images': 10,
            'markdown_formatting': True
        }
        
        report_gen = ReportGenerator(template_config)
        print("✅ Report generator initialized successfully")
        
        # Test data
        test_data = {
            'date': '2025-01-01',
            'community': {
                'active_users': 50,
                'total_posts': 25,
                'total_comments': 100,
                'total_upvotes': 500,
                'engagement_rate': 2.0,
                'historical_data': []
            },
            'users': [],
            'business': {
                'active_businesses': 5,
                'total_hbd_volume': 100.0,
                'transactions': []
            },
            'engagement': {
                'health_index': 75.0,
                'engagement_distribution': {'low': 10, 'medium': 30, 'high': 10}
            },
            'top_performers': {
                'top_poster': {'users': ['testuser'], 'count': 5},
                'top_commenter': {'users': ['testuser2'], 'count': 15},
                'top_supporter': {'users': ['testuser3'], 'count': 25}
            }
        }
        
        report_content = report_gen.generate_full_report(test_data, [])
        if report_content and len(report_content) > 100:
            print("✅ Report generation test passed")
            print(f"   Generated {len(report_content)} characters")
        else:
            print("❌ Report generation test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Hive Ecuador Pulse Bot Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_chart_generation,
        test_report_generation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The bot is ready to use.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
