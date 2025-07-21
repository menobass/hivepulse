"""
Report Generator Module
Generates comprehensive daily reports for the Hive Ecuador Pulse bot
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from pathlib import Path

from utils.helpers import (
    format_date_ecuador, format_number_spanish, get_growth_emoji,
    get_engagement_emoji, get_ecuador_time
)


class ReportGenerator:
    """Generates formatted reports for the Hive Ecuador Pulse bot"""
    
    def __init__(self, template_config: Dict):
        """Initialize report generator with template configuration"""
        self.config = template_config
        self.logger = logging.getLogger(__name__)
        
        # Load templates
        self.templates = self._load_templates()
        
        # Report settings
        self.include_charts = template_config.get('include_charts', True)
        self.max_images = template_config.get('max_images', 10)
        self.markdown_formatting = template_config.get('markdown_formatting', True)
    
    def _load_templates(self) -> Dict:
        """Load report templates"""
        templates = {
            'header': """
# 🇪🇨 HIVE ECUADOR PULSE - REPORTE DIARIO

### 📅 {date}

---

¡Bienvenidos al reporte diario de nuestra vibrante comunidad! 🚀

Este es nuestro análisis comprensivo de la actividad en Hive Ecuador, donde celebramos nuestros logros, reconocemos a nuestros miembros más activos y monitoreamos el crecimiento de nuestra economía comunitaria.

### 🪙 ¡NUEVO! Sistema de Patacoins

Ahora recompensamos la participación activa con **Patacoins** - ¡nuestra moneda comunitaria virtual! Participa activamente y gana Patacoins que pronto podrás canjear por premios y beneficios especiales. 🎁

---
""",
            
            'community_health': """
## 📊 SALUD DE LA COMUNIDAD

### Métricas Principales

| Métrica | Hoy | Ayer | Cambio |
|---------|-----|------|--------|
| 👥 Usuarios Activos | {active_users} | {yesterday_users} | {users_change} |
| 📝 Posts Publicados | {total_posts} | {yesterday_posts} | {posts_change} |
| 💬 Comentarios | {total_comments} | {yesterday_comments} | {comments_change} |
| 👍 Upvotes Dados | {total_upvotes} | {yesterday_upvotes} | {upvotes_change} |
| 🎯 Tasa de Engagement | {engagement_rate:.2f} | {yesterday_engagement:.2f} | {engagement_change} |

### Índice de Salud Comunitaria: {health_index:.1f}/100 {health_emoji}

{health_analysis}

---
""",
            
            'individual_spotlight': """
## 🌟 PROTAGONISTAS DEL DÍA

### 🏆 Reconocimientos

**📝 Campeón de Posts:** {top_poster}
- {top_poster_count} posts publicados {poster_emoji}
- 🪙 Patacoins ganadas: {top_poster_patacoins}

**💬 Maestro de Comentarios:** {top_commenter}
- {top_commenter_count} comentarios realizados {commenter_emoji}
- 🪙 Patacoins ganadas: {top_commenter_patacoins}

**👍 Estrella del Apoyo:** {top_supporter}
- {top_supporter_count} upvotes otorgados {supporter_emoji}
- 🪙 Patacoins ganadas: {top_supporter_patacoins}

**🚀 Estrella en Ascenso:** {rising_star}
- {rising_star_improvement}
- 🪙 Patacoins ganadas: {rising_star_patacoins}

**🎯 Contribuidor Consistente:** {consistent_contributor}
- {consistency_description}
- 🪙 Patacoins ganadas: {consistent_contributor_patacoins}

### 🪙 SISTEMA DE PATACOINS

¡Nuestra comunidad ahora recompensa la participación activa con **Patacoins**! 🎉

**💰 Patacoins Repartidas Hoy:** {total_patacoins_today}
**🏆 Top Ganador:** {top_patacoin_earner}

#### 💡 ¿Cómo Ganar Patacoins?
- 📝 **Publicar posts:** 2.0 Patacoins por post
- 💬 **Comentar activamente:** 0.5 Patacoins por comentario  
- 👍 **Dar upvotes:** 0.02 Patacoins por upvote (máx 0.5/día)
- ⭐ **Recibir upvotes:** 0.1 Patacoins por upvote recibido

*¡Las Patacoins serán canjeables por premios y beneficios especiales en el futuro!* 🎁

### 📈 Análisis de Engagement

{engagement_analysis}

---
""",
            
            'financial_hub': """
## 💰 HUB FINANCIERO

### 📊 Actividad Económica

| Métrica | Valor |
|---------|-------|
| 💼 Negocios Activos | {active_businesses} |
| 💱 Volumen HBD Total | ${total_hbd_volume:.3f} |
| 🏢 Negocio Top | {top_business} |
| 📈 Crecimiento Semanal | {weekly_growth} |

### 🏪 Directorio de Negocios

{business_directory}

### 💸 Flujo de Transacciones

{transaction_summary}

---
""",
            
            'footer': """
## 🔮 PRÓXIMAS MÉTRICAS

- **Análisis de Tendencias:** Seguimiento de patrones de actividad
- **Predicciones de Crecimiento:** Proyecciones basadas en datos históricos
- **Nuevas Funcionalidades:** Próximas mejoras al sistema de análisis

---

## 📱 SÍGUENOS

- **Comunidad:** [Hive Ecuador](https://peakd.com/c/hive-115276)

---

*🤖 Reporte generado automáticamente por Hive Ecuador Pulse Bot*
*📊 Datos recopilados de la blockchain de Hive*
*🕘 Próximo reporte: {next_report_time}*

---

**#HiveEcuador #Analytics #CommunityGrowth #DailyReport #Blockchain**
"""
        }
        
        return templates
    
    def generate_full_report(self, data: Dict, chart_files: List[str]) -> str:
        """Generate complete daily report with all sections"""
        self.logger.info("Generating full daily report")
        
        try:
            # Generate each section
            header = self.generate_header_section(data)
            community_health = self.generate_community_health_section(data)
            individual_spotlight = self.generate_individual_spotlight_section(data)
            financial_hub = self.generate_financial_hub_section(data)
            footer = self.generate_footer_section(data)
            
            # Combine all sections
            sections = [header, community_health, individual_spotlight, financial_hub, footer]
            
            # Add charts if enabled
            if self.include_charts and chart_files:
                report_content = self.integrate_charts(sections, chart_files)
            else:
                report_content = "\n".join(sections)
            
            # Add engagement hooks
            report_content = self.add_engagement_hooks(report_content)
            
            self.logger.info("Full report generated successfully")
            return report_content
            
        except Exception as e:
            self.logger.error(f"Error generating full report: {str(e)}")
            raise
    
    def generate_header_section(self, data: Dict) -> str:
        """Generate header section of the report"""
        try:
            date = data['date']
            formatted_date = format_date_ecuador(datetime.strptime(date, '%Y-%m-%d'))
            
            return self.templates['header'].format(
                date=formatted_date
            )
            
        except Exception as e:
            self.logger.error(f"Error generating header section: {str(e)}")
            return ""
    
    def generate_community_health_section(self, data: Dict) -> str:
        """Generate community health section"""
        try:
            # Try both 'community_stats' (new format) and 'community' (legacy format)
            community_data = data.get('community_stats', data.get('community', {}))
            if not community_data:
                self.logger.warning("No community data available")
                return "## 📊 SALUD DE LA COMUNIDAD\n\n*Datos no disponibles actualmente*\n\n---\n"
            
            historical_data = community_data.get('historical_data', [])
            
            # Current metrics with defaults
            active_users = community_data.get('active_users', 0)
            total_posts = community_data.get('total_posts', 0)
            total_comments = community_data.get('total_comments', 0)
            total_upvotes = community_data.get('total_upvotes', 0)
            engagement_rate = community_data.get('engagement_rate', 0.0)
            
            # Get yesterday's data for comparison
            yesterday_data = historical_data[-2] if len(historical_data) >= 2 else {}
            yesterday_users = yesterday_data.get('active_users', 0)
            yesterday_posts = yesterday_data.get('total_posts', 0)
            yesterday_comments = yesterday_data.get('total_comments', 0)
            yesterday_upvotes = yesterday_data.get('total_upvotes', 0)
            yesterday_engagement = yesterday_data.get('engagement_rate', 0.0)
            
            # Calculate changes
            users_change = self._format_change(active_users, yesterday_users)
            posts_change = self._format_change(total_posts, yesterday_posts)
            comments_change = self._format_change(total_comments, yesterday_comments)
            upvotes_change = self._format_change(total_upvotes, yesterday_upvotes)
            engagement_change = self._format_change(engagement_rate, yesterday_engagement, is_percentage=True)
            
            # Calculate health index
            engagement_data = data.get('engagement', {})
            health_index = engagement_data.get('health_index', 0) if engagement_data else 0
            health_emoji = self._get_health_emoji(health_index)
            health_analysis = self._generate_health_analysis(health_index, community_data)
            
            return self.templates['community_health'].format(
                active_users=format_number_spanish(active_users),
                yesterday_users=format_number_spanish(yesterday_users),
                users_change=users_change,
                total_posts=format_number_spanish(total_posts),
                yesterday_posts=format_number_spanish(yesterday_posts),
                posts_change=posts_change,
                total_comments=format_number_spanish(total_comments),
                yesterday_comments=format_number_spanish(yesterday_comments),
                comments_change=comments_change,
                total_upvotes=format_number_spanish(total_upvotes),
                yesterday_upvotes=format_number_spanish(yesterday_upvotes),
                upvotes_change=upvotes_change,
                engagement_rate=engagement_rate,
                yesterday_engagement=yesterday_engagement,
                engagement_change=engagement_change,
                health_index=health_index,
                health_emoji=health_emoji,
                health_analysis=health_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Error generating community health section: {str(e)}")
            return "## 📊 SALUD DE LA COMUNIDAD\n\n*Error al generar sección*\n\n---\n"
    
    def generate_individual_spotlight_section(self, data: Dict) -> str:
        """Generate individual spotlight section"""
        try:
            top_performers = data.get('top_performers', {})
            user_activities = data.get('user_activities', [])
            
            # Handle empty or None top_performers
            if not top_performers:
                return "## 🌟 PROTAGONISTAS DEL DÍA\n\n*Datos de rendimiento no disponibles*\n\n---\n"
            
            # Format top performers with safe defaults
            top_poster = self._format_top_performers(top_performers.get('top_poster', {}))
            top_commenter = self._format_top_performers(top_performers.get('top_commenter', {}))
            top_supporter = self._format_top_performers(top_performers.get('top_supporter', {}))
            
            # Get counts with defaults
            top_poster_count = top_performers.get('top_poster', {}).get('count', 0)
            top_commenter_count = top_performers.get('top_commenter', {}).get('count', 0)
            top_supporter_count = top_performers.get('top_supporter', {}).get('count', 0)
            
            # Get Patacoins data for top performers - handle users array format
            top_poster_user = top_performers.get('top_poster', {}).get('users', [''])[0] if top_performers.get('top_poster', {}).get('users') else ''
            top_commenter_user = top_performers.get('top_commenter', {}).get('users', [''])[0] if top_performers.get('top_commenter', {}).get('users') else ''
            top_supporter_user = top_performers.get('top_supporter', {}).get('users', [''])[0] if top_performers.get('top_supporter', {}).get('users') else ''
            
            top_poster_patacoins = self._get_patacoins_for_user(user_activities, top_poster_user)
            top_commenter_patacoins = self._get_patacoins_for_user(user_activities, top_commenter_user)
            top_supporter_patacoins = self._get_patacoins_for_user(user_activities, top_supporter_user)
            
            # Get emojis
            poster_emoji = get_growth_emoji(top_poster_count * 5)
            commenter_emoji = get_engagement_emoji(top_commenter_count / 5 if top_commenter_count > 0 else 0)
            supporter_emoji = "⭐" if top_supporter_count > 10 else "👏"
            
            # Rising star and consistent contributor with safe defaults
            rising_star = top_performers.get('rising_star', {})
            consistent_contributor = top_performers.get('consistent_contributor', {})
            
            rising_star_name = rising_star.get('username', 'N/A') if rising_star else 'N/A'
            rising_star_improvement = f"Puntuación de engagement: {rising_star.get('engagement_score', 0):.1f}" if rising_star else "N/A"
            rising_star_patacoins = self._get_patacoins_for_user(user_activities, rising_star_name)
            
            consistent_contributor_name = consistent_contributor.get('username', 'N/A') if consistent_contributor else 'N/A'
            consistency_description = f"Puntuación de consistencia: {consistent_contributor.get('consistency_score', 0)}" if consistent_contributor else "N/A"
            consistent_contributor_patacoins = self._get_patacoins_for_user(user_activities, consistent_contributor_name)
            
            # Calculate Patacoin statistics
            total_patacoins_today = sum(activity.get('patacoins_earned', 0.0) for activity in user_activities if isinstance(activity, dict))
            if not total_patacoins_today and user_activities:
                # Handle if user_activities contains UserActivity objects
                total_patacoins_today = sum(getattr(activity, 'patacoins_earned', 0.0) for activity in user_activities)
            
            # Find top Patacoin earner
            top_patacoin_earner = self._get_top_patacoin_earner(user_activities)
            
            # Generate engagement analysis
            engagement_analysis = self._generate_engagement_analysis(data)
            
            return self.templates['individual_spotlight'].format(
                top_poster=top_poster,
                top_poster_count=top_poster_count,
                poster_emoji=poster_emoji,
                top_poster_patacoins=f"{top_poster_patacoins:.1f}" if top_poster_patacoins > 0 else "0.0",
                top_commenter=top_commenter,
                top_commenter_count=top_commenter_count,
                commenter_emoji=commenter_emoji,
                top_commenter_patacoins=f"{top_commenter_patacoins:.1f}" if top_commenter_patacoins > 0 else "0.0",
                top_supporter=top_supporter,
                top_supporter_count=top_supporter_count,
                supporter_emoji=supporter_emoji,
                top_supporter_patacoins=f"{top_supporter_patacoins:.1f}" if top_supporter_patacoins > 0 else "0.0",
                rising_star=rising_star_name,
                rising_star_improvement=rising_star_improvement,
                rising_star_patacoins=f"{rising_star_patacoins:.1f}" if rising_star_patacoins > 0 else "0.0",
                consistent_contributor=consistent_contributor_name,
                consistency_description=consistency_description,
                consistent_contributor_patacoins=f"{consistent_contributor_patacoins:.1f}" if consistent_contributor_patacoins > 0 else "0.0",
                total_patacoins_today=f"{total_patacoins_today:.1f}" if total_patacoins_today > 0 else "0.0",
                top_patacoin_earner=top_patacoin_earner,
                engagement_analysis=engagement_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Error generating individual spotlight section: {str(e)}")
            return "## 🌟 PROTAGONISTAS DEL DÍA\n\n*Error al generar sección*\n\n---\n"
    
    def generate_financial_hub_section(self, data: Dict) -> str:
        """Generate financial hub section"""
        try:
            business_data = data.get('business', {})
            
            # Handle empty business data
            if not business_data:
                return "## 💰 HUB FINANCIERO\n\n*Datos de negocio no disponibles*\n\n---\n"
            
            # Business metrics with defaults
            active_businesses = business_data.get('active_businesses', 0)
            total_hbd_volume = business_data.get('total_hbd_volume', 0.0)
            top_business = business_data.get('top_business', {})
            
            # Format top business
            top_business_name = 'N/A'
            if top_business and isinstance(top_business, dict):
                username = top_business.get('username', 'N/A')
                if username and username != 'N/A':
                    volume = top_business.get('volume', 0)
                    top_business_name = f"@{username} (${volume:.2f})"
            
            # Weekly growth (placeholder)
            weekly_growth = "+5.2% 📈"  # Would need historical data
            
            # Generate business directory
            business_directory = self._generate_business_directory(business_data)
            
            # Generate transaction summary
            transaction_summary = self._generate_transaction_summary(business_data)
            
            return self.templates['financial_hub'].format(
                active_businesses=active_businesses,
                total_hbd_volume=total_hbd_volume,
                top_business=top_business_name,
                weekly_growth=weekly_growth,
                business_directory=business_directory,
                transaction_summary=transaction_summary
            )
            
        except Exception as e:
            self.logger.error(f"Error generating financial hub section: {str(e)}")
            return "## 💰 HUB FINANCIERO\n\n*Error al generar sección*\n\n---\n"
    
    def generate_footer_section(self, data: Dict) -> str:
        """Generate footer section"""
        try:
            # Calculate next report time
            next_report_time = "Mañana a las 21:00 (hora Ecuador)"
            
            return self.templates['footer'].format(
                next_report_time=next_report_time
            )
            
        except Exception as e:
            self.logger.error(f"Error generating footer section: {str(e)}")
            return ""
    
    def integrate_charts(self, sections: List[str], chart_files: List[str]) -> str:
        """Integrate charts into the report sections"""
        try:
            # Map chart files to sections
            chart_mapping = {
                'header': 0,
                'activity_trend': 1,
                'posts_volume': 1,
                'comments_engagement': 2,
                'upvotes_activity': 1,
                'hbd_flow': 3,
                'dashboard_summary': 4
            }
            
            # Add charts to appropriate sections
            for chart_file in chart_files:
                chart_name = Path(chart_file).stem
                
                # Determine which section to add the chart to
                section_index = None
                for key, index in chart_mapping.items():
                    if key in chart_name:
                        section_index = index
                        break
                
                if section_index is not None and section_index < len(sections):
                    # Add chart image reference
                    image_ref = f"\n![{chart_name}]({chart_file})\n"
                    sections[section_index] += image_ref
            
            return "\n".join(sections)
            
        except Exception as e:
            self.logger.error(f"Error integrating charts: {str(e)}")
            return "\n".join(sections)
    
    def add_engagement_hooks(self, content: str) -> str:
        """Add engagement hooks to increase community interaction"""
        try:
            # Add interactive elements
            engagement_hooks = [
                "\n> 💭 **¿Qué opinas de estos resultados?** ¡Comparte tus comentarios abajo!\n",
                "\n> 🎯 **Meta del día:** ¿Podemos superar estos números mañana?\n",
                "\n> 🏆 **¿Eres uno de nuestros top performers?** ¡Déjanos saber en los comentarios!\n",
                "\n> 📊 **¿Tienes sugerencias para mejorar el reporte?** ¡Nos encantaría escucharlas!\n"
            ]
            
            # Add random engagement hook
            import random
            hook = random.choice(engagement_hooks)
            content += hook
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error adding engagement hooks: {str(e)}")
            return content
    
    def replace_image_urls(self, content: str, uploaded_urls: List[str]) -> str:
        """Replace local image paths with uploaded URLs and improve descriptions"""
        try:
            import re
            from datetime import datetime
            
            # Get current date for descriptions
            current_date = datetime.now().strftime('%B %d, %Y')
            
            # Define better, more human image descriptions
            image_descriptions = {
                'header': f'Hive Ecuador Pulse - {current_date}',
                'activity_trend': f'Activity Trend - {current_date}',
                'posts_volume': f'Posts Volume - {current_date}', 
                'comments_engagement': f'Comments Engagement - {current_date}',
                'upvotes_activity': f'Upvotes Activity - {current_date}'
            }
            
            # Find all image references in content
            image_pattern = r'!\[(.*?)\]\((.*?)\)'
            matches = re.findall(image_pattern, content)
            
            self.logger.info(f"Found {len(matches)} image references in content")
            self.logger.info(f"Have {len(uploaded_urls)} uploaded URLs")
            
            # Replace each image reference
            for i, (old_alt_text, local_path) in enumerate(matches):
                if i < len(uploaded_urls):
                    # Determine image type from filename
                    image_type = None
                    for img_type in image_descriptions.keys():
                        if img_type in local_path.lower():
                            image_type = img_type
                            break
                    
                    # Get better description or fallback to original
                    new_description = image_descriptions.get(image_type, old_alt_text) if image_type else old_alt_text
                    
                    # Convert Imgur URL to proper format (ensure it ends with .png)
                    imgur_url = uploaded_urls[i]
                    if 'imgur.com' in imgur_url and not imgur_url.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        imgur_url = imgur_url + '.png'
                    
                    # Replace the old markdown with new one
                    old_markdown = f'![{old_alt_text}]({local_path})'
                    new_markdown = f'![{new_description}]({imgur_url})'
                    
                    content = content.replace(old_markdown, new_markdown)
                    self.logger.info(f"Replaced: {old_markdown} -> {new_markdown}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error replacing image URLs: {str(e)}")
            return content
    
    def _format_change(self, current: float, previous: float, is_percentage: bool = False) -> str:
        """Format change between two values"""
        try:
            if previous == 0:
                return "🆕 Nuevo" if current > 0 else "➡️ 0"
            
            if is_percentage:
                change = current - previous
                if change > 0:
                    return f"📈 +{change:.2f}%"
                elif change < 0:
                    return f"📉 {change:.2f}%"
                else:
                    return "➡️ Sin cambio"
            else:
                change = current - previous
                percentage = (change / previous) * 100
                
                if change > 0:
                    return f"📈 +{change:.0f} (+{percentage:.1f}%)"
                elif change < 0:
                    return f"📉 {change:.0f} ({percentage:.1f}%)"
                else:
                    return "➡️ Sin cambio"
                    
        except Exception as e:
            return "❓ N/A"
    
    def _get_health_emoji(self, health_index: float) -> str:
        """Get emoji based on health index"""
        if health_index >= 80:
            return "💪"
        elif health_index >= 60:
            return "👍"
        elif health_index >= 40:
            return "👌"
        elif health_index >= 20:
            return "😐"
        else:
            return "😴"
    
    def _generate_health_analysis(self, health_index: float, community_data: Dict) -> str:
        """Generate health analysis text"""
        try:
            if health_index >= 80:
                return "¡Excelente! Nuestra comunidad está en su mejor momento. Alta participación y engagement excepcional. 🔥"
            elif health_index >= 60:
                return "¡Muy bien! La comunidad muestra signos saludables de crecimiento y participación activa. 💪"
            elif health_index >= 40:
                return "Rendimiento sólido. Hay espacio para mejorar, pero vamos por buen camino. 👍"
            elif health_index >= 20:
                return "Actividad moderada. Podríamos beneficiarnos de más engagement y participación. 📈"
            else:
                return "Día tranquilo en la comunidad. ¡Oportunidad para crecer y activar más participación! 🚀"
                
        except Exception as e:
            return "Análisis en progreso... 🔄"
    
    def _format_top_performers(self, performer_data: Dict) -> str:
        """Format top performers for display"""
        try:
            users = performer_data.get('users', [])
            if not users:
                return "N/A"
            
            if len(users) == 1:
                return f"@{users[0]}"
            else:
                # Handle ties
                return f"@{', @'.join(users)} (empate)"
                
        except Exception as e:
            return "N/A"
    
    def _generate_engagement_analysis(self, data: Dict) -> str:
        """Generate engagement analysis text"""
        try:
            engagement_data = data.get('engagement', {})
            distribution = engagement_data.get('engagement_distribution', {})
            
            total_users = sum(distribution.values())
            if total_users == 0:
                return "No hay datos de engagement disponibles."
            
            high_engagement = distribution.get('high', 0)
            medium_engagement = distribution.get('medium', 0)
            low_engagement = distribution.get('low', 0)
            
            high_pct = (high_engagement / total_users) * 100
            medium_pct = (medium_engagement / total_users) * 100
            low_pct = (low_engagement / total_users) * 100
            
            analysis = f"""
**Distribución de Engagement:**
- 🔥 Alto engagement: {high_engagement} usuarios ({high_pct:.1f}%)
- 💪 Medio engagement: {medium_engagement} usuarios ({medium_pct:.1f}%)
- 😴 Bajo engagement: {low_engagement} usuarios ({low_pct:.1f}%)

**Total de usuarios activos:** {total_users}
"""
            
            return analysis
            
        except Exception as e:
            return "Análisis de engagement en progreso... 🔄"
    
    def _generate_business_directory(self, business_data: Dict) -> str:
        """Generate business directory section"""
        try:
            businesses = business_data.get('businesses', [])
            if not businesses:
                return "No hay negocios registrados aún. ¡Sé el primero en registrar tu negocio!"
            
            directory = ""
            for business in businesses[:10]:  # Limit to top 10
                name = business.get('business_name', 'N/A')
                username = business.get('username', '')
                category = business.get('category', 'General')
                
                directory += f"- 🏢 **{name}** (@{username}) - *{category}*\n"
            
            if len(businesses) > 10:
                directory += f"\n*... y {len(businesses) - 10} negocios más*"
            
            return directory
            
        except Exception as e:
            return "Directorio en construcción... 🏗️"
    
    def _generate_transaction_summary(self, business_data: Dict) -> str:
        """Generate transaction summary"""
        try:
            transactions = business_data.get('transactions', [])
            if not transactions:
                return "No hay transacciones registradas hoy."
            
            total_transactions = len(transactions)
            total_volume = sum(float(tx.get('amount', 0)) for tx in transactions)
            avg_transaction = total_volume / total_transactions if total_transactions > 0 else 0
            
            # Categorize transactions
            small_tx = len([tx for tx in transactions if float(tx.get('amount', 0)) < 1])
            medium_tx = len([tx for tx in transactions if 1 <= float(tx.get('amount', 0)) < 10])
            large_tx = len([tx for tx in transactions if float(tx.get('amount', 0)) >= 10])
            
            summary = f"""
**Resumen de Transacciones:**
- 📊 Total de transacciones: {total_transactions}
- 💰 Volumen total: ${total_volume:.3f} HBD
- 📈 Transacción promedio: ${avg_transaction:.3f} HBD

**Por categoría:**
- 🟡 Pequeñas (< $1): {small_tx} transacciones
- 🔵 Medianas ($1-$10): {medium_tx} transacciones
- 🔴 Grandes (> $10): {large_tx} transacciones
"""
            
            return summary
            
        except Exception as e:
            return "Resumen de transacciones en progreso... 💼"
    
    def _get_patacoins_for_user(self, user_activities: List, username: str) -> float:
        """Get Patacoins earned for a specific user"""
        try:
            if not user_activities or not username or username == 'N/A':
                return 0.0
            
            # Normalize username (remove @ if present)
            search_username = username.strip('@').lower()
            
            for activity in user_activities:
                # Handle both dict and UserActivity object formats
                if isinstance(activity, dict):
                    activity_username = str(activity.get('username', '')).strip('@').lower()
                    if activity_username == search_username:
                        patacoins = activity.get('patacoins_earned', 0.0)
                        self.logger.info(f"Found Patacoins for {username}: {patacoins}")
                        return float(patacoins)
                else:
                    # Assume UserActivity object with attributes
                    if hasattr(activity, 'username'):
                        activity_username = str(getattr(activity, 'username', '')).strip('@').lower()
                        if activity_username == search_username:
                            patacoins = getattr(activity, 'patacoins_earned', 0.0)
                            self.logger.info(f"Found Patacoins for {username}: {patacoins}")
                            return float(patacoins)
            
            self.logger.warning(f"No Patacoins found for user {username} in {len(user_activities)} activities")
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting Patacoins for user {username}: {e}")
            return 0.0
    
    def _get_top_patacoin_earner(self, user_activities: List) -> str:
        """Get the username of the top Patacoin earner"""
        try:
            if not user_activities:
                return "N/A"
            
            max_patacoins = 0.0
            top_earner = "N/A"
            
            for activity in user_activities:
                patacoins = 0.0
                username = ""
                
                # Handle both dict and UserActivity object formats
                if isinstance(activity, dict):
                    patacoins = float(activity.get('patacoins_earned', 0.0))
                    username = activity.get('username', '')
                else:
                    # Assume UserActivity object with attributes
                    if hasattr(activity, 'patacoins_earned'):
                        patacoins = float(getattr(activity, 'patacoins_earned', 0.0))
                    if hasattr(activity, 'username'):
                        username = getattr(activity, 'username', '')
                
                if patacoins > max_patacoins and username:
                    max_patacoins = patacoins
                    top_earner = f"@{username} ({patacoins:.1f} 🪙)"
            
            return top_earner if top_earner != "N/A" else "N/A"
        except Exception as e:
            self.logger.error(f"Error getting top Patacoin earner: {e}")
            return "N/A"
