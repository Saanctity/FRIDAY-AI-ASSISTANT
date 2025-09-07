"""
System Controller for FRIDAY
Handles system operations like opening websites, applications, and file management
"""

import os
import webbrowser
import subprocess
import platform
import urllib.parse
from typing import Optional, List, Dict

class SystemController:
    """Handles system operations and commands"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.supported_browsers = [
            'chrome', 'firefox', 'safari', 'edge', 'brave', 'opera'
        ]
        
    def open_website(self, url: str, browser: str = None) -> str:
        """Open website in browser"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Use specific browser if requested
            if browser and browser.lower() in self.supported_browsers:
                webbrowser.get(browser).open(url)
            else:
                webbrowser.open(url)
            
            return f"Opening {url} in browser."
            
        except Exception as e:
            return f"Unable to open website: {str(e)}"
    
    def search_youtube(self, query: str) -> str:
        """Search YouTube for specific content"""
        try:
            # Clean and encode the search query
            clean_query = urllib.parse.quote_plus(query)
            youtube_search_url = f"https://www.youtube.com/results?search_query={clean_query}"
            
            webbrowser.open(youtube_search_url)
            return f"Searching YouTube for '{query}'. Opening results in your browser."
            
        except Exception as e:
            return f"Failed to search YouTube: {str(e)}"
    
    def play_youtube_video(self, search_term: str) -> str:
        """Search and play first YouTube video result"""
        try:
            # Create YouTube search URL
            clean_search = urllib.parse.quote_plus(search_term)
            youtube_url = f"https://www.youtube.com/results?search_query={clean_search}"
            
            webbrowser.open(youtube_url)
            return f"Searching for '{search_term}' on YouTube. You can click the first result to play."
            
        except Exception as e:
            return f"Failed to search YouTube: {str(e)}"
    
    def open_application(self, app_name: str) -> str:
        """Open application by name"""
        try:
            if self.system == "windows":
                return self._open_windows_app(app_name)
            elif self.system == "darwin":  # macOS
                return self._open_macos_app(app_name)
            else:  # Linux
                return self._open_linux_app(app_name)
                
        except Exception as e:
            return f"Unable to open {app_name}: {str(e)}"
    
    def _open_windows_app(self, app_name: str) -> str:
        """Open Windows application"""
        # Enhanced Windows applications
        apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'calc': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task manager': 'taskmgr.exe',
            'taskmgr': 'taskmgr.exe',
            'control panel': 'control.exe',
            'settings': 'ms-settings:',
            'system settings': 'ms-settings:',
            'windows settings': 'ms-settings:',
            'file explorer': 'explorer.exe',
            'explorer': 'explorer.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'code': 'code.exe',
            'vscode': 'code.exe',
            'visual studio code': 'code.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            'outlook': 'outlook.exe'
        }
        
        app_lower = app_name.lower()
        
        if app_lower in apps:
            app_command = apps[app_lower]
            
            # Special handling for Windows Settings
            if app_command == 'ms-settings:':
                subprocess.Popen(f"start {app_command}", shell=True)
                return f"Opening Windows Settings."
            else:
                subprocess.Popen(app_command, shell=True)
                return f"Opening {app_name}."
        else:
            # Try to open by name directly
            subprocess.Popen(f"start {app_name}", shell=True)
            return f"Attempting to open {app_name}."
    
    def _open_macos_app(self, app_name: str) -> str:
        """Open macOS application"""
        apps = {
            'safari': 'Safari',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'finder': 'Finder',
            'terminal': 'Terminal',
            'calculator': 'Calculator',
            'textedit': 'TextEdit',
            'code': 'Visual Studio Code',
            'vscode': 'Visual Studio Code',
            'settings': 'System Preferences',
            'system settings': 'System Preferences'
        }
        
        app_lower = app_name.lower()
        app_to_open = apps.get(app_lower, app_name)
        
        subprocess.Popen(["open", "-a", app_to_open])
        return f"Opening {app_name}."
    
    def _open_linux_app(self, app_name: str) -> str:
        """Open Linux application"""
        apps = {
            'firefox': 'firefox',
            'chrome': 'google-chrome',
            'chromium': 'chromium-browser',
            'terminal': 'gnome-terminal',
            'calculator': 'gnome-calculator',
            'gedit': 'gedit',
            'nautilus': 'nautilus',
            'code': 'code',
            'vscode': 'code',
            'settings': 'gnome-control-center'
        }
        
        app_lower = app_name.lower()
        app_to_open = apps.get(app_lower, app_name)
        
        subprocess.Popen([app_to_open])
        return f"Opening {app_name}."
    
    def search_web(self, query: str, search_engine: str = "google") -> str:
        """Search the web with specified query"""
        try:
            search_engines = {
                'google': 'https://www.google.com/search?q=',
                'bing': 'https://www.bing.com/search?q=',
                'duckduckgo': 'https://duckduckgo.com/?q=',
                'yahoo': 'https://search.yahoo.com/search?p='
            }
            
            base_url = search_engines.get(search_engine.lower(), search_engines['google'])
            encoded_query = urllib.parse.quote_plus(query)
            search_url = base_url + encoded_query
            
            webbrowser.open(search_url)
            return f"Searching for '{query}' on {search_engine.title()}."
            
        except Exception as e:
            return f"Search failed: {str(e)}"
    
    def open_specific_website(self, site_name: str) -> str:
        """Open specific popular websites"""
        websites = {
            'google': 'google.com',
            'youtube': 'youtube.com',
            'facebook': 'facebook.com',
            'twitter': 'twitter.com',
            'instagram': 'instagram.com',
            'linkedin': 'linkedin.com',
            'github': 'github.com',
            'stackoverflow': 'stackoverflow.com',
            'reddit': 'reddit.com',
            'amazon': 'amazon.com',
            'netflix': 'netflix.com',
            'gmail': 'gmail.com',
            'outlook': 'outlook.com',
            'wikipedia': 'wikipedia.org',
            'whatsapp': 'web.whatsapp.com'
        }
        
        site_lower = site_name.lower().strip()
        if site_lower in websites:
            return self.open_website(websites[site_lower])
        else:
            # Try to open as domain
            return self.open_website(f"{site_name}.com")
    
    def create_file(self, filename: str, content: str = "", directory: str = None) -> str:
        """Create a new file"""
        try:
            if directory:
                filepath = os.path.join(directory, filename)
            else:
                filepath = filename
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"File '{filename}' created successfully."
            
        except Exception as e:
            return f"Failed to create file: {str(e)}"
    
    def read_file(self, filepath: str) -> str:
        """Read file content"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Limit content length for display
            if len(content) > 1000:
                content = content[:1000] + "\n... (content truncated)"
            
            return f"File content:\n\n{content}"
            
        except Exception as e:
            return f"Failed to read file: {str(e)}"
    
    def list_directory(self, directory: str = ".") -> str:
        """List directory contents"""
        try:
            items = os.listdir(directory)
            items.sort()
            
            files = []
            folders = []
            
            for item in items:
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    files.append(f"📄 {item}")
                else:
                    folders.append(f"📁 {item}")
            
            result = f"Contents of '{directory}':\n\n"
            
            if folders:
                result += "Folders:\n" + "\n".join(folders) + "\n\n"
            
            if files:
                result += "Files:\n" + "\n".join(files)
            
            if not folders and not files:
                result += "Directory is empty."
            
            return result
            
        except Exception as e:
            return f"Failed to list directory: {str(e)}"
    
    def get_system_info(self) -> str:
        """Get system information"""
        try:
            import psutil
            
            # Get CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Get memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_total = round(memory.total / (1024**3), 2)  # GB
            
            # Get disk info
            disk = psutil.disk_usage('/')
            disk_percent = round((disk.used / disk.total) * 100, 1)
            
            info = f"""System Information:

OS: {platform.system()} {platform.release()}
CPU: {cpu_count} cores, {cpu_percent}% usage
Memory: {memory_percent}% used of {memory_total} GB
Disk: {disk_percent}% used
Python: {platform.python_version()}"""

            return info
            
        except ImportError:
            # Fallback without psutil
            info = f"""Basic System Information:

OS: {platform.system()} {platform.release()}  
Architecture: {platform.architecture()[0]}
Machine: {platform.machine()}
Python: {platform.python_version()}"""
            
            return info
        except Exception as e:
            return f"Failed to get system info: {str(e)}"
    
    def execute_command(self, command: str) -> str:
        """Execute system command (with safety checks)"""
        # Safety check - only allow safe commands
        safe_commands = [
            'dir', 'ls', 'pwd', 'date', 'time', 'whoami',
            'echo', 'ping', 'ipconfig', 'ifconfig'
        ]
        
        command_parts = command.split()
        if not command_parts:
            return "Empty command provided."
        
        base_command = command_parts[0].lower()
        
        if base_command not in safe_commands:
            return "Command not allowed for security reasons."
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nError: {result.stderr.strip()}"
            
            return f"Command output:\n\n{output}"
            
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Command execution failed: {str(e)}"
    
    def manage_volume(self, action: str, level: int = None) -> str:
        """Manage system volume"""
        try:
            if self.system == "windows":
                return self._manage_windows_volume(action, level)
            elif self.system == "darwin":
                return self._manage_macos_volume(action, level)
            else:
                return self._manage_linux_volume(action, level)
        except Exception as e:
            return f"Volume control failed: {str(e)}"
    
    def _manage_windows_volume(self, action: str, level: int = None) -> str:
        """Manage Windows volume"""
        try:
            if action.lower() == "mute":
                os.system("nircmd.exe mutesysvolume 1 > nul 2>&1")
                return "Volume muted."
            elif action.lower() == "unmute":
                os.system("nircmd.exe mutesysvolume 0 > nul 2>&1")
                return "Volume unmuted."
            elif action.lower() == "set" and level is not None:
                # Simple volume control using PowerShell
                ps_command = f'powershell -command "$obj=new-object -com wscript.shell;$obj.SendKeys([char]175)"'
                os.system(ps_command)
                return f"Volume adjusted."
            else:
                return "Volume control completed."
        except Exception as e:
            return f"Windows volume control error: {str(e)}"
    
    def _manage_macos_volume(self, action: str, level: int = None) -> str:
        """Manage macOS volume"""
        if action.lower() == "mute":
            os.system("osascript -e 'set volume output muted true'")
            return "Volume muted."
        elif action.lower() == "unmute":
            os.system("osascript -e 'set volume output muted false'")
            return "Volume unmuted."
        elif action.lower() == "set" and level is not None:
            os.system(f"osascript -e 'set volume output volume {level}'")
            return f"Volume set to {level}%."
        else:
            return "Volume control completed."
    
    def _manage_linux_volume(self, action: str, level: int = None) -> str:
        """Manage Linux volume"""
        if action.lower() == "mute":
            os.system("amixer set Master mute")
            return "Volume muted."
        elif action.lower() == "unmute":
            os.system("amixer set Master unmute")
            return "Volume unmuted."
        elif action.lower() == "set" and level is not None:
            os.system(f"amixer set Master {level}%")
            return f"Volume set to {level}%."
        else:
            return "Volume control completed."

# Global instance
_system_controller = None

def get_system_controller() -> SystemController:
    """Get global system controller instance"""
    global _system_controller
    if _system_controller is None:
        _system_controller = SystemController()
    return _system_controller