#!/usr/bin/env python3
"""Debug script to check what community hive-115276 actually is"""

from lighthive.client import Client
import json

def check_community():
    """Check what community hive-115276 actually is"""
    print("Investigating community hive-115276...")
    
    try:
        # Initialize client
        client = Client(nodes=['https://api.hive.blog', 'https://api.syncad.com'])
        print("✅ Client created successfully")
        
        # Get account info for hive-115276
        print("\n1. Getting account info for hive-115276...")
        accounts = client.get_accounts(['hive-115276'])
        if accounts:
            account = accounts[0]
            print(f"✅ Account name: {account['name']}")
            print(f"✅ Created: {account.get('created')}")
            print(f"✅ Post count: {account.get('post_count')}")
            
            # Parse JSON metadata to get community info
            try:
                posting_metadata = json.loads(account.get('posting_json_metadata', '{}'))
                profile = posting_metadata.get('profile', {})
                print(f"✅ Profile name: {profile.get('name', 'N/A')}")
                print(f"✅ About: {profile.get('about', 'N/A')}")
                print(f"✅ Location: {profile.get('location', 'N/A')}")
            except:
                print("❌ Could not parse profile metadata")
        
        # Try to get actual followers
        print("\n2. Getting real followers...")
        try:
            followers = client.get_followers('hive-115276', '', 'blog', 50)
            if followers and isinstance(followers, list):
                print(f"✅ Found {len(followers)} followers:")
                
                for i, follower in enumerate(followers[:20]):  # Show first 20
                    if isinstance(follower, dict):
                        username = follower.get('follower', str(follower))
                    else:
                        username = str(follower)
                    print(f"   {i+1:2d}. @{username}")
                
                if len(followers) > 20:
                    print(f"   ... and {len(followers) - 20} more")
            else:
                print("❌ No followers found or invalid response")
                
        except Exception as e:
            print(f"❌ Error getting followers: {e}")
        
        # Try to get community info if it's a community
        print("\n3. Checking if it's a Hive community...")
        try:
            # This might fail if it's not a community
            community_info = client.call('bridge', 'get_community', ['hive-115276'])
            if community_info and isinstance(community_info, dict):
                print(f"✅ Community title: {community_info.get('title', 'N/A')}")
                print(f"✅ Community about: {community_info.get('about', 'N/A')}")
                print(f"✅ Subscribers: {community_info.get('subscribers', 'N/A')}")
            else:
                print("❌ Not a recognized community or invalid response format")
        except Exception as e:
            print(f"❌ Error getting community info: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_community()
