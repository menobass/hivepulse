#!/usr/bin/env python3
"""
Test script to verify PostImages.org image upload functionality
"""

import requests
import os
import sys

def test_postimages_upload():
    """Test uploading an image to PostImages.org"""
    
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
    
    print(f"🧪 Testing PostImages upload with: {test_image}")
    
    try:
        # PostImages.org API endpoint
        api_base = "https://postimages.org/json/rr"
        
        with open(test_image, 'rb') as image_file:
            files = {'upload': (os.path.basename(test_image), image_file, 'image/png')}
            
            data = {
                'token': '',  # Not required for basic uploads
                'numfiles': '1',
                'ui': 'json'
            }
            
            print("📤 Uploading to PostImages.org...")
            response = requests.post(
                api_base,
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📝 Response data: {result}")
                
                if result.get('status') == 'OK':
                    url = result.get('url')
                    print(f"✅ SUCCESS! Image uploaded to: {url}")
                    print(f"🔗 Direct link: {url}")
                    
                    # Test if the URL is accessible
                    test_response = requests.get(url, timeout=10)
                    if test_response.status_code == 200:
                        print("✅ Image URL is accessible!")
                        return True
                    else:
                        print(f"⚠️ Image URL returned status: {test_response.status_code}")
                        return False
                        
                else:
                    print(f"❌ PostImages upload failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"❌ PostImages API error: {response.status_code}")
                print(f"Response text: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error during upload test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🖼️ PostImages.org Upload Test")
    print("=" * 40)
    
    success = test_postimages_upload()
    
    print("=" * 40)
    if success:
        print("🎉 PostImages upload test PASSED!")
        print("💚 Ready to use PostImages for the bot!")
    else:
        print("💥 PostImages upload test FAILED!")
        print("💡 We may need to switch to Imgur instead")
    
    sys.exit(0 if success else 1)
