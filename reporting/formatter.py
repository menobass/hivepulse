"""
Report formatter for Hive Ecuador Pulse Analytics Bot
Handles markdown formatting, content optimization, and post structure
"""

import re
import html
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MarkdownFormatter:
    """Handles markdown formatting and optimization"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_length = config.get('max_post_length', 50000)  # Hive post limit
        self.optimize_for_mobile = config.get('optimize_for_mobile', True)
        
    def format_post(self, content: str) -> str:
        """Format content for Hive posting"""
        try:
            # Clean and optimize content
            content = self._clean_content(content)
            content = self._optimize_formatting(content)
            content = self._add_post_metadata(content)
            
            # Ensure content length is within limits
            if len(content) > self.max_length:
                content = self._truncate_content(content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting post: {e}")
            return content
    
    def _clean_content(self, content: str) -> str:
        """Clean and sanitize content"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = re.sub(r' +', ' ', content)
        
        # Escape HTML characters
        content = html.escape(content, quote=False)
        
        # Fix markdown formatting issues
        content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', content)  # Bold
        content = re.sub(r'\*([^*]+)\*', r'*\1*', content)        # Italic
        
        return content.strip()
    
    def _optimize_formatting(self, content: str) -> str:
        """Optimize formatting for readability"""
        if self.optimize_for_mobile:
            # Add more spacing for mobile readability
            content = re.sub(r'(#{1,6}[^#\n]+)', r'\1\n', content)
            content = re.sub(r'(\|[^|]+\|)', r'\1\n', content)
        
        # Ensure proper spacing around headers
        content = re.sub(r'(^|\n)(#{1,6}[^#\n]+)', r'\1\n\2\n', content)
        
        # Ensure proper spacing around tables
        content = re.sub(r'(\|[^|]+\|[^|]*\|)', r'\n\1\n', content)
        
        # Clean up extra newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content
    
    def _add_post_metadata(self, content: str) -> str:
        """Add post metadata and tags"""
        # Add posting metadata at the end
        metadata = f"""

---

*Este reporte fue generado automáticamente por el Hive Ecuador Pulse Bot*

**Síguenos en:**
- [Hive Ecuador Community](https://peakd.com/c/hive-115276)
- [Discord](https://discord.gg/hive-ecuador)
- [Telegram](https://t.me/hive_ecuador)

#HiveEcuador #Analytics #Community #Blockchain #Report
"""
        
        return content + metadata
    
    def _truncate_content(self, content: str) -> str:
        """Truncate content to fit within limits"""
        if len(content) <= self.max_length:
            return content
        
        # Find a good truncation point (prefer end of paragraph)
        target_length = self.max_length - 200  # Leave room for truncation message
        
        # Try to truncate at paragraph boundary
        paragraphs = content.split('\n\n')
        truncated = ""
        
        for paragraph in paragraphs:
            if len(truncated + paragraph) > target_length:
                break
            truncated += paragraph + '\n\n'
        
        # Add truncation message
        truncated += "\n\n*[Reporte truncado debido a límites de longitud]*"
        
        return truncated
    
    def format_table(self, data: List[Dict[str, Any]], headers: List[str]) -> str:
        """Format data as markdown table"""
        try:
            if not data or not headers:
                return ""
            
            # Create header row
            header_row = "|" + "|".join(headers) + "|"
            separator_row = "|" + "|".join(["---"] * len(headers)) + "|"
            
            # Create data rows
            rows = []
            for item in data:
                row_data = []
                for header in headers:
                    value = item.get(header.lower().replace(' ', '_'), '')
                    row_data.append(str(value))
                rows.append("|" + "|".join(row_data) + "|")
            
            return "\n".join([header_row, separator_row] + rows) + "\n"
            
        except Exception as e:
            logger.error(f"Error formatting table: {e}")
            return ""
    
    def format_list(self, items: List[str], ordered: bool = False) -> str:
        """Format list items"""
        try:
            if not items:
                return ""
            
            formatted_items = []
            for i, item in enumerate(items, 1):
                if ordered:
                    formatted_items.append(f"{i}. {item}")
                else:
                    formatted_items.append(f"- {item}")
            
            return "\n".join(formatted_items) + "\n"
            
        except Exception as e:
            logger.error(f"Error formatting list: {e}")
            return ""
    
    def format_metrics_section(self, metrics: Dict[str, Any], title: str) -> str:
        """Format metrics as a structured section"""
        try:
            content = f"\n## {title}\n\n"
            
            for key, value in metrics.items():
                # Format key (convert snake_case to Title Case)
                display_key = key.replace('_', ' ').title()
                
                # Format value based on type
                if isinstance(value, float):
                    if 'rate' in key.lower() or 'percentage' in key.lower():
                        display_value = f"{value:.1f}%"
                    elif 'amount' in key.lower() or 'reward' in key.lower():
                        display_value = f"{value:.3f} HIVE"
                    else:
                        display_value = f"{value:.2f}"
                elif isinstance(value, int):
                    display_value = f"{value:,}"
                else:
                    display_value = str(value)
                
                content += f"- **{display_key}**: {display_value}\n"
            
            return content + "\n"
            
        except Exception as e:
            logger.error(f"Error formatting metrics section: {e}")
            return ""

class HiveFormatter:
    """Handles Hive-specific formatting requirements"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.community = config.get('community', 'hive-115276')
        
    def format_user_mention(self, username: str) -> str:
        """Format user mention for Hive"""
        return f"@{username.lstrip('@')}"
    
    def format_community_tag(self, community: Optional[str] = None) -> str:
        """Format community tag"""
        if community is None:
            community = self.community
        return f"#{community}"
    
    def format_hive_amount(self, amount: float, token: str = 'HIVE') -> str:
        """Format Hive token amount"""
        return f"{amount:.3f} {token}"
    
    def format_reputation(self, reputation: int) -> str:
        """Format Hive reputation score"""
        # Convert raw reputation to readable format
        if reputation <= 0:
            return "25"
        
        import math
        score = math.log10(reputation) - 9
        score = max(score * 9 + 25, 0)
        return f"{score:.0f}"
    
    def create_post_json(self, title: str, body: str, tags: List[str], 
                        community: Optional[str] = None) -> Dict[str, Any]:
        """Create JSON structure for Hive posting"""
        if community is None:
            community = self.community
        
        # Ensure first tag is the community
        if community and community not in tags:
            tags.insert(0, community)
        
        # Limit tags to 10 (Hive limit)
        tags = tags[:10]
        
        return {
            "title": title,
            "body": body,
            "json_metadata": {
                "tags": tags,
                "community": community,
                "app": "hive-ecuador-pulse/1.0.0",
                "format": "markdown"
            }
        }
    
    def validate_post_content(self, content: str) -> Tuple[bool, List[str]]:
        """Validate post content for Hive posting"""
        issues = []
        
        # Check length
        if len(content) > 50000:
            issues.append("Content exceeds maximum length (50,000 characters)")
        
        if len(content) < 100:
            issues.append("Content is too short (minimum 100 characters)")
        
        # Check for required elements
        if not content.strip():
            issues.append("Content is empty")
        
        # Check for potential formatting issues
        if content.count('```') % 2 != 0:
            issues.append("Unmatched code blocks")
        
        if content.count('**') % 2 != 0:
            issues.append("Unmatched bold formatting")
        
        if content.count('*') % 2 != 0:
            issues.append("Unmatched italic formatting")
        
        return len(issues) == 0, issues

class ContentOptimizer:
    """Optimizes content for better engagement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
    def optimize_for_engagement(self, content: str) -> str:
        """Optimize content for better engagement"""
        try:
            # Add engagement elements
            content = self._add_call_to_action(content)
            content = self._add_discussion_prompts(content)
            content = self._optimize_hashtags(content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return content
    
    def _add_call_to_action(self, content: str) -> str:
        """Add call-to-action elements"""
        cta_section = """

## 💬 ¡Participa en la Conversación!

¿Te gustó este reporte? ¡Déjanos saber tu opinión!

- 👍 **Vota** si encontraste información valiosa
- 💬 **Comenta** qué te pareció más interesante
- 🔄 **Comparte** con otros miembros de la comunidad
- 📢 **Sugiere** mejoras para futuros reportes

"""
        
        # Insert CTA before the final metadata
        if "---" in content:
            parts = content.rsplit("---", 1)
            return parts[0] + cta_section + "---" + parts[1]
        else:
            return content + cta_section
    
    def _add_discussion_prompts(self, content: str) -> str:
        """Add discussion prompts"""
        prompts = [
            "¿Qué opinas sobre el crecimiento de nuestra comunidad?",
            "¿Cuál crees que es el mayor desafío para Hive Ecuador?",
            "¿Qué estrategias sugieres para aumentar la participación?",
            "¿Te gustaría ver alguna métrica adicional en futuros reportes?"
        ]
        
        import random
        selected_prompt = random.choice(prompts)
        
        prompt_section = f"""

## 🤔 Pregunta para la Comunidad

**{selected_prompt}**

¡Comparte tu perspectiva en los comentarios!

"""
        
        return content + prompt_section
    
    def _optimize_hashtags(self, content: str) -> str:
        """Optimize hashtags for better discoverability"""
        # Extract existing hashtags
        existing_hashtags = re.findall(r'#\w+', content)
        
        # Suggested hashtags for Ecuador content
        suggested_hashtags = [
            "#HiveEcuador", "#Ecuador", "#Blockchain", "#Analytics",
            "#Community", "#Report", "#Hive", "#Cryptocurrency",
            "#SouthAmerica", "#LatinAmerica", "#Data", "#Growth"
        ]
        
        # Add missing important hashtags
        for hashtag in suggested_hashtags[:5]:  # Limit to avoid spam
            if hashtag not in existing_hashtags:
                content += f" {hashtag}"
        
        return content

class ReportFormatter:
    """Main report formatter combining all formatting capabilities"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.markdown_formatter = MarkdownFormatter(config)
        self.hive_formatter = HiveFormatter(config)
        self.content_optimizer = ContentOptimizer(config)
    
    def format_complete_report(self, content: str, title: Optional[str] = None,
                             tags: Optional[List[str]] = None, optimize: bool = True) -> Dict[str, Any]:
        """Format complete report for posting"""
        try:
            # Apply markdown formatting
            formatted_content = self.markdown_formatter.format_post(content)
            
            # Optimize for engagement if requested
            if optimize:
                formatted_content = self.content_optimizer.optimize_for_engagement(formatted_content)
            
            # Generate title if not provided
            if title is None:
                title = f"🇪🇨 Hive Ecuador Pulse - Reporte Diario {datetime.now().strftime('%d/%m/%Y')}"
            
            # Generate tags if not provided
            if tags is None:
                tags = ['hive-115276', 'hiveecuador', 'ecuador', 'analytics', 'community', 'report']
            
            # Create post JSON
            post_json = self.hive_formatter.create_post_json(title, formatted_content, tags)
            
            # Validate content
            is_valid, issues = self.hive_formatter.validate_post_content(formatted_content)
            
            return {
                'title': title,
                'content': formatted_content,
                'json': post_json,
                'valid': is_valid,
                'issues': issues,
                'length': len(formatted_content),
                'tags': tags
            }
            
        except Exception as e:
            logger.error(f"Error formatting complete report: {e}")
            return {
                'title': title or "Error Report",
                'content': "Error formatting report content",
                'json': {},
                'valid': False,
                'issues': [str(e)],
                'length': 0,
                'tags': []
            }
    
    def preview_report(self, content: str) -> str:
        """Generate preview of formatted report"""
        try:
            # Format content
            formatted_content = self.markdown_formatter.format_post(content)
            
            # Truncate for preview
            preview_length = 1000
            if len(formatted_content) > preview_length:
                preview = formatted_content[:preview_length] + "\n\n...[continued]"
            else:
                preview = formatted_content
            
            return preview
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return "Error generating preview"
