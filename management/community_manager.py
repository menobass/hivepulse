"""
Community Member Manager Module
Handles automatic member discovery and tracking for Hive Ecuador community
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

from utils.hive_api import HiveAPIClient
from database.manager import DatabaseManager


@dataclass
class MembershipChange:
    """Data class for membership changes"""
    username: str
    action: str  # 'joined', 'left', 'rejoined'
    timestamp: str
    previous_join_date: Optional[str] = None


class CommunityMemberManager:
    """Manages community member discovery, tracking, and lifecycle"""
    
    def __init__(self, hive_api: HiveAPIClient, db_manager: DatabaseManager):
        self.hive_api = hive_api
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.community_account = "hive-115276"
    
    def sync_community_members(self) -> Dict[str, int]:
        """Sync community members from Hive blockchain to local database"""
        self.logger.info("Starting community member synchronization")
        
        try:
            # Get current followers from Hive
            current_followers = set(self.hive_api.get_community_followers(self.community_account))
            
            # Get current tracked members from database
            tracked_members = set(self.db_manager.get_tracked_users())
            
            # Find new members (followers not in database)
            new_members = current_followers - tracked_members
            
            # Find members who left (tracked but not following anymore)
            left_members = tracked_members - current_followers
            
            # Process new members
            added_count = 0
            for username in new_members:
                if self._add_new_member(username):
                    added_count += 1
            
            # Process members who left
            removed_count = 0
            for username in left_members:
                if self._handle_member_left(username):
                    removed_count += 1
            
            # Check for returning members (previously tracked, left, now back)
            rejoined_count = 0
            for username in new_members:
                if self._check_and_handle_rejoined_member(username):
                    rejoined_count += 1
            
            self.logger.info(f"Member sync completed: {added_count} new, {removed_count} left, {rejoined_count} rejoined")
            
            return {
                'total_followers': len(current_followers),
                'total_tracked': len(tracked_members) + added_count - removed_count,
                'new_members': added_count,
                'left_members': removed_count,
                'rejoined_members': rejoined_count
            }
            
        except Exception as e:
            self.logger.error(f"Error syncing community members: {str(e)}")
            return {
                'total_followers': 0,
                'total_tracked': 0,
                'new_members': 0,
                'left_members': 0,
                'rejoined_members': 0
            }
    
    def _add_new_member(self, username: str) -> bool:
        """Add a new community member to tracking"""
        try:
            # Get account info from Hive
            account_info = self.hive_api.get_account_info_extended(username)
            
            if account_info:
                now = datetime.now().isoformat()
                
                # Add to database with join date
                success = self.db_manager.add_user_with_join_date(
                    username=username,
                    display_name=account_info.get('display_name', username),
                    join_date=now,
                    reputation=account_info.get('reputation', 0),
                    followers=account_info.get('followers', 0),
                    following=account_info.get('following', 0)
                )
                
                if success:
                    self.logger.info(f"Added new community member: {username}")
                    self._log_membership_change(username, 'joined')
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error adding new member {username}: {str(e)}")
            return False
    
    def _handle_member_left(self, username: str) -> bool:
        """Handle a member who stopped following the community"""
        try:
            now = datetime.now().isoformat()
            
            # Mark as inactive and set leave date
            success = self.db_manager.deactivate_user_with_leave_date(username, now)
            
            if success:
                self.logger.info(f"Member left community: {username}")
                self._log_membership_change(username, 'left')
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling member left {username}: {str(e)}")
            return False
    
    def _check_and_handle_rejoined_member(self, username: str) -> bool:
        """Check if this is a returning member and handle accordingly"""
        try:
            # Check if user existed before (even if inactive)
            user_history = self.db_manager.get_user_history(username)
            
            if user_history and user_history.get('has_previous_membership', False):
                # This is a returning member - reset their tracking per rule #4
                now = datetime.now().isoformat()
                
                success = self.db_manager.reset_user_tracking(
                    username=username,
                    new_join_date=now,
                    previous_join_date=user_history.get('last_join_date')
                )
                
                if success:
                    self.logger.info(f"Returning member reset and reactivated: {username}")
                    self._log_membership_change(username, 'rejoined', user_history.get('last_join_date'))
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking rejoined member {username}: {str(e)}")
            return False
    
    def _log_membership_change(self, username: str, action: str, previous_join_date: Optional[str] = None):
        """Log membership changes for tracking and analytics"""
        try:
            change = MembershipChange(
                username=username,
                action=action,
                timestamp=datetime.now().isoformat(),
                previous_join_date=previous_join_date
            )
            
            # Store in database for future analytics
            self.db_manager.log_membership_change(change)
            
        except Exception as e:
            self.logger.error(f"Error logging membership change: {str(e)}")
    
    def get_membership_stats(self) -> Dict:
        """Get community membership statistics"""
        try:
            total_tracked = len(self.db_manager.get_tracked_users())
            active_today = self.db_manager.get_active_users_count(days=1)
            active_week = self.db_manager.get_active_users_count(days=7)
            new_this_week = self.db_manager.get_new_members_count(days=7)
            
            return {
                'total_members': total_tracked,
                'active_today': active_today,
                'active_this_week': active_week,
                'new_this_week': new_this_week,
                'engagement_rate': (active_week / total_tracked * 100) if total_tracked > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting membership stats: {str(e)}")
            return {
                'total_members': 0,
                'active_today': 0,
                'active_this_week': 0,
                'new_this_week': 0,
                'engagement_rate': 0
            }
    
    def get_top_engaging_members(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """Get top engaging members based on recent activity"""
        try:
            return self.db_manager.get_top_engaging_users(days=days, limit=limit)
            
        except Exception as e:
            self.logger.error(f"Error getting top engaging members: {str(e)}")
            return []
    
    def force_resync_all_members(self) -> bool:
        """Force a complete resync of all community members (use carefully)"""
        self.logger.warning("Starting FORCE RESYNC of all community members")
        
        try:
            # Get all current followers
            current_followers = set(self.hive_api.get_community_followers(self.community_account))
            
            # Clear all current tracking
            self.db_manager.clear_all_users()
            
            # Add all current followers as new members
            added_count = 0
            for username in current_followers:
                if self._add_new_member(username):
                    added_count += 1
            
            self.logger.warning(f"Force resync completed: {added_count} members added")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in force resync: {str(e)}")
            return False
    
    def get_member_join_date(self, username: str) -> Optional[str]:
        """Get the date when a member joined the community"""
        try:
            user_info = self.db_manager.get_user_info(username)
            return user_info.get('join_date') if user_info else None
            
        except Exception as e:
            self.logger.error(f"Error getting join date for {username}: {str(e)}")
            return None
    
    def is_member_active(self, username: str) -> bool:
        """Check if a member is currently active in the community"""
        try:
            user_info = self.db_manager.get_user_info(username)
            return user_info.get('is_active', False) if user_info else False
            
        except Exception as e:
            self.logger.error(f"Error checking if member is active {username}: {str(e)}")
            return False
