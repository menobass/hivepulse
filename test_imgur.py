#!/usr/bin/env python3
"""
Test script to verify Imgur image upload functionality
"""

import requests
import os
import sys
import base64

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not available, using system environment only")

def test_imgur_upload():
    """Test uploading an image to Imgur"""
    
    # Check if we have any chart files to test with
    charts_dir = "charts"
    test_image = None
    
    if os.path.exists(charts_dir):
        for file in os.listdir(charts_dir):
            if file.endswith('.png'):
                test_image = os.path.join(charts_dir, file)
                break
    
    if not test_image:
        print("❌ No PNG files found in charts/ directory")
        print("💡 Run --generate-report first to create test images")
        return False
    
    print(f"🧪 Testing Imgur upload with: {test_image}")
    
    # Get Imgur client ID from environment
    client_id = os.getenv('IMGUR_CLIENT_ID')
    if not client_id or client_id == 'your_imgur_client_id_here':
        print("❌ IMGUR_CLIENT_ID not set in environment variables")
        print("💡 Please get a free client ID from: https://api.imgur.com/oauth2/addclient")
        print("📝 Then add it to your .env file: IMGUR_CLIENT_ID=your_actual_client_id")
        return False
    
    try:
        # Use Imgur API v3
        api_base = "https://api.imgur.com/3"
        
        # Read and encode image
        with open(test_image, 'rb') as image_file:
            image_bytes = image_file.read()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Client-ID {client_id}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'image': image_b64,
            'type': 'base64',
            'title': f'Hive Ecuador Pulse Test - {os.path.basename(test_image)}',
            'description': 'Test upload from Hive Ecuador Pulse Bot'
        }
        
        print("📤 Uploading to Imgur...")
        response = requests.post(
            f"{api_base}/image",
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 Response success: {result.get('success')}")
            
            if result.get('success'):
                url = result['data']['link']
                delete_hash = result['data'].get('deletehash', 'N/A')
                print(f"✅ SUCCESS! Image uploaded to: {url}")
                print(f"🗑️ Delete hash: {delete_hash}")
                
                # Test if the URL is accessible (but don't fail on rate limits)
                try:
                    test_response = requests.get(url, timeout=10)
                    if test_response.status_code == 200:
                        print("✅ Image URL is accessible!")
                    elif test_response.status_code == 429:
                        print("⚠️ Rate limited when checking URL (but upload succeeded)")
                    else:
                        print(f"⚠️ Image URL returned status: {test_response.status_code}")
                except:
                    print("⚠️ Could not verify URL accessibility (but upload succeeded)")
                
                return True  # Upload succeeded, that's what matters
                    
            else:
                error_msg = result.get('data', {}).get('error', 'Unknown error')
                print(f"❌ Imgur upload failed: {error_msg}")
                return False
        else:
            print(f"❌ Imgur API error: {response.status_code}")
            print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🖼️ Imgur Upload Test")
    print("=" * 40)
    
    success = test_imgur_upload()
    
    print("=" * 40)
    if success:
        print("🎉 Imgur upload test PASSED!")
        print("💚 Ready to use Imgur for the bot!")
    else:
        print("💥 Imgur upload test FAILED!")
        print("📋 Next steps:")
        print("  1. Get Imgur Client ID: https://api.imgur.com/oauth2/addclient")
        print("  2. Add to .env: IMGUR_CLIENT_ID=your_actual_client_id")
        print("  3. Run this test again")
    
    sys.exit(0 if success else 1)
