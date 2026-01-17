import json
import os
from datetime import datetime

class ThemeManager:
    def __init__(self):
        self.current_theme = "light"
        self.theme_file = "user_theme.json"
        
        # Define themes matching the exact aesthetic shown
        self.themes = {
            'light': {
                'name': 'Light',
                'colors': {
                    'primary': '#4A90E2',  # Modern blue
                    'secondary': '#7B68EE',  # Soft purple
                    'background': '#F5F5F5',  # Light grey background
                    'surface': '#FFFFFF',  # Pure white for cards
                    'text': '#2C3E50',  # Dark blue-gray text
                    'text_secondary': '#7F8C8D',  # Medium gray text
                    'border': '#000000',  # Black border for white theme
                    'success': '#27AE60',  # Green
                    'warning': '#F39C12',  # Orange
                    'error': '#E74C3C',  # Red
                    'glass': 'rgba(255, 255, 255, 0.95)',  # White glass
                    'glass_border': 'rgba(0, 0, 0, 0.2)'  # Black tint
                }
            },
            'dark': {
                'name': 'Dark',
                'colors': {
                    'primary': '#4A90E2',  # Modern blue
                    'secondary': '#7B68EE',  # Soft purple
                    'background': '#1A1A2E',  # Deep blue-black
                    'surface': '#16213E',  # Dark blue surface
                    'text': '#E8E8E8',  # Light gray text
                    'text_secondary': '#A8A8A8',  # Medium gray text
                    'border': '#3A3A5C',  # Dark blue border
                    'success': '#27AE60',  # Green
                    'warning': '#F39C12',  # Orange
                    'error': '#E74C3C',  # Red
                    'glass': 'rgba(22, 33, 62, 0.95)',  # Dark blue glass
                    'glass_border': 'rgba(74, 144, 226, 0.3)'  # Blue tint
                }
            }
        }
        
        # Load saved theme
        self._load_theme()
    
    def _load_theme(self):
        """Load user's theme preference"""
        try:
            if os.path.exists(self.theme_file):
                with open(self.theme_file, 'r') as f:
                    data = json.load(f)
                    self.current_theme = data.get('theme', 'light')
                    print(f"[THEME] Loaded theme: {self.current_theme}")
        except Exception as e:
            print(f"[THEME] Could not load theme preference: {e}")
            self.current_theme = 'light'
    
    def _save_theme(self):
        """Save user's theme preference"""
        try:
            with open(self.theme_file, 'w') as f:
                json.dump({'theme': self.current_theme, 'last_updated': datetime.now().isoformat()}, f, indent=2)
                print(f"[THEME] Saved theme preference: {self.current_theme}")
        except Exception as e:
            print(f"[THEME] Could not save theme preference: {e}")
    
    def get_available_themes(self):
        """Get list of available themes"""
        return list(self.themes.keys())
    
    def get_current_theme(self):
        """Get current active theme"""
        return self.current_theme
    
    def get_theme_colors(self, theme_name=None):
        """Get color scheme for a specific theme"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name in self.themes:
            return self.themes[theme_name]['colors']
        else:
            return self.themes['light']['colors']  # Default to light
    
    def set_theme(self, theme_name):
        """Set active theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._save_theme()
            print(f"[THEME] Switched to theme: {theme_name}")
            return True
        else:
            print(f"[THEME] Unknown theme: {theme_name}")
            return False
    
    def get_theme_css(self, theme_name=None):
        """Generate complete CSS for theme switching"""
        colors = self.get_theme_colors(theme_name)
        
        if theme_name is None:
            theme_name = self.current_theme
        
        css = f"""
        body {{
            background: {colors['background']};
            color: {colors['text']};
            transition: all 0.3s ease;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        /* Glass morphism containers */
        .glass-morphism {{
            background: {colors['glass']};
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 2px solid {colors['glass_border']};
            border-radius: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        /* Video container */
        .video-container {{
            background: {colors['surface']};
            border: 2px solid {colors['border']};
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        }}
        
        /* Main containers */
        .main-container {{
            background: {colors['background']};
            transition: all 0.3s ease;
        }}
        
        /* Theme-aware text */
        .theme-text {{
            color: {colors['text']} !important;
            transition: color 0.3s ease;
        }}
        
        /* Theme-aware backgrounds */
        .theme-bg {{
            background: {colors['surface']};
            transition: background-color 0.3s ease;
        }}
        
        /* Theme-aware borders */
        .theme-border {{
            border: 2px solid {colors['border']};
            transition: border-color 0.3s ease;
        }}
        
        /* Feature cards */
        .feature-card {{
            background: {colors['surface']};
            border: 2px solid {colors['border']};
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }}
        
        /* Buttons */
        .btn-primary {{
            background: {colors['primary']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        
        .btn-primary:hover {{
            background: {colors['secondary']};
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
        }}
        
        .btn-secondary {{
            background: {colors['surface']};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        
        /* Text colors */
        .text-primary {{
            color: {colors['text']};
            transition: color 0.3s ease;
        }}
        
        .text-secondary {{
            color: {colors['text_secondary']};
            transition: color 0.3s ease;
        }}
        
        /* Override Tailwind classes */
        .text-white {{
            color: {colors['text']} !important;
        }}
        
        .text-gray-200, .text-gray-300, .text-gray-600 {{
            color: {colors['text_secondary']} !important;
        }}
        
        /* Background overrides */
        .bg-white, .bg-gray-700, .bg-gray-800, .bg-gray-500 {{
            background: {colors['surface']} !important;
        }}
        
        .bg-white.bg-opacity-20 {{
            background: {colors['glass']} !important;
        }}
        
        /* Border overrides */
        .border-gray-600, .border-gray-800 {{
            border: 2px solid {colors['border']} !important;
            border-color: {colors['border']} !important;
        }}
        
        /* Status colors */
        .success {{
            color: {colors['success']};
        }}
        
        .warning {{
            color: {colors['warning']};
        }}
        
        .error {{
            color: {colors['error']};
        }}
        
        /* Icon colors */
        .text-blue-400 {{
            color: {colors['primary']} !important;
        }}
        
        .text-green-400 {{
            color: {colors['success']} !important;
        }}
        
        .text-red-400 {{
            color: {colors['error']} !important;
        }}
        
        .text-yellow-400 {{
            color: {colors['warning']} !important;
        }}
        
        /* Button backgrounds */
        .bg-green-500, .bg-green-600 {{
            background: {colors['success']} !important;
            border: 1px solid {colors['success']} !important;
        }}
        
        .bg-red-500, .bg-red-600 {{
            background: {colors['error']} !important;
            border: 1px solid {colors['error']} !important;
        }}
        
        .bg-blue-500, .bg-blue-600 {{
            background: {colors['primary']} !important;
            border: 1px solid {colors['primary']} !important;
        }}
        
        .bg-yellow-500, .bg-yellow-600 {{
            background: {colors['warning']} !important;
            border: 1px solid {colors['warning']} !important;
        }}
        
        /* Hover states */
        .hover\\:bg-green-600:hover {{
            background: {colors['success']} !important;
            opacity: 0.8;
        }}
        
        .hover\\:bg-red-600:hover {{
            background: {colors['error']} !important;
            opacity: 0.8;
        }}
        
        .hover\\:bg-blue-600:hover {{
            background: {colors['secondary']} !important;
            opacity: 0.8;
        }}
        
        .hover\\:bg-yellow-600:hover {{
            background: {colors['warning']} !important;
            opacity: 0.8;
        }}
        """
        
        return css

# Global theme manager
theme_manager = ThemeManager()

def initialize_theme_manager():
    """Initialize the theme manager"""
    return theme_manager

def set_theme(theme_name):
    """Set theme globally"""
    return theme_manager.set_theme(theme_name)

def get_current_theme():
    """Get current theme"""
    return theme_manager.get_current_theme()

def get_theme_css():
    """Get CSS for current theme"""
    return theme_manager.get_theme_css()

def get_available_themes():
    """Get list of available themes"""
    return theme_manager.get_available_themes()
