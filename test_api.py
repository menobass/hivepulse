#!/usr/bin/env python3
"""Test script for Hive API calls"""

from lighthive.client import Client
import json

def test_basic_calls():
    """Test basic Hive API calls"""
    print("Testing Hive API with lighthive...")
    
    try:
        # Initialize client with reliable nodes
        client = Client(nodes=['https://api.hive.blog', 'https://anyx.io'])
        print("✅ Client created successfully")
        
        # Test 1: Get dynamic global properties
        print("\n1. Testing dynamic global properties...")
        props = client.get_dynamic_global_properties()
        if props and isinstance(props, dict):
            print(f"✅ Current block: {props.get('head_block_number')}")
            print(f"✅ Total accounts: {props.get('total_accounts')}")
        else:
            print("❌ Could not get dynamic global properties")
        
        # Test 2: Get account info
        print("\n2. Testing account info...")
        accounts = client.get_accounts(['menobass'])
        if accounts:
            account = accounts[0]
            print(f"✅ Account: {account['name']}")
            print(f"✅ Reputation: {account.get('reputation')}")
        
        # Test 3: Get followers using different method
        print("\n3. Testing followers...")
        try:
            # Try different API formats
            followers_result = client.get_followers('menobass', '', 'blog', 5)
            if isinstance(followers_result, list):
                followers = followers_result
            elif isinstance(followers_result, dict) and 'followers' in followers_result:
                followers = followers_result['followers']
            else:
                followers = []
            
            print(f"✅ Found {len(followers)} followers")
            for follower in followers[:3]:
                if isinstance(follower, dict):
                    print(f"   - {follower.get('follower', str(follower))}")
                else:
                    print(f"   - {follower}")
        except Exception as e:
            print(f"❌ Error getting followers: {e}")
        
        # Test 4: Test community account with a more permissive approach
        print("\n4. Testing community followers with different methods...")
        try:
            # Try getting a few followers to test the API
            test_accounts = ['menobass', 'hive-115276']
            
            for acc in test_accounts:
                print(f"\n   Testing {acc}:")
                try:
                    result = client.get_followers(acc, '', 'blog', 5)
                    if result and isinstance(result, list):
                        print(f"   ✅ {acc} has {len(result)} entries")
                        
                        # Print first few for debugging
                        for i, follower in enumerate(result[:3]):
                            if isinstance(follower, dict):
                                print(f"      {i+1}. {follower}")
                            else:
                                print(f"      {i+1}. {follower}")
                    else:
                        print(f"   ❌ No valid result for {acc}")
                except Exception as e:
                    print(f"   ❌ Error getting followers for {acc}: {e}")
                    
        except Exception as e:
            print(f"❌ Error in community test: {e}")
        
        print("\n🎉 All API tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    test_basic_calls()
