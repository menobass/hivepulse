"""
Database models for Hive Ecuador Pulse Analytics Bot
Defines data structures and relationships for analytics storage
"""

import sqlite3
from datetime import datetime
from datetime import date as DateType
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class User:
    """User model for tracked community members"""
    id: Optional[int] = None
    username: str = ""
    display_name: str = ""
    reputation: int = 0
    followers: int = 0
    following: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True
    is_business: bool = False
    business_description: str = ""
    tags: str = ""  # JSON string
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class UserActivity:
    """User activity tracking model"""
    id: Optional[int] = None
    user_id: int = 0
    username: str = ""
    date: Optional[DateType] = None
    posts_count: int = 0
    comments_count: int = 0
    votes_count: int = 0
    total_rewards: float = 0.0
    avg_reward_per_post: float = 0.0
    engagement_score: float = 0.0
    patacoins_earned: float = 0.0
    activity_score: float = 0.0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now().date()
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class CommunityDaily:
    """Daily community metrics model"""
    id: Optional[int] = None
    date: Optional[DateType] = None
    total_users: int = 0
    active_users: int = 0
    new_users: int = 0
    total_posts: int = 0
    total_comments: int = 0
    total_votes: int = 0
    total_rewards: float = 0.0
    avg_post_reward: float = 0.0
    engagement_rate: float = 0.0
    activity_rate: float = 0.0
    growth_rate: float = 0.0
    top_users: str = ""  # JSON string
    insights: str = ""   # JSON string
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now().date()
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class BusinessTransaction:
    """Business transaction tracking model"""
    id: Optional[int] = None
    from_user: str = ""
    to_user: str = ""
    amount: float = 0.0
    currency: str = "HIVE"
    transaction_type: str = "transfer"
    memo: str = ""
    transaction_id: str = ""
    timestamp: Optional[datetime] = None
    processed: bool = False
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Report:
    """Generated report tracking model"""
    id: Optional[int] = None
    report_type: str = "daily"
    title: str = ""
    content: str = ""
    data_json: str = ""  # JSON string of source data
    post_url: str = ""
    post_id: str = ""
    status: str = "draft"  # draft, published, error
    generated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    metrics: str = ""  # JSON string
    charts: str = ""   # JSON string of chart URLs
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()

@dataclass
class BotConfig:
    """Bot configuration model"""
    id: Optional[int] = None
    key: str = ""
    value: str = ""
    description: str = ""
    category: str = "general"
    updated_by: str = ""
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class BotLog:
    """Bot activity logging model"""
    id: Optional[int] = None
    level: str = "info"
    message: str = ""
    details: str = ""
    module: str = ""
    function: str = ""
    user: str = ""
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class DatabaseModel:
    """Base database model with common operations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
    def connect(self):
        """Connect to database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Cursor]:
        """Execute query with parameters"""
        try:
            if not self.connection:
                self.connect()
            
            if not self.connection:
                return None
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
    
    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Fetch single record"""
        try:
            cursor = self.execute(query, params)
            if cursor:
                row = cursor.fetchone()
                return dict(row) if row else None
            return None
            
        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return None
    
    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Fetch multiple records"""
        try:
            cursor = self.execute(query, params)
            if cursor:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            return []
            
        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return []
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insert record and return ID"""
        try:
            # Remove None values and id field
            clean_data = {k: v for k, v in data.items() if v is not None and k != 'id'}
            
            # Convert datetime objects to strings
            for key, value in clean_data.items():
                if isinstance(value, datetime):
                    clean_data[key] = value.isoformat()
            
            columns = ', '.join(clean_data.keys())
            placeholders = ', '.join(['?' for _ in clean_data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = self.execute(query, tuple(clean_data.values()))
            if cursor:
                return cursor.lastrowid
            return None
            
        except Exception as e:
            logger.error(f"Database insert error: {e}")
            return None
    
    def update(self, table: str, data: Dict[str, Any], where_clause: str, where_params: Tuple = ()) -> bool:
        """Update record"""
        try:
            # Remove None values and id field
            clean_data = {k: v for k, v in data.items() if v is not None and k != 'id'}
            
            # Convert datetime objects to strings
            for key, value in clean_data.items():
                if isinstance(value, datetime):
                    clean_data[key] = value.isoformat()
            
            if not clean_data:
                return False
            
            set_clause = ', '.join([f"{k} = ?" for k in clean_data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            
            params = tuple(clean_data.values()) + where_params
            cursor = self.execute(query, params)
            
            return cursor is not None
            
        except Exception as e:
            logger.error(f"Database update error: {e}")
            return False
    
    def delete(self, table: str, where_clause: str, where_params: Tuple = ()) -> bool:
        """Delete record"""
        try:
            query = f"DELETE FROM {table} WHERE {where_clause}"
            cursor = self.execute(query, where_params)
            return cursor is not None
            
        except Exception as e:
            logger.error(f"Database delete error: {e}")
            return False

class UserModel(DatabaseModel):
    """User data model operations"""
    
    def create_user(self, user: User) -> Optional[int]:
        """Create new user"""
        data = asdict(user)
        return self.insert('users', data)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        data = self.fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        if data:
            # Convert string dates back to datetime
            if data['created_at']:
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            if data['updated_at']:
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            return User(**data)
        return None
    
    def get_all_users(self, active_only: bool = True) -> List[User]:
        """Get all users"""
        query = "SELECT * FROM users"
        params = ()
        
        if active_only:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY username"
        
        rows = self.fetch_all(query, params)
        users = []
        
        for row in rows:
            # Convert string dates back to datetime
            if row['created_at']:
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            if row['updated_at']:
                row['updated_at'] = datetime.fromisoformat(row['updated_at'])
            users.append(User(**row))
        
        return users
    
    def update_user(self, user: User) -> bool:
        """Update user"""
        user.updated_at = datetime.now()
        data = asdict(user)
        return self.update('users', data, 'id = ?', (user.id,))
    
    def get_business_users(self) -> List[User]:
        """Get business users"""
        query = "SELECT * FROM users WHERE is_business = 1 AND is_active = 1 ORDER BY username"
        rows = self.fetch_all(query)
        users = []
        
        for row in rows:
            if row['created_at']:
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            if row['updated_at']:
                row['updated_at'] = datetime.fromisoformat(row['updated_at'])
            users.append(User(**row))
        
        return users

class ActivityModel(DatabaseModel):
    """User activity model operations"""
    
    def create_activity(self, activity: UserActivity) -> Optional[int]:
        """Create activity record"""
        data = asdict(activity)
        # Convert date to string
        if data['date']:
            data['date'] = data['date'].isoformat()
        return self.insert('user_activities', data)
    
    def get_user_activity(self, username: str, days: int = 30) -> List[UserActivity]:
        """Get user activity for specified days"""
        query = """
        SELECT * FROM user_activities 
        WHERE username = ? AND date >= date('now', '-{} days')
        ORDER BY date DESC
        """.format(days)
        
        rows = self.fetch_all(query, (username,))
        activities = []
        
        for row in rows:
            if row['date']:
                row['date'] = datetime.fromisoformat(row['date']).date()
            if row['created_at']:
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            activities.append(UserActivity(**row))
        
        return activities
    
    def get_daily_activity(self, date: Optional[DateType] = None) -> List[UserActivity]:
        """Get all user activities for a specific date"""
        if date is None:
            date = datetime.now().date()
        
        query = "SELECT * FROM user_activities WHERE date = ? ORDER BY activity_score DESC"
        rows = self.fetch_all(query, (date.isoformat(),))
        activities = []
        
        for row in rows:
            if row['date']:
                row['date'] = datetime.fromisoformat(row['date']).date()
            if row['created_at']:
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            activities.append(UserActivity(**row))
        
        return activities

class CommunityModel(DatabaseModel):
    """Community metrics model operations"""
    
    def create_daily_metrics(self, metrics: CommunityDaily) -> Optional[int]:
        """Create daily community metrics"""
        data = asdict(metrics)
        if data['date']:
            data['date'] = data['date'].isoformat()
        return self.insert('community_daily', data)
    
    def get_daily_metrics(self, date: Optional[DateType] = None) -> Optional[CommunityDaily]:
        """Get daily metrics for specific date"""
        if date is None:
            date = datetime.now().date()
        
        data = self.fetch_one("SELECT * FROM community_daily WHERE date = ?", (date.isoformat(),))
        if data:
            if data['date']:
                data['date'] = datetime.fromisoformat(data['date']).date()
            if data['created_at']:
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            return CommunityDaily(**data)
        return None
    
    def get_metrics_range(self, start_date: datetime, end_date: datetime) -> List[CommunityDaily]:
        """Get metrics for date range"""
        query = """
        SELECT * FROM community_daily 
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
        """
        
        rows = self.fetch_all(query, (start_date.isoformat(), end_date.isoformat()))
        metrics = []
        
        for row in rows:
            if row['date']:
                row['date'] = datetime.fromisoformat(row['date']).date()
            if row['created_at']:
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            metrics.append(CommunityDaily(**row))
        
        return metrics

class BusinessModel(DatabaseModel):
    """Business transaction model operations"""
    
    def create_transaction(self, transaction: BusinessTransaction) -> Optional[int]:
        """Create business transaction"""
        data = asdict(transaction)
        return self.insert('business_transactions', data)
    
    def get_daily_transactions(self, date: Optional[DateType] = None) -> List[BusinessTransaction]:
        """Get transactions for specific date"""
        if date is None:
            date = datetime.now().date()
        
        query = """
        SELECT * FROM business_transactions 
        WHERE date(timestamp) = ?
        ORDER BY timestamp DESC
        """
        
        rows = self.fetch_all(query, (date.isoformat(),))
        transactions = []
        
        for row in rows:
            if row['timestamp']:
                row['timestamp'] = datetime.fromisoformat(row['timestamp'])
            if row['created_at']:
                row['created_at'] = datetime.fromisoformat(row['created_at'])
            transactions.append(BusinessTransaction(**row))
        
        return transactions
    
    def get_business_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get business activity summary"""
        query = """
        SELECT 
            COUNT(*) as total_transactions,
            SUM(amount) as total_volume,
            AVG(amount) as avg_transaction,
            COUNT(DISTINCT to_user) as unique_businesses
        FROM business_transactions
        WHERE timestamp >= datetime('now', '-{} days')
        """.format(days)
        
        result = self.fetch_one(query)
        return result if result else {}

class ReportModel(DatabaseModel):
    """Report model operations"""
    
    def create_report(self, report: Report) -> Optional[int]:
        """Create report record"""
        data = asdict(report)
        return self.insert('reports', data)
    
    def get_latest_report(self, report_type: str = 'daily') -> Optional[Report]:
        """Get latest report by type"""
        query = """
        SELECT * FROM reports 
        WHERE report_type = ? AND status = 'published'
        ORDER BY generated_at DESC
        LIMIT 1
        """
        
        data = self.fetch_one(query, (report_type,))
        if data:
            if data['generated_at']:
                data['generated_at'] = datetime.fromisoformat(data['generated_at'])
            if data['published_at']:
                data['published_at'] = datetime.fromisoformat(data['published_at'])
            return Report(**data)
        return None
    
    def update_report_status(self, report_id: int, status: str, post_url: Optional[str] = None) -> bool:
        """Update report status"""
        data = {'status': status}
        if post_url:
            data['post_url'] = post_url
        if status == 'published':
            data['published_at'] = datetime.now().isoformat()
        
        return self.update('reports', data, 'id = ?', (report_id,))

class ConfigModel(DatabaseModel):
    """Configuration model operations"""
    
    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value"""
        data = self.fetch_one("SELECT value FROM bot_config WHERE key = ?", (key,))
        return data['value'] if data else None
    
    def set_config(self, key: str, value: str, description: str = "", category: str = "general", updated_by: str = "") -> bool:
        """Set configuration value"""
        # Check if key exists
        existing = self.fetch_one("SELECT id FROM bot_config WHERE key = ?", (key,))
        
        if existing:
            # Update existing
            data = {
                'value': value,
                'description': description,
                'category': category,
                'updated_by': updated_by,
                'updated_at': datetime.now()
            }
            return self.update('bot_config', data, 'key = ?', (key,))
        else:
            # Insert new
            config = BotConfig(
                key=key,
                value=value,
                description=description,
                category=category,
                updated_by=updated_by
            )
            return self.insert('bot_config', asdict(config)) is not None
    
    def get_all_config(self, category: Optional[str] = None) -> Dict[str, str]:
        """Get all configuration values"""
        query = "SELECT key, value FROM bot_config"
        params = ()
        
        if category:
            query += " WHERE category = ?"
            params = (category,)
        
        rows = self.fetch_all(query, params)
        return {row['key']: row['value'] for row in rows}

class LogModel(DatabaseModel):
    """Logging model operations"""
    
    def create_log(self, log: BotLog) -> Optional[int]:
        """Create log entry"""
        data = asdict(log)
        return self.insert('bot_logs', data)
    
    def get_recent_logs(self, limit: int = 100, level: Optional[str] = None) -> List[BotLog]:
        """Get recent logs"""
        query = "SELECT * FROM bot_logs"
        params = ()
        
        if level:
            query += " WHERE level = ?"
            params = (level,)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params = params + (limit,)
        
        rows = self.fetch_all(query, params)
        logs = []
        
        for row in rows:
            if row['timestamp']:
                row['timestamp'] = datetime.fromisoformat(row['timestamp'])
            logs.append(BotLog(**row))
        
        return logs
    
    def cleanup_old_logs(self, days: int = 30) -> bool:
        """Clean up old log entries"""
        query = "DELETE FROM bot_logs WHERE timestamp < datetime('now', '-{} days')".format(days)
        cursor = self.execute(query)
        return cursor is not None
