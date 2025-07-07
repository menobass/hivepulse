"""
Image upload utility for Hive Ecuador Pulse Analytics Bot
Handles chart and image uploads to various hosting services
"""

import os
import requests
import base64
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class ImageUploader:
    """Base class for image uploaders"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        
    def upload(self, image_path: str, filename: Optional[str] = None) -> Optional[str]:
        """Upload image and return URL"""
        raise NotImplementedError("Subclasses must implement upload method")
    
    def upload_bytes(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """Upload image bytes and return URL"""
        raise NotImplementedError("Subclasses must implement upload_bytes method")
    
    def delete(self, url: str) -> bool:
        """Delete uploaded image"""
        return False  # Most services don't support deletion
    
    def get_upload_info(self) -> Dict[str, Any]:
        """Get upload service information"""
        return {
            'service': self.__class__.__name__,
            'enabled': self.enabled,
            'config': self.config
        }

class ImgurUploader(ImageUploader):
    """Imgur image uploader"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.api_base = "https://api.imgur.com/3"
        
    def upload(self, image_path: str, filename: Optional[str] = None) -> Optional[str]:
        """Upload image file to Imgur"""
        try:
            if not self.client_id:
                logger.error("Imgur client ID not configured")
                return None
            
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            with open(image_path, 'rb') as image_file:
                return self.upload_bytes(image_file.read(), filename or os.path.basename(image_path))
                
        except Exception as e:
            logger.error(f"Error uploading image to Imgur: {e}")
            return None
    
    def upload_bytes(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """Upload image bytes to Imgur"""
        try:
            headers = {
                'Authorization': f'Client-ID {self.client_id}'
            }
            
            # Encode image to base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            data = {
                'image': image_b64,
                'type': 'base64',
                'title': filename,
                'description': 'Hive Ecuador Pulse Analytics Chart'
            }
            
            response = requests.post(
                f"{self.api_base}/image",
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    url = result['data']['link']
                    logger.info(f"Image uploaded to Imgur: {url}")
                    return url
                else:
                    logger.error(f"Imgur upload failed: {result.get('data', {}).get('error', 'Unknown error')}")
            else:
                logger.error(f"Imgur API error: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading bytes to Imgur: {e}")
            return None

class PostImagesUploader(ImageUploader):
    """PostImages.org uploader"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = "https://postimages.org/json/rr"
        
    def upload(self, image_path: str, filename: Optional[str] = None) -> Optional[str]:
        """Upload image file to PostImages"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            with open(image_path, 'rb') as image_file:
                files = {'upload': (filename or os.path.basename(image_path), image_file, 'image/png')}
                
                data = {
                    'token': '',  # PostImages doesn't require token for basic uploads
                    'numfiles': '1',
                    'ui': 'json'
                }
                
                response = requests.post(
                    self.api_base,
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('status') == 'OK':
                        url = result.get('url')
                        logger.info(f"Image uploaded to PostImages: {url}")
                        return url
                    else:
                        logger.error(f"PostImages upload failed: {result.get('error', 'Unknown error')}")
                else:
                    logger.error(f"PostImages API error: {response.status_code}")
                
                return None
                
        except Exception as e:
            logger.error(f"Error uploading image to PostImages: {e}")
            return None
    
    def upload_bytes(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """Upload image bytes to PostImages"""
        try:
            files = {'upload': (filename, image_bytes, 'image/png')}
            
            data = {
                'token': '',
                'numfiles': '1',
                'ui': 'json'
            }
            
            response = requests.post(
                self.api_base,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'OK':
                    url = result.get('url')
                    logger.info(f"Image uploaded to PostImages: {url}")
                    return url
                else:
                    logger.error(f"PostImages upload failed: {result.get('error', 'Unknown error')}")
            else:
                logger.error(f"PostImages API error: {response.status_code}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading bytes to PostImages: {e}")
            return None

class LocalFileUploader(ImageUploader):
    """Local file system uploader (for testing/development)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.upload_dir = config.get('upload_dir', 'uploads')
        self.base_url = config.get('base_url', 'http://localhost:8000')
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        
    def upload(self, image_path: str, filename: Optional[str] = None) -> Optional[str]:
        """Copy image to local upload directory"""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            import shutil
            
            # Generate unique filename
            if filename is None:
                filename = os.path.basename(image_path)
            
            # Add timestamp to avoid conflicts
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{name}_{timestamp}{ext}"
            
            dest_path = os.path.join(self.upload_dir, unique_filename)
            shutil.copy2(image_path, dest_path)
            
            # Return URL
            url = urljoin(self.base_url, f"uploads/{unique_filename}")
            logger.info(f"Image copied to local storage: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error uploading image to local storage: {e}")
            return None
    
    def upload_bytes(self, image_bytes: bytes, filename: str) -> Optional[str]:
        """Save image bytes to local upload directory"""
        try:
            # Generate unique filename
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{name}_{timestamp}{ext}"
            
            dest_path = os.path.join(self.upload_dir, unique_filename)
            
            with open(dest_path, 'wb') as f:
                f.write(image_bytes)
            
            # Return URL
            url = urljoin(self.base_url, f"uploads/{unique_filename}")
            logger.info(f"Image saved to local storage: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Error saving image bytes to local storage: {e}")
            return None

class ImageUploadManager:
    """Manages multiple image upload services"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.uploaders = {}
        self.fallback_chain = []
        
        # Initialize uploaders
        self._init_uploaders()
        
    def _init_uploaders(self):
        """Initialize configured uploaders"""
        upload_config = self.config.get('image_upload', {})
        
        # Imgur uploader
        if upload_config.get('imgur', {}).get('enabled', False):
            self.uploaders['imgur'] = ImgurUploader(upload_config['imgur'])
            self.fallback_chain.append('imgur')
        
        # PostImages uploader
        if upload_config.get('postimages', {}).get('enabled', True):
            self.uploaders['postimages'] = PostImagesUploader(upload_config.get('postimages', {}))
            self.fallback_chain.append('postimages')
        
        # Local uploader (always available as fallback)
        self.uploaders['local'] = LocalFileUploader(upload_config.get('local', {}))
        self.fallback_chain.append('local')
        
        logger.info(f"Initialized {len(self.uploaders)} image uploaders: {list(self.uploaders.keys())}")
    
    def upload_image(self, image_path: str, filename: Optional[str] = None,
                    preferred_service: Optional[str] = None) -> Optional[str]:
        """Upload image with fallback support"""
        try:
            # Try preferred service first
            if preferred_service and preferred_service in self.uploaders:
                url = self.uploaders[preferred_service].upload(image_path, filename)
                if url:
                    return url
                logger.warning(f"Preferred service {preferred_service} failed, trying fallbacks")
            
            # Try fallback chain
            for service_name in self.fallback_chain:
                if service_name in self.uploaders:
                    logger.info(f"Trying image upload service: {service_name}")
                    url = self.uploaders[service_name].upload(image_path, filename)
                    if url:
                        return url
                    logger.warning(f"Upload service {service_name} failed")
            
            logger.error("All image upload services failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in image upload manager: {e}")
            return None
    
    def upload_image_bytes(self, image_bytes: bytes, filename: str, 
                          preferred_service: Optional[str] = None) -> Optional[str]:
        """Upload image bytes with fallback support"""
        try:
            # Try preferred service first
            if preferred_service and preferred_service in self.uploaders:
                url = self.uploaders[preferred_service].upload_bytes(image_bytes, filename)
                if url:
                    return url
                logger.warning(f"Preferred service {preferred_service} failed, trying fallbacks")
            
            # Try fallback chain
            for service_name in self.fallback_chain:
                if service_name in self.uploaders:
                    logger.info(f"Trying image upload service: {service_name}")
                    url = self.uploaders[service_name].upload_bytes(image_bytes, filename)
                    if url:
                        return url
                    logger.warning(f"Upload service {service_name} failed")
            
            logger.error("All image upload services failed")
            return None
            
        except Exception as e:
            logger.error(f"Error in image upload manager: {e}")
            return None
    
    def upload_chart_images(self, chart_paths: Dict[str, str]) -> Dict[str, str]:
        """Upload multiple chart images"""
        uploaded_urls = {}
        
        for chart_name, chart_path in chart_paths.items():
            if os.path.exists(chart_path):
                url = self.upload_image(chart_path, f"{chart_name}.png")
                if url:
                    uploaded_urls[chart_name] = url
                else:
                    logger.error(f"Failed to upload chart: {chart_name}")
            else:
                logger.warning(f"Chart file not found: {chart_path}")
        
        return uploaded_urls
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all upload services"""
        status = {}
        
        for service_name, uploader in self.uploaders.items():
            status[service_name] = uploader.get_upload_info()
        
        return status
    
    def test_upload_service(self, service_name: str) -> bool:
        """Test upload service with a small test image"""
        if service_name not in self.uploaders:
            logger.error(f"Upload service {service_name} not found")
            return False
        
        try:
            # Create a small test image (1x1 pixel PNG)
            test_image_bytes = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            )
            
            url = self.uploaders[service_name].upload_bytes(test_image_bytes, "test.png")
            
            if url:
                logger.info(f"Upload service {service_name} test successful: {url}")
                return True
            else:
                logger.error(f"Upload service {service_name} test failed")
                return False
                
        except Exception as e:
            logger.error(f"Error testing upload service {service_name}: {e}")
            return False
    
    def cleanup_local_uploads(self, max_age_days: int = 7) -> int:
        """Cleanup old local uploads"""
        if 'local' not in self.uploaders:
            return 0
        
        try:
            local_uploader = self.uploaders['local']
            upload_dir = local_uploader.upload_dir
            
            if not os.path.exists(upload_dir):
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            deleted_count = 0
            
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                if os.path.isfile(file_path):
                    file_age = os.path.getctime(file_path)
                    if file_age < cutoff_time:
                        os.remove(file_path)
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old local uploads")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up local uploads: {e}")
            return 0

def create_image_upload_manager(config: Dict[str, Any]) -> ImageUploadManager:
    """Factory function to create image upload manager"""
    return ImageUploadManager(config)

def generate_image_hash(image_path: str) -> str:
    """Generate hash for image to avoid duplicate uploads"""
    try:
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error generating image hash: {e}")
        return ""

def optimize_image_for_upload(image_path: str, max_size: int = 1024, 
                             quality: int = 85) -> str:
    """Optimize image for upload (requires PIL)"""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save optimized version
            optimized_path = image_path.replace('.png', '_optimized.jpg')
            img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
            
            logger.info(f"Image optimized: {optimized_path}")
            return optimized_path
            
    except ImportError:
        logger.warning("PIL not available, skipping image optimization")
        return image_path
    except Exception as e:
        logger.error(f"Error optimizing image: {e}")
        return image_path
