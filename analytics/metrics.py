"""
Metrics calculation and aggregation for Hive Ecuador Pulse Analytics Bot
Handles statistical calculations, KPIs, and metric aggregation
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class MetricResult:
    """Result container for metric calculations"""
    value: Union[int, float, str]
    label: str
    unit: str
    trend: Optional[float] = None
    benchmark: Optional[float] = None

class MetricsCalculator:
    """Main metrics calculator for analytics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ecuador_timezone = config.get('timezone', 'America/Guayaquil')
        
    def calculate_growth_rate(self, current: float, previous: float) -> float:
        """Calculate percentage growth rate"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
    
    def calculate_engagement_rate(self, interactions: int, reach: int) -> float:
        """Calculate engagement rate as percentage"""
        if reach == 0:
            return 0.0
        return (interactions / reach) * 100
    
    def calculate_activity_score(self, posts: int, comments: int, 
                               votes: int = 0, weight_posts: float = 1.0,
                               weight_comments: float = 0.5, weight_votes: float = 0.1) -> float:
        """Calculate weighted activity score"""
        return (posts * weight_posts) + (comments * weight_comments) + (votes * weight_votes)
    
    def calculate_reputation_score(self, reputation: int) -> float:
        """Convert Hive reputation to readable score"""
        if reputation == 0:
            return 25.0
        
        # Hive reputation formula conversion
        score = math.log10(abs(reputation)) - 9
        score = max(score * 9 + 25, 0)
        return min(score, 100)
    
    def calculate_user_metrics(self, user_data: Dict[str, Any]) -> Dict[str, MetricResult]:
        """Calculate comprehensive user metrics"""
        try:
            posts = user_data.get('posts', 0)
            comments = user_data.get('comments', 0)
            rewards = float(user_data.get('rewards', 0))
            reputation = user_data.get('reputation', 0)
            followers = user_data.get('followers', 0)
            following = user_data.get('following', 0)
            
            metrics = {
                'activity_score': MetricResult(
                    value=self.calculate_activity_score(posts, comments),
                    label='Puntuación de Actividad',
                    unit='puntos'
                ),
                'total_posts': MetricResult(
                    value=posts,
                    label='Posts Totales',
                    unit='posts'
                ),
                'total_comments': MetricResult(
                    value=comments,
                    label='Comentarios Totales',
                    unit='comentarios'
                ),
                'total_rewards': MetricResult(
                    value=rewards,
                    label='Recompensas Totales',
                    unit='HIVE'
                ),
                'reputation_score': MetricResult(
                    value=self.calculate_reputation_score(reputation),
                    label='Puntuación de Reputación',
                    unit='puntos'
                ),
                'followers_count': MetricResult(
                    value=followers,
                    label='Seguidores',
                    unit='usuarios'
                ),
                'following_count': MetricResult(
                    value=following,
                    label='Siguiendo',
                    unit='usuarios'
                ),
                'avg_reward_per_post': MetricResult(
                    value=rewards / posts if posts > 0 else 0,
                    label='Recompensa Promedio por Post',
                    unit='HIVE'
                )
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating user metrics: {e}")
            return {}
    
    def calculate_community_kpis(self, community_data: Dict[str, Any], 
                               historical_data: Optional[Dict[str, Any]] = None) -> Dict[str, MetricResult]:
        """Calculate key performance indicators for the community"""
        try:
            total_users = community_data.get('total_users', 0)
            active_users = community_data.get('active_users', 0)
            total_posts = community_data.get('total_posts', 0)
            total_comments = community_data.get('total_comments', 0)
            total_rewards = community_data.get('total_rewards', 0)
            
            # Calculate current metrics
            activity_rate = (active_users / total_users * 100) if total_users > 0 else 0
            engagement_rate = (total_comments / total_posts) if total_posts > 0 else 0
            avg_reward_per_post = total_rewards / total_posts if total_posts > 0 else 0
            
            # Calculate trends if historical data available
            user_growth = 0.0
            activity_growth = 0.0
            reward_growth = 0.0
            
            if historical_data:
                prev_users = historical_data.get('total_users', total_users)
                prev_activity = historical_data.get('total_posts', 0) + historical_data.get('total_comments', 0)
                prev_rewards = historical_data.get('total_rewards', total_rewards)
                
                current_activity = total_posts + total_comments
                
                user_growth = self.calculate_growth_rate(total_users, prev_users)
                activity_growth = self.calculate_growth_rate(current_activity, prev_activity)
                reward_growth = self.calculate_growth_rate(total_rewards, prev_rewards)
            
            kpis = {
                'total_users': MetricResult(
                    value=total_users,
                    label='Usuarios Totales',
                    unit='usuarios',
                    trend=user_growth
                ),
                'active_users': MetricResult(
                    value=active_users,
                    label='Usuarios Activos',
                    unit='usuarios'
                ),
                'activity_rate': MetricResult(
                    value=activity_rate,
                    label='Tasa de Actividad',
                    unit='%',
                    benchmark=50.0  # Target 50% activity rate
                ),
                'total_posts': MetricResult(
                    value=total_posts,
                    label='Posts Totales',
                    unit='posts'
                ),
                'total_comments': MetricResult(
                    value=total_comments,
                    label='Comentarios Totales',
                    unit='comentarios'
                ),
                'engagement_rate': MetricResult(
                    value=engagement_rate,
                    label='Tasa de Interacción',
                    unit='comentarios/post',
                    benchmark=2.0  # Target 2 comments per post
                ),
                'total_rewards': MetricResult(
                    value=total_rewards,
                    label='Recompensas Totales',
                    unit='HIVE',
                    trend=reward_growth
                ),
                'avg_reward_per_post': MetricResult(
                    value=avg_reward_per_post,
                    label='Recompensa Promedio por Post',
                    unit='HIVE',
                    benchmark=1.0  # Target 1 HIVE per post
                ),
                'community_growth': MetricResult(
                    value=user_growth,
                    label='Crecimiento de la Comunidad',
                    unit='%',
                    benchmark=5.0  # Target 5% monthly growth
                ),
                'activity_growth': MetricResult(
                    value=activity_growth,
                    label='Crecimiento de Actividad',
                    unit='%',
                    benchmark=10.0  # Target 10% activity growth
                )
            }
            
            return kpis
            
        except Exception as e:
            logger.error(f"Error calculating community KPIs: {e}")
            return {}
    
    def calculate_business_metrics(self, business_data: List[Dict[str, Any]]) -> Dict[str, MetricResult]:
        """Calculate business transaction metrics"""
        try:
            if not business_data:
                return {}
            
            total_transactions = len(business_data)
            total_volume = sum(float(tx.get('amount', 0)) for tx in business_data)
            
            # Calculate transaction size distribution
            amounts = [float(tx.get('amount', 0)) for tx in business_data]
            avg_transaction = sum(amounts) / len(amounts) if amounts else 0
            
            # Sort amounts for percentile calculations
            amounts.sort()
            median_transaction = amounts[len(amounts) // 2] if amounts else 0
            
            # Calculate unique businesses
            unique_businesses = len(set(tx.get('to', '') for tx in business_data if tx.get('to')))
            
            # Calculate transaction frequency (transactions per day)
            if business_data:
                dates = [tx.get('date', '') for tx in business_data if tx.get('date')]
                unique_dates = len(set(dates))
                daily_frequency = total_transactions / unique_dates if unique_dates > 0 else 0
            else:
                daily_frequency = 0
            
            metrics = {
                'total_transactions': MetricResult(
                    value=total_transactions,
                    label='Transacciones Totales',
                    unit='transacciones'
                ),
                'total_volume': MetricResult(
                    value=total_volume,
                    label='Volumen Total',
                    unit='HIVE'
                ),
                'avg_transaction': MetricResult(
                    value=avg_transaction,
                    label='Transacción Promedio',
                    unit='HIVE'
                ),
                'median_transaction': MetricResult(
                    value=median_transaction,
                    label='Transacción Mediana',
                    unit='HIVE'
                ),
                'unique_businesses': MetricResult(
                    value=unique_businesses,
                    label='Negocios Únicos',
                    unit='negocios'
                ),
                'daily_frequency': MetricResult(
                    value=daily_frequency,
                    label='Frecuencia Diaria',
                    unit='transacciones/día'
                ),
                'business_diversity': MetricResult(
                    value=(unique_businesses / total_transactions * 100) if total_transactions > 0 else 0,
                    label='Diversidad de Negocios',
                    unit='%'
                )
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating business metrics: {e}")
            return {}
    
    def calculate_time_based_metrics(self, data: List[Dict[str, Any]], 
                                   date_field: str = 'date') -> Dict[str, MetricResult]:
        """Calculate time-based activity metrics"""
        try:
            if not data:
                return {}
            
            # Extract dates
            dates = []
            for item in data:
                date_str = item.get(date_field, '')
                if date_str:
                    try:
                        dates.append(datetime.fromisoformat(date_str))
                    except:
                        continue
            
            if not dates:
                return {}
            
            # Calculate time spans
            dates.sort()
            date_range = (dates[-1] - dates[0]).days + 1
            
            # Calculate daily averages
            daily_activity = len(data) / date_range if date_range > 0 else 0
            
            # Calculate activity by day of week
            weekday_counts = {}
            for date in dates:
                weekday = date.strftime('%A')
                weekday_counts[weekday] = weekday_counts.get(weekday, 0) + 1
            
            most_active_day = max(weekday_counts.items(), key=lambda x: x[1]) if weekday_counts else ('N/A', 0)
            
            # Calculate recent activity (last 7 days)
            recent_cutoff = datetime.now() - timedelta(days=7)
            recent_activity = len([d for d in dates if d >= recent_cutoff])
            
            metrics = {
                'daily_average': MetricResult(
                    value=daily_activity,
                    label='Promedio Diario',
                    unit='actividades/día'
                ),
                'most_active_day': MetricResult(
                    value=most_active_day[0],
                    label='Día Más Activo',
                    unit='día'
                ),
                'recent_activity': MetricResult(
                    value=recent_activity,
                    label='Actividad Reciente (7 días)',
                    unit='actividades'
                ),
                'activity_span': MetricResult(
                    value=date_range,
                    label='Período de Actividad',
                    unit='días'
                )
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating time-based metrics: {e}")
            return {}
    
    def format_metric_for_display(self, metric: MetricResult) -> str:
        """Format metric for display in reports"""
        try:
            # Format the value based on type and unit
            if isinstance(metric.value, float):
                if metric.unit in ['HIVE', 'HBD']:
                    formatted_value = f"{metric.value:.3f}"
                elif metric.unit == '%':
                    formatted_value = f"{metric.value:.1f}"
                else:
                    formatted_value = f"{metric.value:.2f}"
            else:
                formatted_value = str(metric.value)
            
            display_text = f"{formatted_value} {metric.unit}"
            
            # Add trend indicator if available
            if metric.trend is not None:
                trend_symbol = "📈" if metric.trend > 0 else "📉" if metric.trend < 0 else "➡️"
                display_text += f" {trend_symbol} {metric.trend:+.1f}%"
            
            # Add benchmark comparison if available
            if metric.benchmark is not None and isinstance(metric.value, (int, float)):
                if metric.value >= metric.benchmark:
                    display_text += " ✅"
                else:
                    display_text += " ⚠️"
            
            return display_text
            
        except Exception as e:
            logger.error(f"Error formatting metric: {e}")
            return f"{metric.value} {metric.unit}"
    
    def aggregate_metrics(self, metrics_list: List[Dict[str, MetricResult]]) -> Dict[str, MetricResult]:
        """Aggregate multiple metric dictionaries"""
        try:
            aggregated = {}
            
            for metrics in metrics_list:
                for key, metric in metrics.items():
                    if key not in aggregated:
                        aggregated[key] = metric
                    else:
                        # For numeric values, sum them
                        if isinstance(metric.value, (int, float)) and isinstance(aggregated[key].value, (int, float)):
                            aggregated[key].value += metric.value
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error aggregating metrics: {e}")
            return {}
