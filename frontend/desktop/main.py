"""
JARVIS Desktop Application - Main Entry Point
Launch the desktop GUI application
"""

import sys
import os
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    # Core dependencies
    try:
        import google.generativeai
    except ImportError:
        missing_deps.append("google-generativeai")
    
    try:
        import assemblyai
    except ImportError:
        missing_deps.append("assemblyai")
    
    try:
        from elevenlabs.client import ElevenLabs
    except ImportError:
        missing_deps.append("elevenlabs")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_deps.append("python-dotenv")
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        missing_deps.append("Pillow")
    
    # Optional dependencies
    optional_deps = []
    
    try:
        import cv2
    except ImportError:
        optional_deps.append("opencv-python (camera features will be disabled)")
    
    try:
        import pvporcupine
        import pyaudio
        import webrtcvad
    except ImportError:
        optional_deps.append("pvporcupine, pyaudio, webrtcvad (voice features will be limited)")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install them using:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    if optional_deps:
        print("⚠️ Optional dependencies missing:")
        for dep in optional_deps:
            print(f"   - {dep}")
        print("\nSome features will be limited. Install optional dependencies for full functionality.")
    
    return True

def check_environment():
    """Check environment variables"""
    from backend.config.settings import get_settings
    
    try:
        settings = get_settings()
        
        missing_keys = []
        if not settings.gemini_api_key:
            missing_keys.append("GEMINI_API_KEY")
        if not settings.assemblyai_api_key:
            missing_keys.append("ASSEMBLYAI_API_KEY")
        if not settings.elevenlabs_api_key:
            missing_keys.append("ELEVENLABS_API_KEY")
        
        if missing_keys:
            print("❌ Missing required API keys:")
            for key in missing_keys:
                print(f"   - {key}")
            print("\nPlease add them to your .env file")
            return False
        
        optional_keys = []
        if not settings.picovoice_access_key:
            optional_keys.append("PICOVOICE_ACCESS_KEY (wake word detection will be disabled)")
        
        if optional_keys:
            print("⚠️ Optional API keys missing:")
            for key in optional_keys:
                print(f"   - {key}")
        
        print("✅ Environment configuration valid")
        return True
        
    except Exception as e:
        print(f"❌ Environment check failed: {e}")
        return False

def main():
    """Main entry point for JARVIS Desktop"""
    print("🚀 Starting JARVIS Desktop Application...")
    print("=" * 50)
    
    try:
        # Check dependencies
        print("🔍 Checking dependencies...")
        if not check_dependencies():
            input("Press Enter to exit...")
            return
        
        # Check environment
        print("\n🔍 Checking environment configuration...")
        if not check_environment():
            input("Press Enter to exit...")
            return
        
        print("\n✅ All checks passed!")
        print("🤖 Initializing JARVIS...")
        
        # Import and run GUI
        from frontend.desktop.gui.main_window import FRIDAYMainWindow
        
        # Create and run application
        app = FRIDAYMainWindow()
        
        print("🎯 JARVIS Desktop is ready!")
        print("=" * 50)
        
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Application interrupted by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed correctly.")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
    finally:
        print("\n👋 JARVIS Desktop shutting down...")

if __name__ == "__main__":
    main()