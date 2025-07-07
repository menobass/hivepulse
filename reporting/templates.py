"""
Report templates for Hive Ecuador Pulse Analytics Bot
Handles markdown formatting, template rendering, and report structure
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
from analytics.processor import UserMetrics, CommunityMetrics, BusinessMetrics
from analytics.metrics import MetricResult

logger = logging.getLogger(__name__)

class ReportTemplate:
    """Base class for report templates"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.community_name = config.get('community', 'hive-115276')
        self.bot_name = config.get('bot_name', 'Hive Ecuador Pulse')
        self.timezone = config.get('timezone', 'America/Guayaquil')
        
    def render(self, data: Dict[str, Any]) -> str:
        """Render the template with data"""
        raise NotImplementedError("Subclasses must implement render method")
    
    def format_date(self, date: datetime) -> str:
        """Format date for display"""
        return date.strftime("%d de %B de %Y")
    
    def format_time(self, time: datetime) -> str:
        """Format time for display"""
        return time.strftime("%H:%M")
    
    def format_currency(self, amount: float, currency: str = 'HIVE') -> str:
        """Format currency amount"""
        return f"{amount:.3f} {currency}"
    
    def format_percentage(self, value: float) -> str:
        """Format percentage value"""
        return f"{value:.1f}%"
    
    def format_number(self, value: int) -> str:
        """Format large numbers with commas"""
        return f"{value:,}"
    
    def _build_footer(self) -> str:
        """Build report footer"""
        return f"""## 📢 Sobre Este Reporte

Este reporte es generado automáticamente por **{self.bot_name}** para proporcionar insights valiosos sobre la actividad y crecimiento de la comunidad Hive Ecuador.

### 🤝 Únete a la Comunidad

- **Comunidad**: [{self.community_name}](https://peakd.com/c/{self.community_name})
- **Discord**: [Hive Ecuador](https://discord.gg/hive-ecuador)
- **Telegram**: [@hive_ecuador](https://t.me/hive_ecuador)

### 🎯 ¿Cómo Aparecer en el Próximo Reporte?

1. 📝 Publica contenido original en la comunidad
2. 💬 Comenta e interactúa con otros usuarios
3. 🏪 Participa en actividades comerciales
4. 🚀 Invita a más ecuatorianos a unirse

---

*Reporte generado el {self.format_date(datetime.now())} a las {self.format_time(datetime.now())} (Ecuador)*

**#HiveEcuador #CommunityReport #BlockchainAnalytics #Ecuador**
"""
    
    def _build_error_report(self) -> str:
        """Build error report when data is unavailable"""
        return f"""# 🇪🇨 Hive Ecuador Pulse - Error en el Reporte

## ⚠️ Reporte No Disponible

Lo sentimos, no pudimos generar el reporte debido a un problema técnico.

### 🔧 ¿Qué Pasó?

- Error en la recolección de datos
- Problemas de conexión con la API de Hive
- Falla en el procesamiento de información

### 📞 Contacto

Si este problema persiste, por favor contacta al equipo de desarrollo:
- **Usuario**: @menobass
- **Comunidad**: {self.community_name}

---

*Reporte de error generado el {self.format_date(datetime.now())}*
"""

class DailyReportTemplate(ReportTemplate):
    """Template for daily community reports"""
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render daily report"""
        try:
            report_date = data.get('date', datetime.now())
            community_metrics = data.get('community_metrics')
            user_metrics = data.get('user_metrics', [])
            business_metrics = data.get('business_metrics')
            insights = data.get('insights', [])
            chart_urls = data.get('chart_urls', {})
            
            # Build report content
            content = self._build_header(report_date)
            if community_metrics:
                content += self._build_summary(community_metrics)
                content += self._build_community_stats(community_metrics)
            content += self._build_top_users(user_metrics)
            if business_metrics:
                content += self._build_business_activity(business_metrics)
            content += self._build_insights(insights)
            content += self._build_charts_section(chart_urls)
            content += self._build_footer()
            
            return content
            
        except Exception as e:
            logger.error(f"Error rendering daily report: {e}")
            return self._build_error_report()
    
    def _build_header(self, report_date: datetime) -> str:
        """Build report header"""
        return f"""# 🇪🇨 Hive Ecuador Pulse - Reporte Diario

## 📅 {self.format_date(report_date)}

¡Bienvenidos al reporte diario de la comunidad **Hive Ecuador**! 🎉

Aquí encontrarás un resumen completo de la actividad, engagement y crecimiento de nuestra vibrante comunidad ecuatoriana en Hive.

---

"""
    
    def _build_summary(self, community_metrics: CommunityMetrics) -> str:
        """Build executive summary section"""
        if not community_metrics:
            return ""
        
        # Calculate activity rate
        activity_rate = (community_metrics.active_users / community_metrics.total_users * 100) if community_metrics.total_users > 0 else 0
        
        return f"""## 📊 Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| 👥 **Usuarios Totales** | {self.format_number(community_metrics.total_users)} |
| 🔥 **Usuarios Activos** | {self.format_number(community_metrics.active_users)} ({self.format_percentage(activity_rate)}) |
| 📝 **Posts Publicados** | {self.format_number(community_metrics.total_posts)} |
| 💬 **Comentarios** | {self.format_number(community_metrics.total_comments)} |
| 💰 **Recompensas Totales** | {self.format_currency(community_metrics.total_rewards)} |
| 📈 **Tasa de Crecimiento** | {self.format_percentage(community_metrics.growth_rate)} |

---

"""
    
    def _build_community_stats(self, community_metrics: CommunityMetrics) -> str:
        """Build detailed community statistics"""
        if not community_metrics:
            return ""
        
        return f"""## 🏛️ Estadísticas de la Comunidad

### 📈 Métricas Clave

- **Engagement Rate**: {community_metrics.engagement_rate:.2f} comentarios por post
- **Recompensa Promedio**: {self.format_currency(community_metrics.avg_post_reward)} por post
- **Actividad Total**: {self.format_number(community_metrics.total_posts + community_metrics.total_comments)} interacciones

### 🎯 Análisis de Participación

"""
        
        # Add participation analysis
        if community_metrics.total_users > 0:
            activity_rate = (community_metrics.active_users / community_metrics.total_users * 100)
            
            if activity_rate > 60:
                participation_analysis = "🎉 **Excelente participación** - La comunidad está muy activa y comprometida."
            elif activity_rate > 30:
                participation_analysis = "✅ **Buena participación** - La comunidad muestra un nivel saludable de actividad."
            elif activity_rate > 15:
                participation_analysis = "⚠️ **Participación moderada** - Hay oportunidades para aumentar el engagement."
            else:
                participation_analysis = "📢 **Baja participación** - La comunidad necesita estrategias para incrementar la actividad."
            
            return f"""## 🏛️ Estadísticas de la Comunidad

### 📈 Métricas Clave

- **Engagement Rate**: {community_metrics.engagement_rate:.2f} comentarios por post
- **Recompensa Promedio**: {self.format_currency(community_metrics.avg_post_reward)} por post
- **Actividad Total**: {self.format_number(community_metrics.total_posts + community_metrics.total_comments)} interacciones

### 🎯 Análisis de Participación

{participation_analysis}

---

"""
        
        return ""
    
    def _build_top_users(self, user_metrics: List[UserMetrics], limit: int = 10) -> str:
        """Build top users section"""
        if not user_metrics:
            return ""
        
        content = f"""## 🌟 Top Contributors del Día

### 🏆 Usuarios Más Activos

"""
        
        # Sort by total activity
        sorted_users = sorted(user_metrics, key=lambda x: x.posts_count + x.comments_count, reverse=True)
        
        for i, user in enumerate(sorted_users[:limit], 1):
            total_activity = user.posts_count + user.comments_count
            activity_emoji = "🔥" if total_activity > 20 else "⭐" if total_activity > 10 else "👍"
            
            content += f"{i}. {activity_emoji} **@{user.username}** - {total_activity} actividades "
            content += f"({user.posts_count} posts, {user.comments_count} comentarios)\n"
        
        content += "\n### 💰 Top Earners\n\n"
        
        # Sort by rewards
        sorted_by_rewards = sorted(user_metrics, key=lambda x: x.total_rewards, reverse=True)
        
        for i, user in enumerate(sorted_by_rewards[:5], 1):
            if user.total_rewards > 0:
                content += f"{i}. 💎 **@{user.username}** - {self.format_currency(user.total_rewards)}\n"
        
        content += "\n---\n\n"
        
        return content
    
    def _build_business_activity(self, business_metrics: BusinessMetrics) -> str:
        """Build business activity section"""
        if not business_metrics or business_metrics.total_transactions == 0:
            return ""
        
        content = f"""## 💼 Actividad Comercial

### 📊 Transacciones del Día

- **Total de Transacciones**: {self.format_number(business_metrics.total_transactions)}
- **Volumen Total**: {self.format_currency(business_metrics.total_volume)}
- **Transacción Promedio**: {self.format_currency(business_metrics.avg_transaction)}
- **Negocios Activos**: {business_metrics.unique_businesses}

### 🏪 Top Negocios

"""
        
        for i, (business, volume) in enumerate(business_metrics.top_businesses[:5], 1):
            content += f"{i}. 🏪 **@{business}** - {self.format_currency(volume)}\n"
        
        content += "\n---\n\n"
        
        return content
    
    def _build_insights(self, insights: List[str]) -> str:
        """Build insights section"""
        if not insights:
            return ""
        
        content = f"""## 🧠 Insights y Análisis

### 💡 Observaciones Clave

"""
        
        for insight in insights:
            content += f"- {insight}\n"
        
        content += "\n---\n\n"
        
        return content
    
    def _build_charts_section(self, chart_urls: Dict[str, str]) -> str:
        """Build charts section"""
        if not chart_urls:
            return ""
        
        content = f"""## 📈 Visualizaciones

### 🎨 Gráficos y Análisis Visual

"""
        
        chart_descriptions = {
            'activity_chart': 'Actividad diaria de la comunidad',
            'users_chart': 'Distribución de usuarios activos',
            'rewards_chart': 'Distribución de recompensas',
            'business_chart': 'Actividad comercial',
            'trends_chart': 'Tendencias de crecimiento'
        }
        
        for chart_id, url in chart_urls.items():
            description = chart_descriptions.get(chart_id, 'Gráfico de análisis')
            content += f"![{description}]({url})\n\n"
        
        content += "---\n\n"
        
        return content
    
class WeeklyReportTemplate(ReportTemplate):
    """Template for weekly community reports"""
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render weekly report"""
        try:
            week_start = data.get('week_start', datetime.now() - timedelta(days=7))
            week_end = data.get('week_end', datetime.now())
            
            content = f"""# 🇪🇨 Hive Ecuador Pulse - Reporte Semanal

## 📅 {self.format_date(week_start)} - {self.format_date(week_end)}

¡Resumen semanal de la actividad en **Hive Ecuador**! 🎉

### 📊 Resumen de la Semana

Este reporte semanal proporciona una visión más profunda de las tendencias y patrones de nuestra comunidad.

---

"""
            
            # Add weekly-specific sections
            content += self._build_weekly_trends(data)
            content += self._build_weekly_highlights(data)
            content += self._build_weekly_goals(data)
            content += self._build_footer()
            
            return content
            
        except Exception as e:
            logger.error(f"Error rendering weekly report: {e}")
            return self._build_error_report()
    
    def _build_weekly_trends(self, data: Dict[str, Any]) -> str:
        """Build weekly trends section"""
        return """## 📈 Tendencias de la Semana

### 🔥 Actividad Semanal

- Análisis de patrones de actividad
- Identificación de días más activos
- Tendencias de crecimiento

---

"""
    
    def _build_weekly_highlights(self, data: Dict[str, Any]) -> str:
        """Build weekly highlights section"""
        return """## 🌟 Destacados de la Semana

### 🏆 Logros Alcanzados

- Hitos importantes de la comunidad
- Usuarios destacados de la semana
- Contenido más popular

---

"""
    
    def _build_weekly_goals(self, data: Dict[str, Any]) -> str:
        """Build weekly goals section"""
        return """## 🎯 Objetivos para la Próxima Semana

### 📋 Metas Propuestas

- Aumentar la participación en un 10%
- Atraer 5 nuevos usuarios activos
- Incrementar el volumen de transacciones

---

"""

class MonthlyReportTemplate(ReportTemplate):
    """Template for monthly community reports"""
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render monthly report"""
        try:
            month_start = data.get('month_start', datetime.now().replace(day=1))
            month_end = data.get('month_end', datetime.now())
            
            content = f"""# 🇪🇨 Hive Ecuador Pulse - Reporte Mensual

## 📅 {month_start.strftime('%B %Y')}

¡Resumen completo del mes para **Hive Ecuador**! 🎉

### 📊 Análisis Mensual

Este reporte mensual ofrece una perspectiva estratégica del crecimiento y desarrollo de nuestra comunidad.

---

"""
            
            # Add monthly-specific sections
            content += self._build_monthly_summary(data)
            content += self._build_monthly_growth(data)
            content += self._build_monthly_achievements(data)
            content += self._build_footer()
            
            return content
            
        except Exception as e:
            logger.error(f"Error rendering monthly report: {e}")
            return self._build_error_report()
    
    def _build_monthly_summary(self, data: Dict[str, Any]) -> str:
        """Build monthly summary section"""
        return """## 📊 Resumen del Mes

### 📈 Métricas Mensuales

- Crecimiento de usuarios
- Actividad total del mes
- Recompensas generadas

---

"""
    
    def _build_monthly_growth(self, data: Dict[str, Any]) -> str:
        """Build monthly growth section"""
        return """## 🚀 Crecimiento Mensual

### 📈 Análisis de Crecimiento

- Tasa de crecimiento mensual
- Comparación con meses anteriores
- Proyecciones futuras

---

"""
    
    def _build_monthly_achievements(self, data: Dict[str, Any]) -> str:
        """Build monthly achievements section"""
        return """## 🏆 Logros del Mes

### 🎯 Hitos Alcanzados

- Objetivos cumplidos
- Récords establecidos
- Reconocimientos especiales

---

"""

class TemplateManager:
    """Manages report templates"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.templates = {
            'daily': DailyReportTemplate(config),
            'weekly': WeeklyReportTemplate(config),
            'monthly': MonthlyReportTemplate(config)
        }
    
    def get_template(self, template_type: str) -> ReportTemplate:
        """Get template by type"""
        return self.templates.get(template_type, self.templates['daily'])
    
    def render_report(self, template_type: str, data: Dict[str, Any]) -> str:
        """Render report using specified template"""
        template = self.get_template(template_type)
        return template.render(data)
    
    def add_custom_template(self, name: str, template: ReportTemplate) -> None:
        """Add custom template"""
        self.templates[name] = template
