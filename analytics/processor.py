"""
Data processor for Hive Ecuador Pulse Analytics Bot
Handles data analysis, metrics calculation, and trend analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

from utils.helpers import format_hbd_amount, calculate_percentage_change

logger = logging.getLogger(__name__)

@dataclass
class UserMetrics:
    """User activity metrics structure"""
    username: str
    posts_count: int
    comments_count: int
    total_rewards: float
    last_activity: datetime
    reputation: float
    followers: int
    following: int

@dataclass
class CommunityMetrics:
    """Community-wide metrics structure"""
    total_users: int
    active_users: int
    total_posts: int
    total_comments: int
    total_rewards: float
    avg_post_reward: float
    engagement_rate: float
    growth_rate: float

@dataclass
class BusinessMetrics:
    """Business transaction metrics"""
    total_transactions: int
    total_volume: float
    avg_transaction: float
    unique_businesses: int
    top_businesses: List[Tuple[str, float]]

class DataProcessor:
    """Main data processor for analytics calculations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.lookback_days = config.get('tracking', {}).get('lookback_days', 30)
        self.chart_days = config.get('tracking', {}).get('chart_days', 7)
        self.min_activity_threshold = config.get('tracking', {}).get('min_activity_threshold', 1)
        
    def process_user_data(self, raw_data: List[Dict]) -> List[UserMetrics]:
        """Process raw user data into structured metrics"""
        try:
            logger.info(f"Processing {len(raw_data)} user records")
            
            user_metrics = []
            for user_data in raw_data:
                metrics = UserMetrics(
                    username=user_data.get('username', 'unknown'),
                    posts_count=user_data.get('posts', 0),
                    comments_count=user_data.get('comments', 0),
                    total_rewards=float(user_data.get('rewards', 0)),
                    last_activity=datetime.fromisoformat(user_data.get('last_activity', datetime.now().isoformat())),
                    reputation=float(user_data.get('reputation', 0)),
                    followers=user_data.get('followers', 0),
                    following=user_data.get('following', 0)
                )
                user_metrics.append(metrics)
            
            # Sort by total activity (posts + comments)
            user_metrics.sort(key=lambda x: x.posts_count + x.comments_count, reverse=True)
            
            logger.info(f"Processed {len(user_metrics)} user metrics")
            return user_metrics
            
        except Exception as e:
            logger.error(f"Error processing user data: {e}")
            return []
    
    def calculate_community_metrics(self, user_metrics: List[UserMetrics], 
                                  historical_data: Optional[Dict] = None) -> CommunityMetrics:
        """Calculate community-wide metrics"""
        try:
            if not user_metrics:
                return CommunityMetrics(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)
            
            total_users = len(user_metrics)
            active_users = len([u for u in user_metrics if u.posts_count + u.comments_count >= self.min_activity_threshold])
            total_posts = sum(u.posts_count for u in user_metrics)
            total_comments = sum(u.comments_count for u in user_metrics)
            total_rewards = sum(u.total_rewards for u in user_metrics)
            
            avg_post_reward = total_rewards / total_posts if total_posts > 0 else 0.0
            engagement_rate = (total_comments / total_posts) if total_posts > 0 else 0.0
            
            # Calculate growth rate if historical data is available
            growth_rate = 0.0
            if historical_data:
                prev_users = historical_data.get('total_users', total_users)
                if prev_users > 0:
                    growth_rate = ((total_users - prev_users) / prev_users) * 100
            
            return CommunityMetrics(
                total_users=total_users,
                active_users=active_users,
                total_posts=total_posts,
                total_comments=total_comments,
                total_rewards=total_rewards,
                avg_post_reward=avg_post_reward,
                engagement_rate=engagement_rate,
                growth_rate=growth_rate
            )
            
        except Exception as e:
            logger.error(f"Error calculating community metrics: {e}")
            return CommunityMetrics(0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0)
    
    def process_business_data(self, transaction_data: List[Dict]) -> BusinessMetrics:
        """Process business transaction data"""
        try:
            if not transaction_data:
                return BusinessMetrics(0, 0.0, 0.0, 0, [])
            
            total_transactions = len(transaction_data)
            total_volume = sum(float(tx.get('amount', 0)) for tx in transaction_data)
            avg_transaction = total_volume / total_transactions if total_transactions > 0 else 0.0
            
            # Group by business/account
            business_volumes = {}
            for tx in transaction_data:
                business = tx.get('to', 'unknown')
                amount = float(tx.get('amount', 0))
                business_volumes[business] = business_volumes.get(business, 0) + amount
            
            unique_businesses = len(business_volumes)
            top_businesses = sorted(business_volumes.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return BusinessMetrics(
                total_transactions=total_transactions,
                total_volume=total_volume,
                avg_transaction=avg_transaction,
                unique_businesses=unique_businesses,
                top_businesses=top_businesses
            )
            
        except Exception as e:
            logger.error(f"Error processing business data: {e}")
            return BusinessMetrics(0, 0.0, 0.0, 0, [])
    
    def calculate_trends(self, current_metrics: CommunityMetrics, 
                        historical_metrics: List[CommunityMetrics]) -> Dict[str, float]:
        """Calculate trend analysis for key metrics"""
        try:
            trends = {}
            
            if not historical_metrics:
                return {
                    'user_growth': 0.0,
                    'activity_growth': 0.0,
                    'reward_growth': 0.0,
                    'engagement_trend': 0.0
                }
            
            # Get the most recent historical data
            prev_metrics = historical_metrics[-1] if historical_metrics else None
            
            if prev_metrics:
                trends['user_growth'] = calculate_percentage_change(
                    prev_metrics.total_users, current_metrics.total_users
                )
                trends['activity_growth'] = calculate_percentage_change(
                    prev_metrics.total_posts + prev_metrics.total_comments,
                    current_metrics.total_posts + current_metrics.total_comments
                )
                trends['reward_growth'] = calculate_percentage_change(
                    prev_metrics.total_rewards, current_metrics.total_rewards
                )
                trends['engagement_trend'] = calculate_percentage_change(
                    prev_metrics.engagement_rate, current_metrics.engagement_rate
                )
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {}
    
    def get_top_performers(self, user_metrics: List[UserMetrics], 
                          metric: str = 'total_activity', limit: int = 10) -> List[UserMetrics]:
        """Get top performing users by specified metric"""
        try:
            if metric == 'total_activity':
                sorted_users = sorted(user_metrics, 
                                    key=lambda x: x.posts_count + x.comments_count, 
                                    reverse=True)
            elif metric == 'posts':
                sorted_users = sorted(user_metrics, key=lambda x: x.posts_count, reverse=True)
            elif metric == 'comments':
                sorted_users = sorted(user_metrics, key=lambda x: x.comments_count, reverse=True)
            elif metric == 'rewards':
                sorted_users = sorted(user_metrics, key=lambda x: x.total_rewards, reverse=True)
            elif metric == 'reputation':
                sorted_users = sorted(user_metrics, key=lambda x: x.reputation, reverse=True)
            else:
                sorted_users = user_metrics
            
            return sorted_users[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top performers: {e}")
            return []
    
    def analyze_activity_patterns(self, user_metrics: List[UserMetrics]) -> Dict[str, Any]:
        """Analyze user activity patterns"""
        try:
            if not user_metrics:
                return {}
            
            # Calculate activity distribution
            activity_scores = [u.posts_count + u.comments_count for u in user_metrics]
            reward_scores = [u.total_rewards for u in user_metrics]
            
            patterns = {
                'total_users': len(user_metrics),
                'active_users': len([s for s in activity_scores if s > 0]),
                'avg_activity': np.mean(activity_scores) if activity_scores else 0,
                'median_activity': np.median(activity_scores) if activity_scores else 0,
                'avg_rewards': np.mean(reward_scores) if reward_scores else 0,
                'median_rewards': np.median(reward_scores) if reward_scores else 0,
                'activity_distribution': {
                    'low': len([s for s in activity_scores if 0 < s <= 5]),
                    'medium': len([s for s in activity_scores if 5 < s <= 20]),
                    'high': len([s for s in activity_scores if s > 20])
                }
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing activity patterns: {e}")
            return {}
    
    def generate_insights(self, community_metrics: CommunityMetrics, 
                         user_metrics: List[UserMetrics], 
                         trends: Dict[str, float]) -> List[str]:
        """Generate actionable insights from the data"""
        insights = []
        
        try:
            # Community size insights
            if community_metrics.total_users > 0:
                activity_ratio = (community_metrics.active_users / community_metrics.total_users) * 100
                if activity_ratio < 20:
                    insights.append(f"📊 Solo {activity_ratio:.1f}% de usuarios están activos. Considera estrategias de engagement.")
                elif activity_ratio > 60:
                    insights.append(f"🎉 Excelente participación con {activity_ratio:.1f}% de usuarios activos!")
            
            # Engagement insights
            if community_metrics.engagement_rate > 2.0:
                insights.append("💬 Alta interacción: Los usuarios están muy comprometidos con el contenido.")
            elif community_metrics.engagement_rate < 0.5:
                insights.append("📝 Baja interacción: Los posts necesitan más engagement.")
            
            # Growth insights
            if trends.get('user_growth', 0) > 10:
                insights.append(f"📈 Crecimiento acelerado: {trends['user_growth']:.1f}% más usuarios.")
            elif trends.get('user_growth', 0) < -5:
                insights.append(f"⚠️ Decrecimiento: {abs(trends['user_growth']):.1f}% menos usuarios.")
            
            # Reward insights
            if community_metrics.avg_post_reward > 1.0:
                insights.append(f"💰 Excelentes recompensas: Promedio de {community_metrics.avg_post_reward:.2f} HIVE por post.")
            
            # Top performer insights
            if user_metrics:
                top_user = user_metrics[0]
                total_activity = top_user.posts_count + top_user.comments_count
                if total_activity > 50:
                    insights.append(f"🌟 @{top_user.username} lidera con {total_activity} actividades.")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Error generando insights."]
