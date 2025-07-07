#!/usr/bin/env python3
"""
Debug script to test the bridge.list_subscribers API call
"""

import requests
import json

def test_subscribers_api():
    """Test the bridge.list_subscribers API call directly"""
    
    # Hive API nodes to try
    nodes = [
        'https://api.hive.blog',
        'https://api.syncad.com',
        'https://api.deathwing.me',
        'https://hive-api.arcange.eu'
    ]
    
    community = "hive-115276"  # Hive Ecuador community
    
    for node in nodes:
        print(f"\n🔍 Testing node: {node}")
        
        # Test payload exactly as found in your Google search
        payload = {
            "jsonrpc": "2.0",
            "method": "bridge.list_subscribers",
            "params": {
                "community": community,
                "limit": 10
            },
            "id": 1
        }
        
        try:
            response = requests.post(
                node,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                
                if 'result' in data and data['result']:
                    print(f"✅ SUCCESS! Found {len(data['result'])} subscribers")
                    for i, subscriber in enumerate(data['result'][:5]):  # Show first 5
                        print(f"  {i+1}. {subscriber}")
                    break
                elif 'error' in data:
                    print(f"❌ API Error: {data['error']}")
                else:
                    print(f"⚠️ No result or empty result")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print(f"\n🔍 Also testing with different parameter format...")
    
    # Try with parameters as array instead of object
    for node in nodes[:2]:  # Test fewer nodes
        print(f"\n🔍 Testing node with array params: {node}")
        
        payload = {
            "jsonrpc": "2.0",
            "method": "bridge.list_subscribers",
            "params": [{"community": community, "limit": 10}],
            "id": 1
        }
        
        try:
            response = requests.post(
                node,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'result' in data and data['result']:
                    print(f"✅ SUCCESS with array params! Found {len(data['result'])} subscribers")
                    for i, subscriber in enumerate(data['result'][:5]):
                        print(f"  {i+1}. {subscriber}")
                    break
                elif 'error' in data:
                    print(f"❌ API Error: {data['error']}")
                    
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_subscribers_api()
