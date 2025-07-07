"""
Analytics Collector Module
Handles data collection from Hive blockchain APIs
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from utils.hive_api import HiveAPIClient
from database.manager import DatabaseManager


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
    """Collects and processes analytics data from Hive blockchain"""
    
    def __init__(self, hive_api: HiveAPIClient, db_manager: DatabaseManager):
        self.hive_api = hive_api
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.community_tag = "hive-115276"  # Hive Ecuador community
    
    def get_community_activity(self, date: str) -> Dict:
        """Get community activity data for a specific date"""
        self.logger.info(f"Collecting community activity for {date}")
        
        try:
            # Get posts from the community for the date
            posts = self.hive_api.get_posts_by_tag(
                tag=self.community_tag,
                date=date,
                limit=100
            )
            
            # Handle None response
            if posts is None:
                posts = []
            
            # Get comments data
            comments = self.hive_api.get_comments_by_community(
                community=self.community_tag,
                date=date
            )
            
            # Handle None response
            if comments is None:
                comments = []
            
            # Calculate community statistics
            active_users = len(set([post.get('author', '') for post in posts if post.get('author')] + 
                                 [comment.get('author', '') for comment in comments if comment.get('author')]))
            
            total_posts = len(posts)
            total_comments = len(comments)
            total_upvotes = sum(post.get('net_votes', 0) for post in posts if isinstance(post.get('net_votes'), (int, float)))
            
            # Calculate engagement rate
            engagement_rate = (total_comments / total_posts) if total_posts > 0 else 0.0
            
            # Get historical data for trends
            historical_data = self._get_historical_community_data(date, days=7)
            
            community_stats = {
                'date': date,
                'active_users': active_users,
                'total_posts': total_posts,
                'total_comments': total_comments,
                'total_upvotes': total_upvotes,
                'engagement_rate': engagement_rate,
                'historical_data': historical_data,
                'posts_data': posts,
                'comments_data': comments
            }
            
            # Store in database
            self.db_manager.store_community_stats(community_stats)
            
            return community_stats
            
        except Exception as e:
            self.logger.error(f"Error collecting community activity: {str(e)}")
            # Return default structure instead of raising
            return {
                'date': date,
                'active_users': 0,
                'total_posts': 0,
                'total_comments': 0,
                'total_upvotes': 0,
                'engagement_rate': 0.0,
                'historical_data': [],
                'posts_data': [],
                'comments_data': []
            }
    
    def get_user_activities(self, date: str) -> List[UserActivity]:
        """Get user activity data for all tracked users"""
        self.logger.info(f"Collecting user activities for {date}")
        
        try:
            # Get list of tracked users
            tracked_users = self.db_manager.get_tracked_users()
            user_activities = []
            
            for username in tracked_users:
                activity = self.get_user_activity(username, date)
                user_activities.append(activity)
            
            # Store user activities in database
            self.db_manager.store_user_activities(user_activities, date)
            
            return user_activities
            
        except Exception as e:
            self.logger.error(f"Error collecting user activities: {str(e)}")
            raise
    
    def get_user_activity(self, username: str, date: str) -> UserActivity:
        """Get activity data for a specific user"""
        try:
            # Get user's posts for the date
            posts = self.hive_api.get_user_posts(username, date, community=self.community_tag)
            if posts is None:
                posts = []
            
            # Get user's comments for the date
            comments = self.hive_api.get_user_comments(username, date, community=self.community_tag)
            if comments is None:
                comments = []
            
            # Get upvotes given by user
            upvotes_given = self.hive_api.get_user_upvotes_given(username, date)
            if upvotes_given is None:
                upvotes_given = 0
            
            # Get upvotes received by user
            upvotes_received = sum(post.get('net_votes', 0) for post in posts if isinstance(post.get('net_votes'), (int, float)))
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                len(posts), len(comments), upvotes_given, upvotes_received
            )
            
            return UserActivity(
                username=username,
                posts_count=len(posts),
                comments_count=len(comments),
                upvotes_given=upvotes_given,
                upvotes_received=upvotes_received,
                engagement_score=engagement_score
            )
            
        except Exception as e:
            self.logger.error(f"Error getting user activity for {username}: {str(e)}")
            return UserActivity(username=username)
    
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
                # Get HBD transactions for this business
                transactions = self.hive_api.get_hbd_transactions(
                    username=business.get('username', ''),
                    date=date
                )
                
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
