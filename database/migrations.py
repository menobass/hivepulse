"""
Database migrations for Hive Ecuador Pulse Analytics Bot
Handles database schema creation and updates
"""

import sqlite3
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Migration:
    """Base migration class"""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Apply migration"""
        raise NotImplementedError("Subclasses must implement up method")
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Rollback migration"""
        raise NotImplementedError("Subclasses must implement down method")

class InitialMigration(Migration):
    """Initial database schema creation"""
    
    def __init__(self):
        super().__init__("001", "Initial database schema")
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Create initial tables"""
        try:
            cursor = connection.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    reputation INTEGER DEFAULT 0,
                    followers INTEGER DEFAULT 0,
                    following INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_business BOOLEAN DEFAULT 0,
                    business_description TEXT,
                    tags TEXT
                )
            """)
            
            # User activities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    username TEXT NOT NULL,
                    date TEXT NOT NULL,
                    posts_count INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0,
                    votes_count INTEGER DEFAULT 0,
                    total_rewards REAL DEFAULT 0.0,
                    avg_reward_per_post REAL DEFAULT 0.0,
                    engagement_score REAL DEFAULT 0.0,
                    activity_score REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Community daily metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS community_daily (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE NOT NULL,
                    total_users INTEGER DEFAULT 0,
                    active_users INTEGER DEFAULT 0,
                    new_users INTEGER DEFAULT 0,
                    total_posts INTEGER DEFAULT 0,
                    total_comments INTEGER DEFAULT 0,
                    total_votes INTEGER DEFAULT 0,
                    total_rewards REAL DEFAULT 0.0,
                    avg_post_reward REAL DEFAULT 0.0,
                    engagement_rate REAL DEFAULT 0.0,
                    activity_rate REAL DEFAULT 0.0,
                    growth_rate REAL DEFAULT 0.0,
                    top_users TEXT,
                    insights TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Business transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_user TEXT NOT NULL,
                    to_user TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'HIVE',
                    transaction_type TEXT DEFAULT 'transfer',
                    memo TEXT,
                    transaction_id TEXT UNIQUE,
                    timestamp TEXT NOT NULL,
                    processed BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    data_json TEXT,
                    post_url TEXT,
                    post_id TEXT,
                    status TEXT DEFAULT 'draft',
                    generated_at TEXT NOT NULL,
                    published_at TEXT,
                    metrics TEXT,
                    charts TEXT
                )
            """)
            
            # Bot configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_by TEXT,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Bot logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bot_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    module TEXT,
                    function TEXT,
                    user TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_business ON users(is_business)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_username ON user_activities(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON user_activities(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_user_date ON user_activities(user_id, date)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_community_date ON community_daily(date)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_to_user ON business_transactions(to_user)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON business_transactions(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_id ON business_transactions(transaction_id)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_generated ON reports(generated_at)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_key ON bot_config(key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_config_category ON bot_config(category)")
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_level ON bot_logs(level)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON bot_logs(timestamp)")
            
            connection.commit()
            logger.info("Initial database schema created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating initial schema: {e}")
            connection.rollback()
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Drop all tables"""
        try:
            cursor = connection.cursor()
            
            tables = [
                'bot_logs', 'bot_config', 'reports', 'business_transactions',
                'community_daily', 'user_activities', 'users'
            ]
            
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            connection.commit()
            logger.info("Database schema dropped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error dropping schema: {e}")
            connection.rollback()
            return False

class AddUserTagsMigration(Migration):
    """Add user tags functionality"""
    
    def __init__(self):
        super().__init__("002", "Add user tags and enhanced business tracking")
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Add user tags column if not exists"""
        try:
            cursor = connection.cursor()
            
            # Check if tags column exists
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'tags' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN tags TEXT")
                logger.info("Added tags column to users table")
            
            # Add business metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_user TEXT NOT NULL,
                    date TEXT NOT NULL,
                    transaction_count INTEGER DEFAULT 0,
                    total_volume REAL DEFAULT 0.0,
                    avg_transaction REAL DEFAULT 0.0,
                    unique_customers INTEGER DEFAULT 0,
                    growth_rate REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_metrics_user ON business_metrics(business_user)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_business_metrics_date ON business_metrics(date)")
            
            connection.commit()
            logger.info("User tags migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in user tags migration: {e}")
            connection.rollback()
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Remove user tags functionality"""
        try:
            cursor = connection.cursor()
            
            # SQLite doesn't support dropping columns, so we'll recreate the table
            cursor.execute("""
                CREATE TABLE users_backup AS 
                SELECT id, username, display_name, reputation, followers, following,
                       created_at, updated_at, is_active, is_business, business_description
                FROM users
            """)
            
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_backup RENAME TO users")
            
            cursor.execute("DROP TABLE IF EXISTS business_metrics")
            
            connection.commit()
            logger.info("User tags migration rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back user tags migration: {e}")
            connection.rollback()
            return False

class AddAnalyticsMigration(Migration):
    """Add advanced analytics tables"""
    
    def __init__(self):
        super().__init__("003", "Add advanced analytics and caching")
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Add analytics tables"""
        try:
            cursor = connection.cursor()
            
            # Analytics cache table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cache_key TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    memory_usage REAL,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # User engagement tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_engagement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    engagement_type TEXT NOT NULL,
                    target_user TEXT,
                    target_post TEXT,
                    weight REAL DEFAULT 1.0,
                    timestamp TEXT NOT NULL
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON analytics_cache(cache_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON analytics_cache(expires_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_operation ON performance_metrics(operation)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_username ON user_engagement(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_type ON user_engagement(engagement_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_engagement_timestamp ON user_engagement(timestamp)")
            
            connection.commit()
            logger.info("Advanced analytics migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in analytics migration: {e}")
            connection.rollback()
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Remove analytics tables"""
        try:
            cursor = connection.cursor()
            
            tables = ['user_engagement', 'performance_metrics', 'analytics_cache']
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            connection.commit()
            logger.info("Analytics migration rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back analytics migration: {e}")
            connection.rollback()
            return False

class AddPatacoinsMigration(Migration):
    """Add patacoins tracking to user activities"""
    
    def __init__(self):
        super().__init__("004", "Add Patacoins tracking system")
    
    def up(self, connection: sqlite3.Connection) -> bool:
        """Add patacoins_earned column to user_activities"""
        try:
            cursor = connection.cursor()
            
            # Check if column already exists
            cursor.execute("PRAGMA table_info(user_activities)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'patacoins_earned' not in columns:
                # Add patacoins_earned column
                cursor.execute("""
                    ALTER TABLE user_activities 
                    ADD COLUMN patacoins_earned REAL DEFAULT 0.0
                """)
                
                logger.info("Added patacoins_earned column to user_activities table")
            else:
                logger.info("patacoins_earned column already exists")
            
            # Create patacoins_balances table for cumulative tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patacoins_balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    total_balance REAL DEFAULT 0.0,
                    total_earned REAL DEFAULT 0.0,
                    total_redeemed REAL DEFAULT 0.0,
                    last_updated TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            connection.commit()
            logger.info("Patacoins migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in patacoins migration: {e}")
            connection.rollback()
            return False
    
    def down(self, connection: sqlite3.Connection) -> bool:
        """Remove patacoins tracking"""
        try:
            cursor = connection.cursor()
            
            # Note: SQLite doesn't support DROP COLUMN, so we'll leave the column
            # but we can drop the patacoins_balances table
            cursor.execute("DROP TABLE IF EXISTS patacoins_balances")
            
            connection.commit()
            logger.info("Patacoins migration rolled back successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back patacoins migration: {e}")
            connection.rollback()
            return False

class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations = [
            InitialMigration(),
            AddUserTagsMigration(),
            AddAnalyticsMigration(),
            AddPatacoinsMigration()
        ]
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_migration_table(self, connection: sqlite3.Connection) -> None:
        """Create migration tracking table"""
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                version TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                applied_at TEXT NOT NULL
            )
        """)
        connection.commit()
    
    def get_applied_migrations(self, connection: sqlite3.Connection) -> List[str]:
        """Get list of applied migrations"""
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT version FROM migrations ORDER BY version")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Migration table doesn't exist yet
            return []
    
    def apply_migration(self, migration: Migration, connection: sqlite3.Connection) -> bool:
        """Apply single migration"""
        try:
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            
            if migration.up(connection):
                # Record migration
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO migrations (version, description, applied_at) VALUES (?, ?, ?)",
                    (migration.version, migration.description, datetime.now().isoformat())
                )
                connection.commit()
                logger.info(f"Migration {migration.version} applied successfully")
                return True
            else:
                logger.error(f"Migration {migration.version} failed")
                return False
                
        except Exception as e:
            logger.error(f"Error applying migration {migration.version}: {e}")
            connection.rollback()
            return False
    
    def rollback_migration(self, migration: Migration, connection: sqlite3.Connection) -> bool:
        """Rollback single migration"""
        try:
            logger.info(f"Rolling back migration {migration.version}: {migration.description}")
            
            if migration.down(connection):
                # Remove migration record
                cursor = connection.cursor()
                cursor.execute("DELETE FROM migrations WHERE version = ?", (migration.version,))
                connection.commit()
                logger.info(f"Migration {migration.version} rolled back successfully")
                return True
            else:
                logger.error(f"Migration {migration.version} rollback failed")
                return False
                
        except Exception as e:
            logger.error(f"Error rolling back migration {migration.version}: {e}")
            connection.rollback()
            return False
    
    def migrate(self) -> bool:
        """Apply all pending migrations"""
        try:
            connection = self.get_connection()
            
            # Create migration table if it doesn't exist
            self.create_migration_table(connection)
            
            # Get applied migrations
            applied = set(self.get_applied_migrations(connection))
            
            # Apply pending migrations
            success = True
            for migration in self.migrations:
                if migration.version not in applied:
                    if not self.apply_migration(migration, connection):
                        success = False
                        break
            
            connection.close()
            return success
            
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            return False
    
    def rollback(self, target_version: Optional[str] = None) -> bool:
        """Rollback to specific migration version"""
        try:
            connection = self.get_connection()
            
            # Get applied migrations
            applied = self.get_applied_migrations(connection)
            
            # Find migrations to rollback
            to_rollback = []
            for migration in reversed(self.migrations):
                if migration.version in applied:
                    to_rollback.append(migration)
                    if target_version and migration.version == target_version:
                        break
            
            # Rollback migrations
            success = True
            for migration in to_rollback:
                if not self.rollback_migration(migration, connection):
                    success = False
                    break
            
            connection.close()
            return success
            
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status"""
        try:
            connection = self.get_connection()
            applied = set(self.get_applied_migrations(connection))
            
            status = {
                'total_migrations': len(self.migrations),
                'applied_migrations': len(applied),
                'pending_migrations': len(self.migrations) - len(applied),
                'migrations': []
            }
            
            for migration in self.migrations:
                status['migrations'].append({
                    'version': migration.version,
                    'description': migration.description,
                    'applied': migration.version in applied
                })
            
            connection.close()
            return status
            
        except Exception as e:
            logger.error(f"Error getting migration status: {e}")
            return {'error': str(e)}
    
    def init_database(self) -> bool:
        """Initialize database with all migrations"""
        try:
            # Create database file if it doesn't exist
            if not os.path.exists(self.db_path):
                open(self.db_path, 'a').close()
            
            # Apply all migrations
            success = self.migrate()
            
            if success:
                logger.info("Database initialized successfully")
                
                # Insert default configuration
                self._insert_default_config()
            else:
                logger.error("Database initialization failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            return False
    
    def _insert_default_config(self) -> None:
        """Insert default configuration values"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            default_configs = [
                ('bot_version', '1.0.0', 'Bot version', 'system'),
                ('last_report_time', '', 'Last report generation time', 'system'),
                ('report_enabled', 'true', 'Enable automatic reports', 'reports'),
                ('report_hour', '21', 'Report generation hour (24h format)', 'reports'),
                ('dry_run', 'false', 'Dry run mode (no posting)', 'system'),
                ('max_users_tracked', '1000', 'Maximum users to track', 'limits'),
                ('data_retention_days', '90', 'Data retention period in days', 'cleanup')
            ]
            
            for key, value, description, category in default_configs:
                cursor.execute(
                    "INSERT OR IGNORE INTO bot_config (key, value, description, category, updated_by, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (key, value, description, category, 'system', datetime.now().isoformat())
                )
            
            connection.commit()
            connection.close()
            
            logger.info("Default configuration inserted successfully")
            
        except Exception as e:
            logger.error(f"Error inserting default configuration: {e}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            import shutil
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Database restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
