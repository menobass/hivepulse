#!/usr/bin/env python3
"""
Debug script to test the bridge.list_subscribers API with different community name formats
"""

import requests
import json
import time

# Test different Hive API nodes and community name formats
nodes = [
    "https://api.hive.blog",
    "https://hived.emre.sh",
    "https://api.deathwing.me",
    "https://rpc.ausbit.dev",
    "https://hive-api.arcange.eu"
]

# Different community name formats to test
community_formats = [
    "hive-115276",           # Full name with prefix
    "115276",                # Just the number
    "hive-115276",           # Standard format
]

def test_subscribers_api():
    """Test bridge.list_subscribers API with different formats"""
    
    for node in nodes:
        print(f"\n=== Testing node: {node} ===")
        
        for community in community_formats:
            print(f"\nTesting community format: '{community}'")
            
            # Test with small limit first
            for limit in [10, 50, 100]:
                print(f"  Testing limit: {limit}")
                
                payload = {
                    "jsonrpc": "2.0",
                    "method": "bridge.list_subscribers",
                    "params": [{
                        "community": community,
                        "limit": limit
                    }],
                    "id": 1
                }
                
                try:
                    response = requests.post(
                        node,
                        json=payload,
                        timeout=15,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'result' in data:
                            result = data['result']
                            if result:
                                print(f"    ✅ SUCCESS: Found {len(result)} subscribers")
                                print(f"    First few: {result[:3] if len(result) >= 3 else result}")
                                return True  # Found working combination
                            else:
                                print(f"    ⚠️  Empty result")
                        elif 'error' in data:
                            print(f"    ❌ API Error: {data['error']}")
                        else:
                            print(f"    ⚠️  Unexpected response format")
                    else:
                        print(f"    ❌ HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"    ❌ Exception: {e}")
                
                time.sleep(1)  # Be nice to the API
    
    return False

if __name__ == "__main__":
    print("Testing Hive bridge.list_subscribers API...")
    print("Looking for the correct community name format and node combination")
    
    success = test_subscribers_api()
    
    if not success:
        print("\n❌ No working combination found")
        print("The community might not have subscribers or the API might be having issues")
    else:
        print("\n✅ Found working API combination!")
