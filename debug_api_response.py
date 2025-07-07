#!/usr/bin/env python3

"""
Debug script to examine the exact API response structure from bridge.list_subscribers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.hive_api import HiveAPIClient
import json

def debug_subscribers_api():
    """Debug the subscribers API response structure"""
    
    config = {
        'HIVE_ACCOUNT_NAME': 'hiveecuador',
        'IMAGE_UPLOAD_SERVICE': 'https://images.hive.blog'
    }
    
    client = HiveAPIClient(config)
    
    print("🔍 Testing bridge.list_subscribers API response structure...")
    
    # Test with small limit to see exact structure
    result = client._make_api_call_with_failover('bridge.list_subscribers', [{
        "community": "hive-115276",
        "limit": 5
    }])
    
    print(f"\n📋 Raw API Response (first 5 subscribers):")
    print(f"Type: {type(result)}")
    print(f"Content: {json.dumps(result, indent=2)}")
    
    if result and isinstance(result, list):
        print(f"\n🔍 Analyzing structure:")
        for i, item in enumerate(result):
            print(f"  Item {i}: Type={type(item)}, Content={item}")
            
            if isinstance(item, list):
                print(f"    → Array with {len(item)} elements")
                for j, element in enumerate(item):
                    print(f"      [{j}]: {element} (type: {type(element)})")
            elif isinstance(item, dict):
                print(f"    → Dict with keys: {list(item.keys())}")
                for key, value in item.items():
                    print(f"      {key}: {value}")
    
    # Test a different approach
    print(f"\n🔍 Testing with different parameters...")
    result2 = client._make_api_call_with_failover('bridge.list_subscribers', [{
        "community": "hive-115276",
        "limit": 10,
        "last": ""
    }])
    
    print(f"\nAlternative API Response:")
    print(f"Type: {type(result2)}")
    if result2:
        print(f"Length: {len(result2)}")
        if len(result2) > 0:
            print(f"First item: {result2[0]} (type: {type(result2[0])})")

if __name__ == "__main__":
    debug_subscribers_api()
