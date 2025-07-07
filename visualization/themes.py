"""
Visual themes and styling for Hive Ecuador Pulse Analytics Bot
Handles Ecuador-themed color schemes, styling, and chart appearance
"""

import matplotlib.pyplot as plt
import matplotlib.style as style
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class EcuadorTheme:
    """Ecuador flag themed visual styling"""
    
    # Ecuador flag colors
    COLORS = {
        'yellow': '#FFDD00',      # Ecuador yellow
        'blue': '#0052CC',        # Ecuador blue  
        'red': '#FF0000',         # Ecuador red
        'dark_yellow': '#E6C200',  # Darker yellow for contrast
        'dark_blue': '#003D99',    # Darker blue for contrast
        'dark_red': '#CC0000',     # Darker red for contrast
        'light_yellow': '#FFF5B3', # Light yellow for backgrounds
        'light_blue': '#B3D9FF',   # Light blue for backgrounds
        'light_red': '#FFB3B3',    # Light red for backgrounds
        'white': '#FFFFFF',
        'black': '#000000',
        'gray': '#666666',
        'light_gray': '#CCCCCC'
    }
    
    # Color palettes for different chart types
    PALETTES = {
        'primary': [COLORS['yellow'], COLORS['blue'], COLORS['red']],
        'extended': [
            COLORS['yellow'], COLORS['blue'], COLORS['red'],
            COLORS['dark_yellow'], COLORS['dark_blue'], COLORS['dark_red']
        ],
        'gradient_yellow': [COLORS['light_yellow'], COLORS['yellow'], COLORS['dark_yellow']],
        'gradient_blue': [COLORS['light_blue'], COLORS['blue'], COLORS['dark_blue']],
        'gradient_red': [COLORS['light_red'], COLORS['red'], COLORS['dark_red']],
        'monochrome': [COLORS['gray'], COLORS['black'], COLORS['light_gray']],
        'business': [COLORS['blue'], COLORS['dark_blue'], COLORS['yellow'], COLORS['red']]
    }
    
    @classmethod
    def get_color_palette(cls, name: str = 'primary', n_colors: int = 3) -> List[str]:
        """Get color palette by name"""
        palette = cls.PALETTES.get(name, cls.PALETTES['primary'])
        
        # Extend palette if needed
        if len(palette) < n_colors:
            # Cycle through existing colors
            extended_palette = []
            for i in range(n_colors):
                extended_palette.append(palette[i % len(palette)])
            return extended_palette
        
        return palette[:n_colors]
    
    @classmethod
    def create_custom_colormap(cls, name: str = 'ecuador') -> LinearSegmentedColormap:
        """Create custom colormap based on Ecuador colors"""
        if name == 'ecuador':
            colors = [cls.COLORS['yellow'], cls.COLORS['blue'], cls.COLORS['red']]
        elif name == 'ecuador_gradient':
            colors = [cls.COLORS['light_yellow'], cls.COLORS['yellow'], 
                     cls.COLORS['blue'], cls.COLORS['dark_blue']]
        else:
            colors = [cls.COLORS['yellow'], cls.COLORS['blue'], cls.COLORS['red']]
        
        return LinearSegmentedColormap.from_list(name, colors)

class ChartStyler:
    """Chart styling and formatting utilities"""
    
    def __init__(self, theme: Optional[EcuadorTheme] = None):
        self.theme = theme or EcuadorTheme()
        self.setup_style()
    
    def setup_style(self):
        """Setup matplotlib style for Ecuador theme"""
        try:
            # Set up custom style parameters
            plt.style.use('default')
            
            # Configure matplotlib parameters
            plt.rcParams.update({
                'figure.facecolor': self.theme.COLORS['white'],
                'axes.facecolor': self.theme.COLORS['white'],
                'axes.edgecolor': self.theme.COLORS['gray'],
                'axes.labelcolor': self.theme.COLORS['black'],
                'axes.axisbelow': True,
                'axes.grid': True,
                'axes.spines.left': True,
                'axes.spines.bottom': True,
                'axes.spines.top': False,
                'axes.spines.right': False,
                'grid.color': self.theme.COLORS['light_gray'],
                'grid.linewidth': 0.5,
                'text.color': self.theme.COLORS['black'],
                'xtick.color': self.theme.COLORS['gray'],
                'ytick.color': self.theme.COLORS['gray'],
                'legend.frameon': False,
                'font.size': 10,
                'axes.titlesize': 14,
                'axes.labelsize': 12,
                'xtick.labelsize': 10,
                'ytick.labelsize': 10,
                'legend.fontsize': 10,
                'font.family': 'Arial'
            })
            
            logger.info("Ecuador theme style configured")
            
        except Exception as e:
            logger.error(f"Error setting up style: {e}")
    
    def style_bar_chart(self, ax, title: str, colors: Optional[List[str]] = None) -> None:
        """Apply Ecuador theme styling to bar chart"""
        try:
            if colors is None:
                colors = self.theme.get_color_palette('primary')
            
            # Set title with Ecuador colors
            ax.set_title(title, fontsize=14, fontweight='bold', 
                        color=self.theme.COLORS['black'], pad=20)
            
            # Style bars
            for i, bar in enumerate(ax.patches):
                bar.set_color(colors[i % len(colors)])
                bar.set_edgecolor(self.theme.COLORS['white'])
                bar.set_linewidth(1)
            
            # Style axes
            ax.tick_params(axis='x', colors=self.theme.COLORS['gray'])
            ax.tick_params(axis='y', colors=self.theme.COLORS['gray'])
            
            # Add subtle grid
            ax.grid(True, alpha=0.3, color=self.theme.COLORS['light_gray'])
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        except Exception as e:
            logger.error(f"Error styling bar chart: {e}")
    
    def style_line_chart(self, ax, title: str, colors: Optional[List[str]] = None) -> None:
        """Apply Ecuador theme styling to line chart"""
        try:
            if colors is None:
                colors = self.theme.get_color_palette('primary')
            
            # Set title
            ax.set_title(title, fontsize=14, fontweight='bold', 
                        color=self.theme.COLORS['black'], pad=20)
            
            # Style lines
            for i, line in enumerate(ax.get_lines()):
                line.set_color(colors[i % len(colors)])
                line.set_linewidth(2.5)
                line.set_marker('o')
                line.set_markersize(6)
                line.set_markerfacecolor(colors[i % len(colors)])
                line.set_markeredgecolor(self.theme.COLORS['white'])
                line.set_markeredgewidth(1)
            
            # Style axes
            ax.tick_params(axis='x', colors=self.theme.COLORS['gray'])
            ax.tick_params(axis='y', colors=self.theme.COLORS['gray'])
            
            # Add grid
            ax.grid(True, alpha=0.3, color=self.theme.COLORS['light_gray'])
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        except Exception as e:
            logger.error(f"Error styling line chart: {e}")
    
    def style_pie_chart(self, ax, title: str, colors: Optional[List[str]] = None) -> None:
        """Apply Ecuador theme styling to pie chart"""
        try:
            if colors is None:
                colors = self.theme.get_color_palette('extended', 6)
            
            # Set title
            ax.set_title(title, fontsize=14, fontweight='bold', 
                        color=self.theme.COLORS['black'], pad=20)
            
            # Style pie slices
            for i, wedge in enumerate(ax.patches):
                wedge.set_facecolor(colors[i % len(colors)])
                wedge.set_edgecolor(self.theme.COLORS['white'])
                wedge.set_linewidth(2)
            
        except Exception as e:
            logger.error(f"Error styling pie chart: {e}")
    
    def add_ecuador_branding(self, fig, ax, subtitle: Optional[str] = None) -> None:
        """Add Ecuador branding elements to chart"""
        try:
            # Add subtle Ecuador flag colors as background accent
            fig.patch.set_facecolor(self.theme.COLORS['white'])
            
            # Add subtitle if provided
            if subtitle:
                fig.suptitle(subtitle, fontsize=10, color=self.theme.COLORS['gray'], 
                           y=0.02, ha='center')
            
            # Add Hive Ecuador watermark
            fig.text(0.99, 0.01, 'Hive Ecuador Pulse', 
                    fontsize=8, color=self.theme.COLORS['gray'], 
                    ha='right', va='bottom', alpha=0.7)
            
        except Exception as e:
            logger.error(f"Error adding Ecuador branding: {e}")
    
    def create_gradient_background(self, ax, direction: str = 'vertical') -> None:
        """Create gradient background using Ecuador colors"""
        try:
            # Create gradient from light yellow to light blue
            if direction == 'vertical':
                colors = [self.theme.COLORS['light_yellow'], self.theme.COLORS['light_blue']]
                ax.set_facecolor(colors[0])
                # Add gradient effect (simplified)
                ax.axhspan(ax.get_ylim()[0], ax.get_ylim()[1], 
                          color=colors[1], alpha=0.1, zorder=0)
            else:
                colors = [self.theme.COLORS['light_yellow'], self.theme.COLORS['light_blue']]
                ax.set_facecolor(colors[0])
                ax.axvspan(ax.get_xlim()[0], ax.get_xlim()[1], 
                          color=colors[1], alpha=0.1, zorder=0)
            
        except Exception as e:
            logger.error(f"Error creating gradient background: {e}")
    
    def format_currency_axis(self, ax, currency: str = 'HIVE', axis: str = 'y') -> None:
        """Format axis labels for currency display"""
        try:
            if axis == 'y':
                labels = ax.get_yticklabels()
                ax.set_yticklabels([f"{float(label.get_text()):.2f} {currency}" 
                                   for label in labels if label.get_text()])
            else:
                labels = ax.get_xticklabels()
                ax.set_xticklabels([f"{float(label.get_text()):.2f} {currency}" 
                                   for label in labels if label.get_text()])
            
        except Exception as e:
            logger.error(f"Error formatting currency axis: {e}")
    
    def add_value_labels(self, ax, chart_type: str = 'bar', format_as_currency: bool = False) -> None:
        """Add value labels to chart elements"""
        try:
            if chart_type == 'bar':
                for bar in ax.patches:
                    height = bar.get_height()
                    if format_as_currency:
                        label = f"{height:.2f} HIVE"
                    else:
                        label = f"{height:.0f}" if height == int(height) else f"{height:.1f}"
                    
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           label, ha='center', va='bottom', 
                           color=self.theme.COLORS['black'], fontsize=9)
            
        except Exception as e:
            logger.error(f"Error adding value labels: {e}")
    
    def create_comparison_chart_style(self, ax, title: str,                                    positive_color: Optional[str] = None,
                                    negative_color: Optional[str] = None) -> None:
        """Style charts that show comparisons with positive/negative values"""
        try:
            if positive_color is None:
                positive_color = self.theme.COLORS['blue']
            if negative_color is None:
                negative_color = self.theme.COLORS['red']
            
            # Set title
            ax.set_title(title, fontsize=14, fontweight='bold', 
                        color=self.theme.COLORS['black'], pad=20)
            
            # Style bars based on positive/negative values
            for bar in ax.patches:
                if bar.get_height() >= 0:
                    bar.set_color(positive_color)
                else:
                    bar.set_color(negative_color)
                bar.set_edgecolor(self.theme.COLORS['white'])
                bar.set_linewidth(1)
            
            # Add horizontal line at y=0
            ax.axhline(y=0, color=self.theme.COLORS['black'], linewidth=1, alpha=0.7)
            
            # Style axes
            ax.tick_params(axis='x', colors=self.theme.COLORS['gray'])
            ax.tick_params(axis='y', colors=self.theme.COLORS['gray'])
            
            # Add grid
            ax.grid(True, alpha=0.3, color=self.theme.COLORS['light_gray'])
            
            # Remove top and right spines
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        except Exception as e:
            logger.error(f"Error styling comparison chart: {e}")
    
    def get_chart_dimensions(self, chart_type: str = 'standard') -> Tuple[int, int]:
        """Get recommended chart dimensions for different types"""
        dimensions = {
            'standard': (10, 6),
            'wide': (12, 6),
            'tall': (8, 10),
            'square': (8, 8),
            'small': (6, 4),
            'instagram': (8, 8),  # Instagram square format
            'twitter': (12, 6),   # Twitter banner format
        }
        return dimensions.get(chart_type, dimensions['standard'])
    
    def save_chart(self, fig, filename: str, dpi: int = 300, 
                  format: str = 'png', transparent: bool = False) -> None:
        """Save chart with Ecuador theme optimizations"""
        try:
            fig.savefig(filename, 
                       dpi=dpi, 
                       format=format, 
                       bbox_inches='tight',
                       facecolor=self.theme.COLORS['white'] if not transparent else 'transparent',
                       edgecolor='none',
                       pad_inches=0.1)
            
            logger.info(f"Chart saved: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving chart: {e}")

class ThemeManager:
    """Manages different theme configurations"""
    
    def __init__(self):
        self.themes = {
            'ecuador': EcuadorTheme(),
            'dark_ecuador': self._create_dark_theme(),
            'minimal': self._create_minimal_theme()
        }
        self.current_theme = 'ecuador'
    
    def _create_dark_theme(self) -> EcuadorTheme:
        """Create dark variant of Ecuador theme"""
        dark_theme = EcuadorTheme()
        dark_theme.COLORS.update({
            'white': '#1a1a1a',
            'black': '#ffffff',
            'gray': '#cccccc',
            'light_gray': '#333333'
        })
        return dark_theme
    
    def _create_minimal_theme(self) -> EcuadorTheme:
        """Create minimal variant of Ecuador theme"""
        minimal_theme = EcuadorTheme()
        minimal_theme.COLORS.update({
            'yellow': '#666666',
            'blue': '#333333',
            'red': '#999999'
        })
        return minimal_theme
    
    def get_theme(self, name: Optional[str] = None) -> EcuadorTheme:
        """Get theme by name"""
        if name is None:
            name = self.current_theme
        return self.themes.get(name, self.themes['ecuador'])
    
    def set_theme(self, name: str) -> bool:
        """Set current theme"""
        if name in self.themes:
            self.current_theme = name
            return True
        return False
    
    def get_styler(self, theme_name: Optional[str] = None) -> ChartStyler:
        """Get chart styler for specified theme"""
        theme = self.get_theme(theme_name)
        return ChartStyler(theme)
