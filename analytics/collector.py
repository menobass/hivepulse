"""
Analytics Collector Module
Handles data collection from Hive blockchain APIs with automatic member discovery
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from utils.hive_api import HiveAPIClient
from database.manager import DatabaseManager
from management.community_manager import CommunityMemberManager


@dataclass
class UserActivity:
    """Data class for user activity metrics"""
    username: str
    posts_count: int = 0
    comments_count: int = 0
    upvotes_given: int = 0
    upvotes_received: int = 0
    engagement_score: float = 0.0


@dataclass
class CommunityStats:
    """Data class for community statistics"""
    date: str
    active_users: int = 0
    total_posts: int = 0
    total_comments: int = 0
    total_upvotes: int = 0
    new_users: int = 0
    engagement_rate: float = 0.0


class AnalyticsCollector:
    """Collects and processes analytics data from Hive blockchain with automatic member management"""
    
    def __init__(self, hive_api: HiveAPIClient, db_manager: DatabaseManager):
        self.hive_api = hive_api
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize community member manager
        self.member_manager = CommunityMemberManager(hive_api, db_manager)
        
    def collect_daily_data_with_member_sync(self, date: Optional[str] = None) -> Dict:
        """Complete data collection process with automatic member sync"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.logger.info(f"Starting daily data collection with member sync for {date}")
        
        try:
            # Step 1: Sync community members (auto-discovery)
            sync_results = self.member_manager.sync_community_members()
            self.logger.info(f"Member sync: {sync_results}")
            
            # Step 2: Collect blockchain-wide activity for all members
            user_activities = self.get_user_activities_blockchain_wide(date)
            
            # Step 3: Calculate community stats based on member activity
            community_stats = self.calculate_community_stats_from_members(user_activities, date)
            
            # Step 4: Get historical data for trends (last 7 days)
            historical_data = self.db_manager.get_community_trends(7)
            community_stats['historical_data'] = historical_data
            
            # Step 5: Get membership analytics
            membership_stats = self.member_manager.get_membership_stats()
            
            # Step 6: Identify top performers
            top_performers = self.identify_top_performers(user_activities)
            
            return {
                'date': date,
                'sync_results': sync_results,
                'membership_stats': membership_stats,
                'community_stats': community_stats,
                'user_activities': user_activities,
                'top_performers': top_performers,
                'total_tracked_members': len(user_activities)
            }
            
        except Exception as e:
            self.logger.error(f"Error in daily data collection: {str(e)}")
            raise
    
    def get_user_activities_blockchain_wide(self, date: str) -> List[UserActivity]:
        """Get blockchain-wide activity for all tracked community members"""
        self.logger.info(f"Collecting blockchain-wide activities for {date}")
        
        try:
            # Get all active community members
            tracked_users = self.db_manager.get_tracked_users()
            user_activities = []
            
            for username in tracked_users:
                # Check if member is still active (joined after their activity starts)
                join_date = self.member_manager.get_member_join_date(username)
                should_collect = True
                
                if join_date:
                    # If we have a join date, only collect data for dates after they joined
                    join_datetime = datetime.fromisoformat(join_date.replace('Z', '+00:00'))
                    date_datetime = datetime.strptime(date, '%Y-%m-%d')
                    should_collect = date_datetime >= join_datetime.replace(tzinfo=None)
                    
                    if not should_collect:
                        self.logger.debug(f"Skipping {username} - date {date} is before join date {join_date}")
                else:
                    # If no join date, assume they're a legacy member and collect data
                    self.logger.debug(f"No join date for {username} - treating as legacy member")
                
                if should_collect:
                    activity = self.get_user_blockchain_activity(username, date)
                    user_activities.append(activity)
            
            # Store activities in database
            self.db_manager.store_user_activities(user_activities, date)
            
            return user_activities
            
        except Exception as e:
            self.logger.error(f"Error collecting blockchain-wide activities: {str(e)}")
            return []
    
    def get_user_blockchain_activity(self, username: str, date: str) -> UserActivity:
        """Get user's blockchain-wide activity for a specific date"""
        try:
            # Get comprehensive blockchain activity using the new API method (days=1 for single day)
            raw_activities = self.hive_api.get_user_blockchain_activity(username, days=1)
            
            # Process raw activities to count different types
            posts_count = 0
            comments_count = 0
            upvotes_given = 0
            upvotes_received = 0
            
            for activity in raw_activities:
                activity_type = activity.get('type', '')
                
                if activity_type == 'comment':
                    # Check if it's a post (parent_author is empty) or comment
                    op_data = activity.get('data', {}).get('op', [None, {}])
                    if len(op_data) > 1:
                        comment_data = op_data[1]
                        if comment_data.get('parent_author', '') == '':
                            posts_count += 1
                        else:
                            comments_count += 1
                elif activity_type == 'vote':
                    upvotes_given += 1
            
            # Calculate engagement score
            total_activity = posts_count + comments_count + upvotes_given
            engagement_score = min(total_activity * 0.1, 10.0)  # Cap at 10.0
            
            return UserActivity(
                username=username,
                posts_count=posts_count,
                comments_count=comments_count,
                upvotes_given=upvotes_given,
                upvotes_received=upvotes_received,  # TODO: Need separate API call for this
                engagement_score=engagement_score
            )
            
        except Exception as e:
            self.logger.error(f"Error getting blockchain activity for {username}: {str(e)}")
            return UserActivity(username=username)
    
    def calculate_community_stats_from_members(self, user_activities: List[UserActivity], date: str) -> Dict:
        """Calculate community statistics based on member activities"""
        try:
            # Aggregate member activities
            total_posts = sum(activity.posts_count for activity in user_activities)
            total_comments = sum(activity.comments_count for activity in user_activities)
            total_votes_given = sum(activity.upvotes_given for activity in user_activities)
            total_votes_received = sum(activity.upvotes_received for activity in user_activities)
            
            # Count active users (those with any activity)
            active_users = len([a for a in user_activities if a.posts_count > 0 or a.comments_count > 0 or a.upvotes_given > 0])
            
            # Calculate engagement rate
            total_members = len(user_activities)
            engagement_rate = (active_users / total_members * 100) if total_members > 0 else 0.0
            
            # Get new members today
            new_members_today = self.db_manager.get_new_members_count(days=1)
            
            community_stats = {
                'date': date,
                'total_members': total_members,
                'active_users': active_users,
                'total_posts': total_posts,
                'total_comments': total_comments,
                'total_upvotes': total_votes_given + total_votes_received,  # Fixed: combine for total_upvotes
                'new_members': new_members_today,
                'engagement_rate': engagement_rate,
                'health_index': self._calculate_health_index(user_activities),
                # Additional fields for detailed analytics
                'total_votes_given': total_votes_given,
                'total_votes_received': total_votes_received
            }
            
            # Store community stats
            self.db_manager.store_community_stats(community_stats)
            
            return community_stats
            
        except Exception as e:
            self.logger.error(f"Error calculating community stats: {str(e)}")
            return {
                'date': date,
                'total_members': 0,
                'active_users': 0,
                'total_posts': 0,
                'total_comments': 0,
                'total_votes_given': 0,
                'total_votes_received': 0,
                'new_members': 0,
                'engagement_rate': 0.0,
                'health_index': 0.0
            }
    
    def _calculate_health_index(self, user_activities: List[UserActivity]) -> float:
        """Calculate community health index based on engagement patterns"""
        try:
            if not user_activities:
                return 0.0
            
            total_engagement = sum(activity.engagement_score for activity in user_activities)
            avg_engagement = total_engagement / len(user_activities)
            
            # Factor in distribution of engagement
            high_engagement_users = len([a for a in user_activities if a.engagement_score > avg_engagement])
            engagement_distribution = (high_engagement_users / len(user_activities)) * 100
            
            # Health index combines average engagement and distribution
            health_index = min(100, (avg_engagement / 10) + (engagement_distribution * 0.5))
            
            return round(health_index, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating health index: {str(e)}")
            return 0.0
    
    # Legacy methods - now handled by new blockchain-wide collection system
    # These methods are kept for compatibility but should use the new system
    
    def get_community_activity(self, date: str) -> Dict:
        """Legacy method - use collect_daily_data_with_member_sync instead"""
        self.logger.warning("get_community_activity is deprecated - use collect_daily_data_with_member_sync")
        return self.calculate_community_stats_from_members([], date)
    
    def get_user_activities(self, date: str) -> List[UserActivity]:
        """Legacy method - use get_user_activities_blockchain_wide instead"""
        self.logger.warning("get_user_activities is deprecated - use get_user_activities_blockchain_wide")
        return self.get_user_activities_blockchain_wide(date)
    
    def get_user_activity(self, username: str, date: str) -> UserActivity:
        """Legacy method - use get_user_blockchain_activity instead"""
        self.logger.warning("get_user_activity is deprecated - use get_user_blockchain_activity")
        return self.get_user_blockchain_activity(username, date)
    
    def track_business_activity(self, date: str) -> Dict:
        """Track business activity and HBD transactions"""
        self.logger.info(f"Tracking business activity for {date}")
        
        try:
            # Get registered businesses
            businesses = self.db_manager.get_registered_businesses()
            if businesses is None:
                businesses = []
            
            business_data = {
                'date': date,
                'businesses': businesses,
                'transactions': [],
                'total_hbd_volume': 0.0,
                'top_business': None,
                'active_businesses': 0
            }
            
            total_volume = 0.0
            business_volumes = {}
            
            for business in businesses:
                # TODO: Implement HBD transaction tracking
                # For now, use placeholder data
                transactions = []  # self.hive_api.get_hbd_transactions(business.get('username', ''), date)
                
                if transactions is None:
                    transactions = []
                
                business_volume = sum(float(tx.get('amount', 0)) for tx in transactions if tx.get('amount'))
                business_volumes[business.get('username', '')] = business_volume
                total_volume += business_volume
                
                business_data['transactions'].extend(transactions)
                
                if business_volume > 0:
                    business_data['active_businesses'] += 1
            
            business_data['total_hbd_volume'] = total_volume
            
            # Find top business by volume
            if business_volumes:
                top_business = max(business_volumes.items(), key=lambda x: x[1])
                business_data['top_business'] = {
                    'username': top_business[0],
                    'volume': top_business[1]
                }
            
            # Store business data
            self.db_manager.store_business_data(business_data)
            
            return business_data
            
        except Exception as e:
            self.logger.error(f"Error tracking business activity: {str(e)}")
            # Return default structure instead of raising
            return {
                'date': date,
                'businesses': [],
                'transactions': [],
                'total_hbd_volume': 0.0,
                'top_business': None,
                'active_businesses': 0
            }
    
    def calculate_engagement_metrics(self, data: Dict) -> Dict:
        """Calculate various engagement metrics"""
        self.logger.info("Calculating engagement metrics")
        
        try:
            community_data = data['community']
            user_activities = data['users']
            
            # Calculate community health index
            health_index = self._calculate_community_health_index(community_data)
            
            # Calculate user engagement distribution
            engagement_distribution = self._calculate_engagement_distribution(user_activities)
            
            # Calculate growth metrics
            growth_metrics = self._calculate_growth_metrics(community_data)
            
            return {
                'health_index': health_index,
                'engagement_distribution': engagement_distribution,
                'growth_metrics': growth_metrics,
                'summary': {
                    'total_engagement_score': sum(user.engagement_score for user in user_activities),
                    'average_engagement': sum(user.engagement_score for user in user_activities) / len(user_activities) if user_activities else 0,
                    'highly_engaged_users': len([u for u in user_activities if u.engagement_score > 50])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement metrics: {str(e)}")
            raise
    
    def identify_top_performers(self, user_activities: List[UserActivity]) -> Dict:
        """Identify top performing users in various categories"""
        self.logger.info("Identifying top performers")
        
        try:
            # Sort users by different metrics
            top_poster = max(user_activities, key=lambda u: u.posts_count, default=None)
            top_commenter = max(user_activities, key=lambda u: u.comments_count, default=None)
            top_supporter = max(user_activities, key=lambda u: u.upvotes_given, default=None)
            top_engagement = max(user_activities, key=lambda u: u.engagement_score, default=None)
            
            # Handle ties
            top_posters = [u for u in user_activities if u.posts_count == top_poster.posts_count] if top_poster else []
            top_commenters = [u for u in user_activities if u.comments_count == top_commenter.comments_count] if top_commenter else []
            top_supporters = [u for u in user_activities if u.upvotes_given == top_supporter.upvotes_given] if top_supporter else []
            
            # Find rising star (biggest improvement)
            rising_star = self._find_rising_star(user_activities)
            
            # Find most consistent contributor
            consistent_contributor = self._find_consistent_contributor(user_activities)
            
            return {
                'top_poster': {
                    'users': [u.username for u in top_posters],
                    'count': top_poster.posts_count if top_poster else 0
                },
                'top_commenter': {
                    'users': [u.username for u in top_commenters],
                    'count': top_commenter.comments_count if top_commenter else 0
                },
                'top_supporter': {
                    'users': [u.username for u in top_supporters],
                    'count': top_supporter.upvotes_given if top_supporter else 0
                },
                'top_engagement': {
                    'user': top_engagement.username if top_engagement else None,
                    'score': top_engagement.engagement_score if top_engagement else 0
                },
                'rising_star': rising_star,
                'consistent_contributor': consistent_contributor
            }
            
        except Exception as e:
            self.logger.error(f"Error identifying top performers: {str(e)}")
            raise
    
    def _get_historical_community_data(self, date: str, days: int = 7) -> List[Dict]:
        """Get historical community data for trend analysis"""
        try:
            historical_data = []
            current_date = datetime.strptime(date, '%Y-%m-%d')
            
            for i in range(days):
                check_date = current_date - timedelta(days=i)
                date_str = check_date.strftime('%Y-%m-%d')
                
                # Get data from database if available
                data = self.db_manager.get_community_stats(date_str)
                if data:
                    historical_data.append(data)
                else:
                    # If not in database, use default values to avoid recursion
                    historical_data.append({
                        'date': date_str,
                        'active_users': 0,
                        'total_posts': 0,
                        'total_comments': 0,
                        'total_upvotes': 0,
                        'engagement_rate': 0.0
                    })
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {str(e)}")
            return []
    
    def _calculate_engagement_score(self, posts: int, comments: int, upvotes_given: int, upvotes_received: int) -> float:
        """Calculate engagement score for a user"""
        # Weighted scoring system
        score = (posts * 10) + (comments * 5) + (upvotes_given * 2) + (upvotes_received * 1)
        return round(score, 2)
    
    def _calculate_community_health_index(self, community_data: Dict) -> float:
        """Calculate community health index (0-100)"""
        try:
            # Normalize metrics to 0-100 scale
            active_users_score = min(community_data['active_users'] * 2, 100)
            posts_score = min(community_data['total_posts'] * 5, 100)
            engagement_score = min(community_data['engagement_rate'] * 50, 100)
            
            # Weighted average
            health_index = (active_users_score * 0.4) + (posts_score * 0.3) + (engagement_score * 0.3)
            
            return round(health_index, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating health index: {str(e)}")
            return 0.0
    
    def _calculate_engagement_distribution(self, user_activities: List[UserActivity]) -> Dict:
        """Calculate engagement distribution across users"""
        try:
            if not user_activities:
                return {'low': 0, 'medium': 0, 'high': 0}
            
            scores = [u.engagement_score for u in user_activities]
            
            # Define engagement levels
            low_engagement = len([s for s in scores if s < 20])
            medium_engagement = len([s for s in scores if 20 <= s < 50])
            high_engagement = len([s for s in scores if s >= 50])
            
            return {
                'low': low_engagement,
                'medium': medium_engagement,
                'high': high_engagement
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating engagement distribution: {str(e)}")
            return {'low': 0, 'medium': 0, 'high': 0}
    
    def _calculate_growth_metrics(self, community_data: Dict) -> Dict:
        """Calculate growth metrics compared to previous periods"""
        try:
            historical_data = community_data.get('historical_data', [])
            
            if len(historical_data) < 2:
                return {'daily_growth': 0, 'weekly_growth': 0, 'trend': 'stable'}
            
            # Sort by date
            historical_data.sort(key=lambda x: x['date'])
            
            # Calculate daily growth
            today = historical_data[-1]
            yesterday = historical_data[-2] if len(historical_data) >= 2 else today
            
            daily_growth = ((today['total_posts'] - yesterday['total_posts']) / yesterday['total_posts'] * 100) if yesterday['total_posts'] > 0 else 0
            
            # Calculate weekly growth
            week_ago = historical_data[0] if len(historical_data) >= 7 else yesterday
            weekly_growth = ((today['total_posts'] - week_ago['total_posts']) / week_ago['total_posts'] * 100) if week_ago['total_posts'] > 0 else 0
            
            # Determine trend
            if daily_growth > 5:
                trend = 'growing'
            elif daily_growth < -5:
                trend = 'declining'
            else:
                trend = 'stable'
            
            return {
                'daily_growth': round(daily_growth, 2),
                'weekly_growth': round(weekly_growth, 2),
                'trend': trend
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating growth metrics: {str(e)}")
            return {'daily_growth': 0, 'weekly_growth': 0, 'trend': 'stable'}
    
    def _find_rising_star(self, user_activities: List[UserActivity]) -> Optional[Dict]:
        """Find user with biggest improvement compared to previous week"""
        try:
            # This would require historical user data comparison
            # For now, return user with highest engagement score
            if not user_activities:
                return None
            
            rising_star = max(user_activities, key=lambda u: u.engagement_score)
            
            return {
                'username': rising_star.username,
                'engagement_score': rising_star.engagement_score,
                'improvement': 'N/A'  # Would need historical data
            }
            
        except Exception as e:
            self.logger.error(f"Error finding rising star: {str(e)}")
            return None
    
    def _find_consistent_contributor(self, user_activities: List[UserActivity]) -> Optional[Dict]:
        """Find most consistent contributor"""
        try:
            # This would require historical consistency analysis
            # For now, return user with balanced activity across all metrics
            if not user_activities:
                return None
            
            # Score based on balance across all activities
            balanced_users = []
            for user in user_activities:
                balance_score = min(user.posts_count, user.comments_count, user.upvotes_given // 5)
                balanced_users.append((user, balance_score))
            
            if balanced_users:
                consistent_user = max(balanced_users, key=lambda x: x[1])[0]
                return {
                    'username': consistent_user.username,
                    'consistency_score': balanced_users[0][1],
                    'days_active': 'N/A'  # Would need historical data
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error finding consistent contributor: {str(e)}")
            return None
