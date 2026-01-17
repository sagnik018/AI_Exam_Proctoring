import json
import os
from datetime import datetime

class ThemeManager:
    def __init__(self):
        self.themes = {
            'light': {
                'name': 'Light Theme',
                'primary_bg': '#ffffff',
                'secondary_bg': '#f8f9fa',
                'text_color': '#212529',
                'border_color': '#dee2e6',
                'button_primary': '#007bff',
                'button_secondary': '#6c757d',
                'glass_bg': 'rgba(255, 255, 255, 0.1)',
                'glass_border': 'rgba(0, 0, 0, 0.1)',
                'gradient_start': '#f8f9fa',
                'gradient_end': '#e9ecef'
            },
            'dark': {
                'name': 'Dark Theme',
                'primary_bg': '#1a1a1a',
                'secondary_bg': '#2d3748',
                'text_color': '#ffffff',
                'border_color': '#495057',
                'button_primary': '#0d6efd',
                'button_secondary': '#6c757d',
                'glass_bg': 'rgba(255, 255, 255, 0.05)',
                'glass_border': 'rgba(255, 255, 255, 0.1)',
                'gradient_start': '#2d3748',
                'gradient_end': '#1a1a1a'
            },
            'blue': {
                'name': 'Blue Theme',
                'primary_bg': '#0f172a',
                'secondary_bg': '#1e293b',
                'text_color': '#f8fafc',
                'border_color': '#334155',
                'button_primary': '#3b82f6',
                'button_secondary': '#64748b',
                'glass_bg': 'rgba(59, 130, 246, 0.1)',
                'glass_border': 'rgba(59, 130, 246, 0.2)',
                'gradient_start': '#1e293b',
                'gradient_end': '#0f172a'
            },
            'purple': {
                'name': 'Purple Theme',
                'primary_bg': '#581c87',
                'secondary_bg': '#6d28d9',
                'text_color': '#f8fafc',
                'border_color': '#9333ea',
                'button_primary': '#8b5cf6',
                'button_secondary': '#a855f7',
                'glass_bg': 'rgba(139, 92, 246, 0.1)',
                'glass_border': 'rgba(139, 92, 246, 0.2)',
                'gradient_start': '#6d28d9',
                'gradient_end': '#581c87'
            }
        }
        
        self.current_theme = 'light'
        self.theme_file = 'user_theme.json'
        self.custom_themes = {}
        
        # Load saved theme preference
        self._load_theme_preference()
    
    def _load_theme_preference(self):
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
    
    def _save_theme_preference(self):
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
            return self.themes[theme_name]
        elif theme_name in self.custom_themes:
            return self.custom_themes[theme_name]
        else:
            return self.themes['light']  # Default to light
    
    def set_theme(self, theme_name):
        """Set active theme"""
        if theme_name in self.themes or theme_name in self.custom_themes:
            self.current_theme = theme_name
            self._save_theme_preference()
            print(f"[THEME] Switched to theme: {theme_name}")
            return True
        else:
            print(f"[THEME] Unknown theme: {theme_name}")
            return False
    
    def create_custom_theme(self, name, colors):
        """Create a custom theme"""
        self.custom_themes[name] = {
            'name': name,
            'primary_bg': colors.get('primary_bg', '#ffffff'),
            'secondary_bg': colors.get('secondary_bg', '#f8f9fa'),
            'text_color': colors.get('text_color', '#212529'),
            'border_color': colors.get('border_color', '#dee2e6'),
            'button_primary': colors.get('button_primary', '#007bff'),
            'button_secondary': colors.get('button_secondary', '#6c757d'),
            'glass_bg': colors.get('glass_bg', 'rgba(255, 255, 255, 0.1)'),
            'glass_border': colors.get('glass_border', 'rgba(0, 0, 0, 0.1)'),
            'gradient_start': colors.get('gradient_start', '#f8f9fa'),
            'gradient_end': colors.get('gradient_end', '#e9ecef')
        }
        print(f"[THEME] Created custom theme: {name}")
        return True
    
    def get_css_variables(self, theme_name=None):
        """Generate CSS variables for theme"""
        colors = self.get_theme_colors(theme_name)
        
        css_vars = f"""
        :root {{
            --theme-name: '{colors['name']}';
            --primary-bg: {colors['primary_bg']};
            --secondary-bg: {colors['secondary_bg']};
            --text-color: {colors['text_color']};
            --border-color: {colors['border_color']};
            --button-primary: {colors['button_primary']};
            --button-secondary: {colors['button_secondary']};
            --glass-bg: {colors['glass_bg']};
            --glass-border: {colors['glass_border']};
            --gradient-start: {colors['gradient_start']};
            --gradient-end: {colors['gradient_end']};
        }}
        """
        
        return css_vars
    
    def get_theme_css(self, theme_name=None):
        """Generate complete CSS for theme switching"""
        colors = self.get_theme_colors(theme_name)
        
        css = f"""
        body {{
            background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
            color: var(--text-color);
        }}
        
        .glass-morphism {{
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
        }}
        
        .btn-primary {{
            background-color: var(--button-primary);
            color: white;
        }}
        
        .btn-secondary {{
            background-color: var(--button-secondary);
            color: white;
        }}
        
        .text-primary {{
            color: var(--text-color);
        }}
        
        .border-theme {{
            border-color: var(--border-color);
        }}
        """
        
        return css
    
    def auto_detect_theme(self):
        """Auto-detect system theme preference"""
        try:
            import platform
            system = platform.system()
            
            # Check for system dark mode preference
            if system == 'Darwin':  # macOS
                result = os.popen('defaults read -g AppleInterfaceStyle 2>/dev/null').read()
                if 'Dark' in result:
                    return 'dark'
            elif system == 'Windows':
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\microsoft\windows\currentversion\themes\personalize')
                    value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                    if value == 0:
                        return 'dark'
                except:
                    pass
            elif system == 'Linux':
                # Check for GNOME/Qt dark mode
                if os.path.exists('~/.config/gtk-3.0/settings.ini'):
                    with open('~/.config/gtk-3.0/settings.ini', 'r') as f:
                        if 'gtk-application-prefer-dark-theme=1' in f.read():
                            return 'dark'
        
        except Exception as e:
            print(f"[THEME] Auto-detection failed: {e}")
        
        return 'light'  # Default
    
    def get_theme_info(self):
        """Get comprehensive theme information"""
        current_colors = self.get_theme_colors()
        
        return {
            'current_theme': self.current_theme,
            'available_themes': list(self.themes.keys()),
            'custom_themes': list(self.custom_themes.keys()),
            'current_colors': current_colors,
            'css_variables': self.get_css_variables(),
            'theme_css': self.get_theme_css()
        }

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

def create_custom_theme(name, colors):
    """Create a custom theme"""
    return theme_manager.create_custom_theme(name, colors)
