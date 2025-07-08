#!/usr/bin/env python3
"""
Debug script to test Patacoins template rendering
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reporting.generator import ReportGenerator

def test_template_rendering():
    """Test the Patacoins template rendering with sample data"""
    print("🪙 Testing Patacoins Template Rendering")
    print("=" * 50)
    
    try:
        # Initialize generator
        config = {'include_charts': True, 'max_images': 10, 'markdown_formatting': True}
        gen = ReportGenerator(config)
        
        # Create sample data structure like what the collector would provide
        sample_data = {
            'top_performers': {
                'top_poster': {'username': 'angelica7', 'count': 5},
                'top_commenter': {'username': 'jcrodriguez', 'count': 10},
                'top_supporter': {'username': 'kpoulout', 'count': 15},
                'rising_star': {'username': 'jersont', 'engagement_score': 8.5},
                'consistent_contributor': {'username': 'beelzael', 'consistency_score': 90}
            },
            'user_activities': [
                {'username': 'angelica7', 'patacoins_earned': 12.5},
                {'username': 'jcrodriguez', 'patacoins_earned': 8.2},
                {'username': 'kpoulout', 'patacoins_earned': 15.7},
                {'username': 'jersont', 'patacoins_earned': 6.3},
                {'username': 'beelzael', 'patacoins_earned': 9.1}
            ]
        }
        
        print("1. Testing individual spotlight section generation...")
        
        # Test the method directly
        result = gen.generate_individual_spotlight_section(sample_data)
        
        print("2. Generated content:")
        print("-" * 30)
        print(result)
        print("-" * 30)
        
        # Check if Patacoins are mentioned
        if "Patacoins" in result or "🪙" in result:
            print("✅ Patacoins content found in output!")
            
            # Extract Patacoins-specific lines
            lines = result.split('\n')
            for i, line in enumerate(lines):
                if 'Patacoins' in line or '🪙' in line:
                    print(f"Patacoins line {i}: {line}")
        else:
            print("❌ Patacoins content NOT found in output")
            
        print("\n🎉 Template test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template_rendering()
