"""
Database Manager Module
Handles SQLite database operations for the Hive Ecuador Pulse bot
"""

import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database operations for the analytics bot"""
    
    def __init__(self, db_path: str = "pulse_analytics.db"):
        """Initialize database manager with database path"""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_database(self):
        """Initialize database with required tables"""
        self.logger.info("Initializing database tables")
        
        try:
            with self.get_connection() as conn:
                # Create only the legacy tables that are still needed
                # (The main tables are created by migrations)
                
                # Create daily activity tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS daily_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        username TEXT NOT NULL,
                        posts_count INTEGER DEFAULT 0,
                        comments_count INTEGER DEFAULT 0,
                        upvotes_given INTEGER DEFAULT 0,
                        upvotes_received INTEGER DEFAULT 0,
                        engagement_score REAL DEFAULT 0.0,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date, username)
                    )
                """)
                
                # Create community aggregate statistics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS community_stats (
                        date TEXT PRIMARY KEY,
                        active_users INTEGER DEFAULT 0,
                        total_posts INTEGER DEFAULT 0,
                        total_comments INTEGER DEFAULT 0,
                        total_upvotes INTEGER DEFAULT 0,
                        new_users INTEGER DEFAULT 0,
                        engagement_rate REAL DEFAULT 0.0,
                        health_index REAL DEFAULT 0.0,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create HBD transaction tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS hbd_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        from_user TEXT NOT NULL,
                        to_user TEXT NOT NULL,
                        amount REAL NOT NULL,
                        memo TEXT,
                        transaction_id TEXT UNIQUE,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create generated reports tracking table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS generated_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        post_author TEXT,
                        post_permlink TEXT,
                        generation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        charts_generated INTEGER DEFAULT 0,
                        success BOOLEAN DEFAULT 0
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_daily_activity_date ON daily_activity(date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_community_stats_date ON community_stats(date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_hbd_transactions_date ON hbd_transactions(date)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def store_community_stats(self, stats: Dict):
        """Store community statistics in database"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO community_stats 
                    (date, active_users, total_posts, total_comments, total_upvotes, 
                     engagement_rate, health_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    stats['date'],
                    stats['active_users'],
                    stats['total_posts'],
                    stats['total_comments'],
                    stats['total_upvotes'],
                    stats['engagement_rate'],
                    stats.get('health_index', 0.0)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing community stats: {str(e)}")
            raise
    
    def store_user_activities(self, user_activities: List, date: str):
        """Store user activities in database"""
        try:
            with self.get_connection() as conn:
                for activity in user_activities:
                    conn.execute("""
                        INSERT OR REPLACE INTO daily_activity 
                        (date, username, posts_count, comments_count, upvotes_given, 
                         upvotes_received, engagement_score)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        date,
                        activity.username,
                        activity.posts_count,
                        activity.comments_count,
                        activity.upvotes_given,
                        activity.upvotes_received,
                        activity.engagement_score
                    ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing user activities: {str(e)}")
            raise
    
    def store_business_data(self, business_data: Dict):
        """Store business transaction data"""
        try:
            with self.get_connection() as conn:
                # Store transactions
                for transaction in business_data.get('transactions', []):
                    conn.execute("""
                        INSERT OR IGNORE INTO hbd_transactions 
                        (date, from_user, to_user, amount, memo, transaction_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        business_data['date'],
                        transaction.get('from', ''),
                        transaction.get('to', ''),
                        float(transaction.get('amount', 0)),
                        transaction.get('memo', ''),
                        transaction.get('transaction_id', '')
                    ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing business data: {str(e)}")
            raise
    
    def get_community_stats(self, date: str) -> Optional[Dict]:
        """Get community statistics for a specific date"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM community_stats WHERE date = ?
                """, (date,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting community stats: {str(e)}")
            return None
    
    def get_tracked_users(self) -> List[str]:
        """Get list of all tracked users"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT username FROM users WHERE is_active = 1
                """)
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting tracked users: {str(e)}")
            return []
    
    def get_registered_businesses(self) -> List[Dict]:
        """Get list of all registered businesses"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT username, display_name, business_description, created_at
                    FROM users 
                    WHERE is_business = 1 AND is_active = 1
                """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting registered businesses: {str(e)}")
            return []
    
    def add_user(self, username: str) -> bool:
        """Add a user to tracking"""
        try:
            with self.get_connection() as conn:
                now = datetime.now().isoformat()
                conn.execute("""
                    INSERT OR REPLACE INTO users 
                    (username, display_name, created_at, updated_at, is_active, is_business)
                    VALUES (?, ?, ?, ?, 1, 0)
                """, (username, username, now, now))
                conn.commit()
                
                self.logger.info(f"Added user {username} to tracking")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding user {username}: {str(e)}")
            return False
    
    def remove_user(self, username: str) -> bool:
        """Remove a user from tracking"""
        try:
            with self.get_connection() as conn:
                now = datetime.now().isoformat()
                conn.execute("""
                    UPDATE users SET is_active = 0, updated_at = ? WHERE username = ?
                """, (now, username))
                conn.commit()
                
                self.logger.info(f"Removed user {username} from tracking")
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing user {username}: {str(e)}")
            return False
    
    def add_business(self, username: str, business_name: str, category: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Add a business to tracking"""
        try:
            with self.get_connection() as conn:
                now = datetime.now().isoformat()
                # First ensure the user exists
                conn.execute("""
                    INSERT OR IGNORE INTO users 
                    (username, display_name, created_at, updated_at, is_active, is_business)
                    VALUES (?, ?, ?, ?, 1, 1)
                """, (username, username, now, now))
                
                # Then update them as a business
                conn.execute("""
                    UPDATE users SET 
                        is_business = 1, 
                        business_description = ?, 
                        updated_at = ?
                    WHERE username = ?
                """, (description or business_name, now, username))
                
                conn.commit()
                
                self.logger.info(f"Added business {business_name} ({username}) to tracking")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding business {business_name}: {str(e)}")
            return False
    
    def remove_business(self, username: str) -> bool:
        """Remove a business from tracking"""
        try:
            with self.get_connection() as conn:
                now = datetime.now().isoformat()
                conn.execute("""
                    UPDATE users SET is_business = 0, updated_at = ? WHERE username = ?
                """, (now, username))
                conn.commit()
                
                self.logger.info(f"Removed business {username} from tracking")
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing business {username}: {str(e)}")
            return False
    
    def record_generated_report(self, date: str, post_author: str, post_permlink: str, 
                               charts_generated: int, success: bool) -> bool:
        """Record a generated report"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO generated_reports 
                    (date, post_author, post_permlink, charts_generated, success)
                    VALUES (?, ?, ?, ?, ?)
                """, (date, post_author, post_permlink, charts_generated, success))
                conn.commit()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error recording generated report: {str(e)}")
            return False
    
    def get_user_activity_history(self, username: str, days: int = 30) -> List[Dict]:
        """Get user activity history for specified number of days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM daily_activity 
                    WHERE username = ? 
                    ORDER BY date DESC 
                    LIMIT ?
                """, (username, days))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting user activity history: {str(e)}")
            return []
    
    def get_community_trends(self, days: int = 30) -> List[Dict]:
        """Get community trend data for specified number of days"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM community_stats 
                    ORDER BY date DESC 
                    LIMIT ?
                """, (days,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting community trends: {str(e)}")
            return []
    
    def get_business_transaction_history(self, username: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get business transaction history"""
        try:
            with self.get_connection() as conn:
                if username:
                    cursor = conn.execute("""
                        SELECT * FROM hbd_transactions 
                        WHERE (from_user = ? OR to_user = ?)
                        ORDER BY date DESC 
                        LIMIT ?
                    """, (username, username, days))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM hbd_transactions 
                        ORDER BY date DESC 
                        LIMIT ?
                    """, (days,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting business transaction history: {str(e)}")
            return []
    
    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """Create a backup of the database"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_pulse_analytics_{timestamp}.db"
            
            # Create backup using sqlite3 backup API
            source = self.get_connection()
            backup = sqlite3.connect(backup_path)
            
            source.backup(backup)
            
            backup.close()
            source.close()
            
            self.logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating database backup: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                stats = {}
                
                # Get table counts
                tables = ['daily_activity', 'community_stats', 'business_registry', 
                         'hbd_transactions', 'user_registry', 'generated_reports']
                
                for table in tables:
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                
                # Get date range
                cursor = conn.execute("SELECT MIN(date), MAX(date) FROM daily_activity")
                date_range = cursor.fetchone()
                stats['activity_date_range'] = {
                    'start': date_range[0] if date_range[0] else None,
                    'end': date_range[1] if date_range[1] else None
                }
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {str(e)}")
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> bool:
        """Clean up old data beyond specified days"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
            
            with self.get_connection() as conn:
                # Clean up old daily activity records
                conn.execute("DELETE FROM daily_activity WHERE date < ?", (cutoff_date,))
                
                # Clean up old community stats
                conn.execute("DELETE FROM community_stats WHERE date < ?", (cutoff_date,))
                
                # Clean up old transactions
                conn.execute("DELETE FROM hbd_transactions WHERE date < ?", (cutoff_date,))
                
                # Clean up old reports
                conn.execute("DELETE FROM generated_reports WHERE date < ?", (cutoff_date,))
                
                conn.commit()
                
                self.logger.info(f"Cleaned up data older than {days_to_keep} days")
                return True
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")
            return False
    
    def add_user_with_join_date(self, username: str, display_name: str, join_date: str, 
                                reputation: int = 0, followers: int = 0, following: int = 0) -> bool:
        """Add a user with detailed information including join date"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO users 
                    (username, display_name, reputation, followers, following, 
                     created_at, updated_at, is_active, is_business, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, ?)
                """, (username, display_name, reputation, followers, following, 
                      join_date, join_date, f"joined:{join_date}"))
                conn.commit()
                
                self.logger.info(f"Added user {username} with join date {join_date}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding user with join date {username}: {str(e)}")
            return False
    
    def deactivate_user_with_leave_date(self, username: str, leave_date: str) -> bool:
        """Deactivate a user and mark their leave date"""
        try:
            with self.get_connection() as conn:
                # Get current tags to preserve join date
                cursor = conn.execute("SELECT tags FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                current_tags = row[0] if row else ""
                
                # Add leave date to tags
                new_tags = f"{current_tags},left:{leave_date}" if current_tags else f"left:{leave_date}"
                
                conn.execute("""
                    UPDATE users SET 
                        is_active = 0, 
                        updated_at = ?, 
                        tags = ?
                    WHERE username = ?
                """, (leave_date, new_tags, username))
                conn.commit()
                
                self.logger.info(f"Deactivated user {username} with leave date {leave_date}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error deactivating user {username}: {str(e)}")
            return False
    
    def reset_user_tracking(self, username: str, new_join_date: str, previous_join_date: Optional[str]) -> bool:
        """Reset user tracking for returning members (starts from zero)"""
        try:
            with self.get_connection() as conn:
                # Archive their previous activity by updating tags
                history_tag = f"previous_member:{previous_join_date}" if previous_join_date else "previous_member"
                new_tags = f"rejoined:{new_join_date},{history_tag}"
                
                # Reset user as if they're new
                conn.execute("""
                    UPDATE users SET 
                        is_active = 1,
                        created_at = ?,
                        updated_at = ?,
                        tags = ?
                    WHERE username = ?
                """, (new_join_date, new_join_date, new_tags, username))
                
                # Clear their activity history (start from zero per requirement)
                conn.execute("DELETE FROM user_activities WHERE username = ?", (username,))
                conn.execute("DELETE FROM daily_activity WHERE username = ?", (username,))
                
                conn.commit()
                
                self.logger.info(f"Reset tracking for returning user {username}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error resetting user tracking {username}: {str(e)}")
            return False
    
    def get_user_history(self, username: str) -> Optional[Dict]:
        """Get user membership history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT username, created_at, updated_at, is_active, tags
                    FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if row:
                    tags = row[4] or ""
                    
                    # Parse tags to find join/leave history
                    has_previous = "left:" in tags or "previous_member:" in tags
                    last_join_date = None
                    
                    if "joined:" in tags:
                        for tag in tags.split(","):
                            if tag.startswith("joined:"):
                                last_join_date = tag.replace("joined:", "")
                                break
                    
                    return {
                        'username': row[0],
                        'has_previous_membership': has_previous,
                        'last_join_date': last_join_date,
                        'is_currently_active': bool(row[3]),
                        'last_updated': row[2]
                    }
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting user history {username}: {str(e)}")
            return None
    
    def log_membership_change(self, change) -> bool:
        """Log membership changes for analytics"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO bot_logs 
                    (level, message, details, module, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    "INFO",
                    f"Membership change: {change.username} {change.action}",
                    f"Previous join: {change.previous_join_date}" if change.previous_join_date else "",
                    "community_manager",
                    change.timestamp
                ))
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error logging membership change: {str(e)}")
            return False
    
    def get_active_users_count(self, days: int = 7) -> int:
        """Get count of users active in the last N days"""
        try:
            with self.get_connection() as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                cursor = conn.execute("""
                    SELECT COUNT(DISTINCT username) 
                    FROM daily_activity 
                    WHERE date >= ? AND (posts_count > 0 OR comments_count > 0 OR upvotes_given > 0)
                """, (cutoff_date,))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            self.logger.error(f"Error getting active users count: {str(e)}")
            return 0
    
    def get_new_members_count(self, days: int = 7) -> int:
        """Get count of new members in the last N days"""
        try:
            with self.get_connection() as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM users 
                    WHERE created_at >= ? AND is_active = 1
                """, (cutoff_date,))
                
                return cursor.fetchone()[0]
                
        except Exception as e:
            self.logger.error(f"Error getting new members count: {str(e)}")
            return 0
    
    def get_top_engaging_users(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get top engaging users based on recent activity"""
        try:
            with self.get_connection() as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                
                cursor = conn.execute("""
                    SELECT 
                        username,
                        SUM(posts_count) as total_posts,
                        SUM(comments_count) as total_comments,
                        SUM(upvotes_given) as total_votes_given,
                        SUM(engagement_score) as total_engagement
                    FROM daily_activity 
                    WHERE date >= ?
                    GROUP BY username
                    ORDER BY total_engagement DESC
                    LIMIT ?
                """, (cutoff_date, limit))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            self.logger.error(f"Error getting top engaging users: {str(e)}")
            return []
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get detailed user information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting user info {username}: {str(e)}")
            return None
    
    def clear_all_users(self) -> bool:
        """Clear all users (use with extreme caution!)"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM users")
                conn.execute("DELETE FROM user_activities") 
                conn.execute("DELETE FROM daily_activity")
                conn.commit()
                
                self.logger.warning("Cleared all users from database")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing all users: {str(e)}")
            return False
