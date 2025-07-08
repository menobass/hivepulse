#!/usr/bin/env python3
"""
Test script to generate a new report with Patacoins display
"""

import sys
import os
import logging
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import HiveEcuadorPulse

def test_patacoins_report():
    """Test generating a report with Patacoins information"""
    print("🪙 Testing Patacoins Report Generation")
    print("=" * 50)
    
    try:
        # Initialize bot
        print("1. Initializing bot...")
        bot = HiveEcuadorPulse()
        
        # Force generate a new report
        print("2. Generating fresh daily report with Patacoins...")
        report_content = bot.create_daily_report()
        
        if report_content:
            # Find the latest report file
            import glob
            report_files = glob.glob("report_*.md")
            if report_files:
                latest_report = max(report_files, key=os.path.getctime)
                print(f"   ✅ Report generated: {latest_report}")
                
                # Show preview
                with open(latest_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:800] + "..." if len(content) > 800 else content
                    print(f"\n📄 Report preview:\n{preview}")
                    
                    # Check for Patacoins content
                    if "patacoins" in content.lower() or "🪙" in content:
                        print("\n🎉 Patacoins content detected in report!")
                    else:
                        print("\n⚠️ Patacoins content not found in report")
                        
            else:
                print("   ❌ No report file found")
        else:
            print("   ❌ Report generation failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_patacoins_report()
