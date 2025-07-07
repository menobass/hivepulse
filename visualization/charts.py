"""
Chart Generator Module
Creates professional charts with Ecuador theme for the Hive Ecuador Pulse bot
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


class ChartGenerator:
    """Generates charts and visualizations for the Hive Ecuador Pulse bot"""
    
    def __init__(self, theme_config: Dict):
        """Initialize chart generator with theme configuration"""
        self.config = theme_config
        self.logger = logging.getLogger(__name__)
        
        # Ecuador flag colors
        self.colors = theme_config.get('ecuador_colors', {
            'yellow': '#FFDD00',
            'blue': '#0052CC',
            'red': '#FF0000'
        })
        
        # Extended color palette
        self.extended_colors = [
            self.colors['yellow'],
            self.colors['blue'],
            self.colors['red'],
            '#FF6B35',  # Orange
            '#4ECDC4',  # Teal
            '#45B7D1',  # Light blue
            '#FFA726',  # Amber
            '#66BB6A',  # Green
            '#AB47BC',  # Purple
            '#EF5350'   # Light red
        ]
        
        # Chart style settings
        self.chart_style = theme_config.get('chart_style', 'professional')
        self.font_family = theme_config.get('font_family', 'Arial')
        
        # Create charts directory
        self.charts_dir = Path("charts")
        self.charts_dir.mkdir(exist_ok=True)
        
        # Setup matplotlib style
        self._setup_matplotlib_style()
    
    def _setup_matplotlib_style(self):
        """Setup matplotlib style for professional charts"""
        plt.style.use('seaborn-v0_8')
        
        # Set default font with fallback
        try:
            plt.rcParams['font.family'] = self.font_family
        except:
            # Fall back to default font
            plt.rcParams['font.family'] = 'DejaVu Sans'
            
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
        plt.rcParams['figure.titlesize'] = 16
        
        # Professional styling
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['grid.linewidth'] = 0.5
    
    def apply_ecuador_theme(self, fig, ax):
        """Apply Ecuador theme to matplotlib figure"""
        # Set background colors
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#FAFAFA')
        
        # Grid styling
        ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        
        # Spine styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#CCCCCC')
        ax.spines['left'].set_color('#CCCCCC')
        
        # Tick styling
        ax.tick_params(colors='#666666')
        
        return fig, ax
    
    def create_header_image(self, date: str) -> str:
        """Create header image for daily report"""
        self.logger.info(f"Creating header image for {date}")
        
        try:
            # Create image with Ecuador flag colors
            width, height = 1200, 400
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Draw Ecuador flag stripes
            stripe_height = height // 4
            
            # Yellow stripe (top half)
            draw.rectangle([0, 0, width, height//2], fill=self.colors['yellow'])
            
            # Blue stripe
            draw.rectangle([0, height//2, width, height//2 + stripe_height], fill=self.colors['blue'])
            
            # Red stripe (bottom)
            draw.rectangle([0, height//2 + stripe_height, width, height], fill=self.colors['red'])
            
            # Add text overlay
            try:
                # Try to load a font with better fallback
                try:
                    font_large = ImageFont.truetype("arial.ttf", 48)
                    font_medium = ImageFont.truetype("arial.ttf", 24)
                    font_small = ImageFont.truetype("arial.ttf", 18)
                except (OSError, IOError):
                    # Try alternative common fonts
                    try:
                        font_large = ImageFont.truetype("calibri.ttf", 48)
                        font_medium = ImageFont.truetype("calibri.ttf", 24)
                        font_small = ImageFont.truetype("calibri.ttf", 18)
                    except (OSError, IOError):
                        # Fall back to default font
                        font_large = ImageFont.load_default()
                        font_medium = ImageFont.load_default()
                        font_small = ImageFont.load_default()
            except Exception as e:
                self.logger.warning(f"Font loading warning: {e}")
                # Fall back to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Add semi-transparent overlay for text readability
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 128))
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            draw = ImageDraw.Draw(img)
            
            # Main title
            title = "🇪🇨 HIVE ECUADOR PULSE"
            title_bbox = draw.textbbox((0, 0), title, font=font_large)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, 80), title, font=font_large, fill='white')
            
            # Subtitle
            subtitle = "Daily Community Analytics Report"
            subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_medium)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            draw.text((subtitle_x, 150), subtitle, font=font_medium, fill='white')
            
            # Date
            date_formatted = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
            date_bbox = draw.textbbox((0, 0), date_formatted, font=font_small)
            date_width = date_bbox[2] - date_bbox[0]
            date_x = (width - date_width) // 2
            draw.text((date_x, 200), date_formatted, font=font_small, fill='white')
            
            # Add pulse effect (decorative circles)
            center_x, center_y = width // 2, height // 2
            for i in range(3):
                radius = 20 + i * 10
                alpha = 100 - i * 30
                circle_overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
                circle_draw = ImageDraw.Draw(circle_overlay)
                circle_draw.ellipse([center_x - radius, center_y - radius, 
                                   center_x + radius, center_y + radius], 
                                  outline=(255, 255, 255, alpha), width=2)
                img = Image.alpha_composite(img, circle_overlay)
            
            # Save image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"header_{date}_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            img.convert('RGB').save(filepath, 'PNG', optimize=True, quality=95)
            
            self.logger.info(f"Header image created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating header image: {str(e)}")
            raise
    
    def create_activity_trend_chart(self, community_data: Dict) -> str:
        """Create activity trend chart showing 7-day trends"""
        self.logger.info("Creating activity trend chart")
        
        try:
            # Prepare data
            historical_data = community_data.get('historical_data', [])
            if not historical_data:
                return ""
            
            # Sort by date
            historical_data.sort(key=lambda x: x['date'])
            
            dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in historical_data]
            active_users = [item['active_users'] for item in historical_data]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            fig, ax = self.apply_ecuador_theme(fig, ax)
            
            # Plot line
            ax.plot(dates, active_users, color=self.colors['blue'], linewidth=3, 
                   marker='o', markersize=8, markerfacecolor=self.colors['yellow'])
            
            # Fill area under curve
            ax.fill_between(dates, active_users, alpha=0.3, color=self.colors['blue'])
            
            # Formatting
            ax.set_title('📊 Usuarios Activos - Tendencia 7 Días', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Fecha', fontsize=12)
            ax.set_ylabel('Usuarios Activos', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45)
            
            # Add value labels on points
            for i, (date, users) in enumerate(zip(dates, active_users)):
                ax.annotate(f'{users}', (date, users), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=10, fontweight='bold')
            
            # Add growth indicator
            if len(active_users) >= 2:
                growth = ((active_users[-1] - active_users[0]) / active_users[0]) * 100
                growth_text = f"📈 +{growth:.1f}%" if growth > 0 else f"📉 {growth:.1f}%"
                ax.text(0.02, 0.98, growth_text, transform=ax.transAxes, 
                       fontsize=12, fontweight='bold', va='top',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['yellow'], alpha=0.8))
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"activity_trend_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Activity trend chart created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating activity trend chart: {str(e)}")
            return ""
    
    def create_posts_volume_chart(self, community_data: Dict) -> str:
        """Create posts volume chart with growth indicators"""
        self.logger.info("Creating posts volume chart")
        
        try:
            historical_data = community_data.get('historical_data', [])
            if not historical_data:
                return ""
            
            # Sort by date
            historical_data.sort(key=lambda x: x['date'])
            
            dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in historical_data]
            posts = [item['total_posts'] for item in historical_data]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            fig, ax = self.apply_ecuador_theme(fig, ax)
            
            # Create bar chart
            bars = ax.bar(dates, posts, color=self.colors['yellow'], alpha=0.8, 
                         edgecolor=self.colors['blue'], linewidth=2)
            
            # Add gradient effect
            for bar in bars:
                height = bar.get_height()
                bar.set_facecolor(self.colors['yellow'])
                bar.set_alpha(0.8)
            
            # Formatting
            ax.set_title('📝 Volumen de Posts - Últimos 7 Días', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Fecha', fontsize=12)
            ax.set_ylabel('Número de Posts', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                           fontsize=10, fontweight='bold')
            
            # Add trend line
            z = np.polyfit(range(len(posts)), posts, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(range(len(posts))), color=self.colors['red'], 
                   linestyle='--', linewidth=2, alpha=0.7)
            
            # Add statistics
            avg_posts = np.mean(posts)
            max_posts = max(posts)
            stats_text = f"📊 Promedio: {avg_posts:.1f} | Máximo: {max_posts}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   fontsize=10, va='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"posts_volume_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Posts volume chart created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating posts volume chart: {str(e)}")
            return ""
    
    def create_comments_chart(self, community_data: Dict) -> str:
        """Create comments activity chart"""
        self.logger.info("Creating comments chart")
        
        try:
            historical_data = community_data.get('historical_data', [])
            if not historical_data:
                return ""
            
            # Sort by date
            historical_data.sort(key=lambda x: x['date'])
            
            dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in historical_data]
            comments = [item['total_comments'] for item in historical_data]
            posts = [item['total_posts'] for item in historical_data]
            
            # Calculate engagement rate
            engagement_rates = [(c/p if p > 0 else 0) for c, p in zip(comments, posts)]
            
            # Create figure with dual y-axis
            fig, ax1 = plt.subplots(figsize=(12, 6))
            fig, ax1 = self.apply_ecuador_theme(fig, ax1)
            
            # Plot comments bars
            bars = ax1.bar(dates, comments, color=self.colors['blue'], alpha=0.7, 
                          label='Comentarios')
            
            # Create second y-axis for engagement rate
            ax2 = ax1.twinx()
            line = ax2.plot(dates, engagement_rates, color=self.colors['red'], 
                           linewidth=3, marker='o', markersize=6, 
                           label='Tasa de Engagement')
            
            # Formatting
            ax1.set_title('💬 Actividad de Comentarios y Engagement', fontsize=16, fontweight='bold', pad=20)
            ax1.set_xlabel('Fecha', fontsize=12)
            ax1.set_ylabel('Número de Comentarios', fontsize=12, color=self.colors['blue'])
            ax2.set_ylabel('Comentarios por Post', fontsize=12, color=self.colors['red'])
            
            # Format x-axis
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            plt.xticks(rotation=45)
            
            # Add value labels
            for bar, rate in zip(bars, engagement_rates):
                height = bar.get_height()
                ax1.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                           fontsize=9, fontweight='bold')
            
            # Add legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Add average engagement rate
            avg_engagement = np.mean(engagement_rates)
            ax2.axhline(y=avg_engagement, color=self.colors['yellow'], linestyle='--', 
                       linewidth=2, alpha=0.7)
            ax2.text(0.02, 0.98, f"🎯 Engagement promedio: {avg_engagement:.2f}", 
                    transform=ax2.transAxes, fontsize=10, va='top',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['yellow'], alpha=0.8))
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"comments_engagement_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Comments chart created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating comments chart: {str(e)}")
            return ""
    
    def create_upvotes_chart(self, community_data: Dict) -> str:
        """Create upvotes activity chart"""
        self.logger.info("Creating upvotes chart")
        
        try:
            historical_data = community_data.get('historical_data', [])
            if not historical_data:
                return ""
            
            # Sort by date
            historical_data.sort(key=lambda x: x['date'])
            
            dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in historical_data]
            upvotes = [item['total_upvotes'] for item in historical_data]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            fig, ax = self.apply_ecuador_theme(fig, ax)
            
            # Create area chart
            ax.fill_between(dates, upvotes, color=self.colors['red'], alpha=0.6)
            ax.plot(dates, upvotes, color=self.colors['red'], linewidth=3, 
                   marker='o', markersize=6, markerfacecolor=self.colors['yellow'])
            
            # Formatting
            ax.set_title('👍 Actividad de Upvotes - Apoyo Comunitario', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Fecha', fontsize=12)
            ax.set_ylabel('Número de Upvotes', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            plt.xticks(rotation=45)
            
            # Add value labels
            for date, votes in zip(dates, upvotes):
                ax.annotate(f'{votes}', (date, votes), textcoords="offset points", 
                           xytext=(0,10), ha='center', fontsize=10, fontweight='bold')
            
            # Add statistics
            total_upvotes = sum(upvotes)
            avg_upvotes = np.mean(upvotes)
            stats_text = f"🏆 Total: {total_upvotes} | Promedio: {avg_upvotes:.1f}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   fontsize=10, va='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
            
            # Add trend arrow
            if len(upvotes) >= 2:
                trend = upvotes[-1] - upvotes[0]
                trend_emoji = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                ax.text(0.98, 0.98, f"{trend_emoji} {trend:+d}", transform=ax.transAxes, 
                       fontsize=14, ha='right', va='top', fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"upvotes_activity_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Upvotes chart created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating upvotes chart: {str(e)}")
            return ""
    
    def create_hbd_flow_chart(self, business_data: Dict) -> str:
        """Create HBD transaction flow chart"""
        self.logger.info("Creating HBD flow chart")
        
        try:
            transactions = business_data.get('transactions', [])
            if not transactions:
                return ""
            
            # Group transactions by date
            daily_volumes = {}
            for tx in transactions:
                date = tx.get('date', datetime.now().strftime('%Y-%m-%d'))
                if date not in daily_volumes:
                    daily_volumes[date] = 0
                daily_volumes[date] += float(tx.get('amount', 0))
            
            # Sort by date
            sorted_dates = sorted(daily_volumes.keys())
            dates = [datetime.strptime(date, '%Y-%m-%d') for date in sorted_dates]
            volumes = [daily_volumes[date] for date in sorted_dates]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            fig, ax = self.apply_ecuador_theme(fig, ax)
            
            # Create bar chart with gradient
            bars = ax.bar(dates, volumes, color=self.colors['yellow'], alpha=0.8, 
                         edgecolor=self.colors['blue'], linewidth=2)
            
            # Add gradient effect to bars
            for bar in bars:
                height = bar.get_height()
                # Create gradient effect
                gradient = np.linspace(0, 1, 100).reshape(1, -1)
                gradient = np.vstack((gradient, gradient))
                
                # Apply gradient
                extent = [bar.get_x(), bar.get_x() + bar.get_width(), 0, height]
                ax.imshow(gradient, aspect='auto', extent=extent, alpha=0.3, 
                         cmap='YlOrRd', vmin=0, vmax=1)
            
            # Formatting
            ax.set_title('💰 Flujo de HBD - Actividad Económica', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Fecha', fontsize=12)
            ax.set_ylabel('Volumen HBD', fontsize=12)
            
            # Format x-axis
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            plt.xticks(rotation=45)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'${height:.2f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                           fontsize=10, fontweight='bold')
            
            # Add statistics
            total_volume = sum(volumes)
            avg_volume = np.mean(volumes)
            max_volume = max(volumes)
            
            stats_text = f"💼 Total: ${total_volume:.2f} | Promedio: ${avg_volume:.2f} | Máximo: ${max_volume:.2f}"
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                   fontsize=10, va='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9))
            
            # Add business count
            unique_businesses = len(set([tx.get('from', '') for tx in transactions] + 
                                       [tx.get('to', '') for tx in transactions]))
            business_text = f"🏢 Negocios activos: {unique_businesses}"
            ax.text(0.98, 0.98, business_text, transform=ax.transAxes, 
                   fontsize=10, ha='right', va='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['yellow'], alpha=0.8))
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hbd_flow_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"HBD flow chart created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating HBD flow chart: {str(e)}")
            return ""
    
    def create_user_engagement_pie_chart(self, user_activities: List) -> str:
        """Create pie chart showing user engagement distribution"""
        self.logger.info("Creating user engagement pie chart")
        
        try:
            if not user_activities:
                return ""
            
            # Categorize users by engagement level
            low_engagement = len([u for u in user_activities if u.engagement_score < 20])
            medium_engagement = len([u for u in user_activities if 20 <= u.engagement_score < 50])
            high_engagement = len([u for u in user_activities if u.engagement_score >= 50])
            
            # Data for pie chart
            labels = ['Bajo Engagement', 'Medio Engagement', 'Alto Engagement']
            sizes = [low_engagement, medium_engagement, high_engagement]
            colors = [self.colors['red'], self.colors['yellow'], self.colors['blue']]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 8))
            fig, ax = self.apply_ecuador_theme(fig, ax)
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90,
                                             textprops={'fontsize': 12, 'fontweight': 'bold'})
            
            # Enhance visual appeal
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Add title
            ax.set_title('📊 Distribución de Engagement de Usuarios', fontsize=16, fontweight='bold', pad=20)
            
            # Add total users count
            total_users = len(user_activities)
            ax.text(0.5, -0.1, f"Total de usuarios: {total_users}", transform=ax.transAxes, 
                   ha='center', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_engagement_pie_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"User engagement pie chart created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating user engagement pie chart: {str(e)}")
            return ""
    
    def create_summary_dashboard(self, data: Dict) -> str:
        """Create comprehensive dashboard with multiple metrics"""
        self.logger.info("Creating summary dashboard")
        
        try:
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('📊 Hive Ecuador Pulse - Dashboard Resumen', fontsize=18, fontweight='bold')
            
            # Apply theme to all subplots
            for ax in [ax1, ax2, ax3, ax4]:
                ax.set_facecolor('#FAFAFA')
                ax.grid(True, alpha=0.3)
            
            # 1. Active Users Trend (top-left)
            historical_data = data['community'].get('historical_data', [])
            dates = []
            if historical_data:
                dates = [datetime.strptime(item['date'], '%Y-%m-%d') for item in historical_data]
                active_users = [item['active_users'] for item in historical_data]
                
                ax1.plot(dates, active_users, color=self.colors['blue'], linewidth=2, marker='o')
                ax1.fill_between(dates, active_users, alpha=0.3, color=self.colors['blue'])
                ax1.set_title('Usuarios Activos', fontweight='bold')
                ax1.set_ylabel('Usuarios')
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
            else:
                ax1.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', transform=ax1.transAxes)
                ax1.set_title('Usuarios Activos', fontweight='bold')
            
            # 2. Posts vs Comments (top-right)
            if historical_data and dates:
                posts = [item['total_posts'] for item in historical_data]
                comments = [item['total_comments'] for item in historical_data]
                
                width = 0.35
                x = np.arange(len(dates))
                
                ax2.bar(x - width/2, posts, width, label='Posts', color=self.colors['yellow'], alpha=0.8)
                ax2.bar(x + width/2, comments, width, label='Comentarios', color=self.colors['red'], alpha=0.8)
                ax2.set_title('Posts vs Comentarios', fontweight='bold')
                ax2.set_ylabel('Cantidad')
                ax2.legend()
                ax2.set_xticks(x)
                ax2.set_xticklabels([d.strftime('%d/%m') for d in dates], rotation=45)
            else:
                ax2.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title('Posts vs Comentarios', fontweight='bold')
            
            # 3. Top Performers (bottom-left)
            top_performers = data.get('top_performers', {})
            
            categories = []
            values = []
            
            if top_performers.get('top_poster', {}).get('count', 0) > 0:
                categories.append('Top Poster')
                values.append(top_performers['top_poster']['count'])
            
            if top_performers.get('top_commenter', {}).get('count', 0) > 0:
                categories.append('Top Commenter')
                values.append(top_performers['top_commenter']['count'])
            
            if top_performers.get('top_supporter', {}).get('count', 0) > 0:
                categories.append('Top Supporter')
                values.append(top_performers['top_supporter']['count'])
            
            if categories:
                bars = ax3.bar(categories, values, color=self.extended_colors[:len(categories)])
                ax3.set_title('Top Performers', fontweight='bold')
                ax3.set_ylabel('Actividad')
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax3.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                               xytext=(0, 3), textcoords="offset points", ha='center', va='bottom',
                               fontweight='bold')
            
            # 4. HBD Volume (bottom-right)
            business_data = data.get('business', {})
            if business_data.get('transactions'):
                # Group by amount ranges
                small_tx = len([tx for tx in business_data['transactions'] if float(tx.get('amount', 0)) < 1])
                medium_tx = len([tx for tx in business_data['transactions'] if 1 <= float(tx.get('amount', 0)) < 10])
                large_tx = len([tx for tx in business_data['transactions'] if float(tx.get('amount', 0)) >= 10])
                
                labels = ['< $1 HBD', '$1-$10 HBD', '> $10 HBD']
                sizes = [small_tx, medium_tx, large_tx]
                colors = [self.colors['yellow'], self.colors['blue'], self.colors['red']]
                
                ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax4.set_title('Distribución de Transacciones HBD', fontweight='bold')
            
            plt.tight_layout()
            
            # Save dashboard
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"dashboard_summary_{timestamp}.png"
            filepath = self.charts_dir / filename
            
            plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            
            self.logger.info(f"Summary dashboard created: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error creating summary dashboard: {str(e)}")
            return ""
