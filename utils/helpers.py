"""
Helper Functions Module
General utility functions for the Hive Ecuador Pulse bot
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import pytz
from dotenv import load_dotenv


def load_config(config_path: str = "config/pulse_config.json") -> Dict:
    """Load configuration from JSON file"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Load base configuration
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            # Create default config if file doesn't exist
            config = get_default_config()
            save_config(config, config_path)
        
        # Override with environment variables
        config['HIVE_ACCOUNT_NAME'] = os.getenv('HIVE_ACCOUNT_NAME', config.get('posting_account', ''))
        config['HIVE_POSTING_KEY'] = os.getenv('HIVE_POSTING_KEY', '')
        config['HIVE_ACTIVE_KEY'] = os.getenv('HIVE_ACTIVE_KEY', '')
        config['HIVE_NODE'] = os.getenv('HIVE_NODE', config.get('hive_node', 'https://api.hive.blog'))
        config['IMAGE_UPLOAD_SERVICE'] = os.getenv('IMAGE_UPLOAD_SERVICE', 'https://images.hive.blog')
        config['TIMEZONE'] = os.getenv('TIMEZONE', config.get('timezone', 'America/Guayaquil'))
        config['LOG_LEVEL'] = os.getenv('LOG_LEVEL', 'INFO')
        
        return config
        
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return get_default_config()


def save_config(config: Dict, config_path: str = "config/pulse_config.json"):
    """Save configuration to JSON file"""
    try:
        # Create config directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Remove sensitive keys before saving
        safe_config = {k: v for k, v in config.items() 
                      if not k.startswith('HIVE_') and k not in ['HIVE_POSTING_KEY', 'HIVE_ACTIVE_KEY']}
        
        with open(config_path, 'w') as f:
            json.dump(safe_config, f, indent=2)
            
    except Exception as e:
        print(f"Error saving config: {str(e)}")


def get_default_config() -> Dict:
    """Get default configuration"""
    return {
        "bot_name": "Hive Ecuador Pulse",
        "version": "1.0.0",
        "community": "hive-115276",
        "posting_account": "hiveecuador",
        "report_time": "21:00",
        "timezone": "America/Guayaquil",
        "database_file": "pulse_analytics.db",
        "charts_directory": "charts",
        "assets_directory": "assets",
        "dry_run": True,
        "generate_test_report": False,
        "hive_node": "https://api.hive.blog",
        
        "tracking": {
            "lookback_days": 30,
            "chart_days": 7,
            "min_activity_threshold": 1
        },
        
        "visual_theme": {
            "ecuador_colors": {
                "yellow": "#FFDD00",
                "blue": "#0052CC",
                "red": "#FF0000"
            },
            "chart_style": "professional",
            "font_family": "Arial",
            "logo_path": "assets/hive_ecuador_pulse_logo.png"
        },
        
        "business_tracking": {
            "monitor_transfers": True,
            "min_transfer_amount": 0.001,
            "track_incoming_only": False
        },
        
        "post_template": {
            "header_image": True,
            "include_charts": True,
            "max_images": 10,
            "markdown_formatting": True
        },
        
        "management": {
            "allow_user_commands": True,
            "admin_users": ["menobass"],
            "command_prefix": "!pulse"
        },
        
        "log_level": "INFO"
    }


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/pulse_{datetime.now().strftime('%Y%m%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create logger
    logger = logging.getLogger("HiveEcuadorPulse")
    logger.info("Logging initialized")
    
    return logger


def get_ecuador_timezone() -> pytz.BaseTzInfo:
    """Get Ecuador timezone"""
    return pytz.timezone('America/Guayaquil')


def get_ecuador_time() -> datetime:
    """Get current time in Ecuador timezone"""
    ecuador_tz = get_ecuador_timezone()
    return datetime.now(ecuador_tz)


def format_date_ecuador(date: datetime) -> str:
    """Format date for Ecuador locale"""
    months_es = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    
    ecuador_time = date.astimezone(get_ecuador_timezone())
    month_name = months_es[ecuador_time.month - 1]
    
    return f"{ecuador_time.day} de {month_name} de {ecuador_time.year}"


def format_number_spanish(number: float) -> str:
    """Format numbers for Spanish locale"""
    if number >= 1000000:
        return f"{number/1000000:.1f}M"
    elif number >= 1000:
        return f"{number/1000:.1f}K"
    else:
        return f"{number:.0f}"


def get_growth_emoji(growth_rate: float) -> str:
    """Get emoji based on growth rate"""
    if growth_rate > 10:
        return "🚀"
    elif growth_rate > 5:
        return "📈"
    elif growth_rate > 0:
        return "➡️"
    elif growth_rate > -5:
        return "📉"
    else:
        return "🔻"


def get_engagement_emoji(engagement_rate: float) -> str:
    """Get emoji based on engagement rate"""
    if engagement_rate > 2.0:
        return "🔥"
    elif engagement_rate > 1.5:
        return "💪"
    elif engagement_rate > 1.0:
        return "👍"
    elif engagement_rate > 0.5:
        return "👌"
    else:
        return "😴"


def validate_username(username: str) -> bool:
    """Validate Hive username format"""
    import re
    
    # Hive username rules: 3-16 characters, letters, numbers, hyphens, dots
    pattern = r'^[a-z0-9.-]{3,16}$'
    
    if not re.match(pattern, username):
        return False
    
    # Additional rules
    if username.startswith('.') or username.endswith('.'):
        return False
    
    if username.startswith('-') or username.endswith('-'):
        return False
    
    if '..' in username or '--' in username:
        return False
    
    return True


def sanitize_markdown(text: str) -> str:
    """Sanitize text for markdown formatting"""
    # Escape special markdown characters
    special_chars = ['*', '_', '`', '#', '[', ']', '(', ')', '!', '\\']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def create_progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create ASCII progress bar"""
    if total == 0:
        return "░" * width
    
    progress = current / total
    filled = int(progress * width)
    
    bar = "█" * filled + "░" * (width - filled)
    percentage = int(progress * 100)
    
    return f"{bar} {percentage}%"


def format_hbd_amount(amount: float) -> str:
    """Format HBD amount with currency symbol"""
    return f"${amount:.3f} HBD"


def get_relative_time(date: datetime) -> str:
    """Get relative time string in Spanish"""
    now = datetime.now()
    diff = now - date
    
    if diff.days > 0:
        return f"hace {diff.days} días"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"hace {hours} horas"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"hace {minutes} minutos"
    else:
        return "hace un momento"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def clean_html(text: str) -> str:
    """Remove HTML tags from text"""
    import re
    
    # Remove HTML tags
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def ensure_directory(path: str):
    """Ensure directory exists, create if not"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def is_business_hours() -> bool:
    """Check if it's business hours in Ecuador"""
    ecuador_time = get_ecuador_time()
    hour = ecuador_time.hour
    
    # Business hours: 8 AM to 8 PM Ecuador time
    return 8 <= hour <= 20


def get_next_report_time() -> datetime:
    """Get next report time (9 PM Ecuador time)"""
    ecuador_time = get_ecuador_time()
    
    # Set to 9 PM today
    next_report = ecuador_time.replace(hour=21, minute=0, second=0, microsecond=0)
    
    # If it's already past 9 PM, set to tomorrow
    if ecuador_time.hour >= 21:
        next_report += timedelta(days=1)
    
    return next_report


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds} segundos"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutos"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0 if new_value == 0 else 100
    
    return ((new_value - old_value) / old_value) * 100


def get_color_by_value(value: float, positive_color: str = "green", negative_color: str = "red") -> str:
    """Get color based on positive/negative value"""
    return positive_color if value >= 0 else negative_color


def load_json_file(file_path: str) -> Dict:
    """Load JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        return {}


def save_json_file(data: Dict, file_path: str):
    """Save data to JSON file"""
    try:
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")


def get_system_info() -> Dict:
    """Get system information"""
    import platform
    import psutil
    
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
    }


def check_internet_connection() -> bool:
    """Check if internet connection is available"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def retry_on_failure(func, max_retries: int = 3, delay: int = 1):
    """Retry function on failure"""
    import time
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))  # Exponential backoff


def hash_string(text: str) -> str:
    """Generate hash of string"""
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()


def is_valid_hive_post_permlink(permlink: str) -> bool:
    """Validate Hive post permlink format"""
    import re
    
    # Basic permlink validation
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, permlink)) and len(permlink) <= 256
