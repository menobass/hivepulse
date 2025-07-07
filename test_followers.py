#!/usr/bin/env python3
"""Simple test for Hive followers API"""

from lighthive.client import Client
import json

def test_followers():
    """Test different approaches to get followers"""
    print("Testing Hive followers API...")
    
    try:
        # Initialize client with multiple nodes
        hive_nodes = [
            'https://api.hive.blog',
            'https://api.syncad.com', 
            'https://api.deathwing.me',
            'https://hive-api.arcange.eu'
        ]
        
        client = Client(nodes=hive_nodes)
        print(f"✅ Client created with {len(hive_nodes)} nodes")
        
        # Test community account followers
        community = 'hive-115276'
        
        # Method 1: Try get_followers (who follows this account)
        print(f"\n1. Testing get_followers for {community}...")
        try:
            result = client.get_followers(community, '', 'blog', 10)
            print(f"   ✅ Result type: {type(result)}")
            print(f"   ✅ Result length: {len(result) if result else 0}")
            
            if result and len(result) > 0:
                print(f"   ✅ First entry: {result[0]}")
                print(f"   ✅ All entries: {result}")
            else:
                print("   ⚠️ No followers found")
                
        except Exception as e:
            print(f"   ❌ get_followers error: {e}")
        
        # Method 2: Try a test with a known account that has followers
        print(f"\n2. Testing with a known active account...")
        test_account = 'blocktrades'  # Known active account
        try:
            result = client.get_followers(test_account, '', 'blog', 5)
            print(f"   ✅ {test_account} followers result: {len(result) if result else 0}")
            
            if result and len(result) > 0:
                print(f"   ✅ First follower: {result[0]}")
                
        except Exception as e:
            print(f"   ❌ Error with {test_account}: {e}")
        
        print("\n🎉 Followers test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in followers test: {e}")
        return False

if __name__ == "__main__":
    test_followers()
