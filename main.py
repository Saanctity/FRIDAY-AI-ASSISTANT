"""
JARVIS AI Assistant - Main Launcher
Choose between Desktop Application and API Server
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print JARVIS banner"""
    banner = """
    ░░░░░██╗░█████╗░██████╗░██╗░░░██╗██╗░██████╗
    ░░░░░██║██╔══██╗██╔══██╗██║░░░██║██║██╔════╝
    ░░░░░██║███████║██████╔╝╚██╗░██╔╝██║╚█████╗░
    ██╗░░██║██╔══██║██╔══██╗░╚████╔╝░██║░╚═══██╗
    ╚█████╔╝██║░░██║██║░░██║░░╚██╔╝░░██║██████╔╝
    ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝╚═════╝░
    
    Just A Rather Very Intelligent System
    Advanced AI Assistant by Tony Stark Industries
    """
    print(banner)
    print("=" * 60)

def check_environment():
    """Check if .env file exists"""
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("Please create a .env file with your API keys:")
        print("""
GEMINI_API_KEY=your_gemini_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
PICOVOICE_ACCESS_KEY=your_picovoice_key_here (optional)
        """)
        return False
    return True

def run_desktop():
    """Launch desktop application"""
    print("🖥️  Launching JARVIS Desktop Application...")
    try:
        from frontend.desktop.main import main
        main()
    except Exception as e:
        print(f"❌ Failed to launch desktop app: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

def run_server():
    """Launch API server"""
    print("🌐 Launching JARVIS API Server...")
    try:
        import uvicorn
        from backend.main import app
        
        print("Starting server on http://localhost:8000")
        print("API documentation available at http://localhost:8000/docs")
        
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to launch server: {e}")
        print("Make sure FastAPI and uvicorn are installed: pip install fastapi uvicorn")

def interactive_launcher():
    """Interactive launcher menu"""
    print("\n🤖 JARVIS Launcher")
    print("-" * 20)
    print("1. 🖥️  Desktop Application (Recommended)")
    print("2. 🌐 API Server")
    print("3. 🔧 Check System Requirements")
    print("4. ❌ Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                run_desktop()
                break
            elif choice == "2":
                run_server()
                break
            elif choice == "3":
                check_system_requirements()
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def check_system_requirements():
    """Check system requirements and dependencies"""
    print("\n🔍 Checking System Requirements...")
    print("-" * 35)
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} (requires 3.8+)")
    
    # Check core dependencies
    deps_status = {
        "google-generativeai": False,
        "assemblyai": False,
        "elevenlabs": False,
        "fastapi": False,
        "uvicorn": False,
        "python-dotenv": False,
        "Pillow": False,
    }
    
    optional_deps = {
        "cv2 (opencv-python)": False,
        "pyaudio": False,
        "pvporcupine": False,
        "webrtcvad": False,
    }
    
    # Check core dependencies
    for dep in deps_status:
        try:
            if dep == "google-generativeai":
                import google.generativeai
            elif dep == "assemblyai":
                import assemblyai
            elif dep == "elevenlabs":
                from elevenlabs.client import ElevenLabs
            elif dep == "fastapi":
                import fastapi
            elif dep == "uvicorn":
                import uvicorn
            elif dep == "python-dotenv":
                from dotenv import load_dotenv
            elif dep == "Pillow":
                from PIL import Image
            
            deps_status[dep] = True
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
    
    # Check optional dependencies
    print("\nOptional Dependencies:")
    for dep in optional_deps:
        try:
            if "opencv" in dep:
                import cv2
            elif "pyaudio" in dep:
                import pyaudio
            elif "pvporcupine" in dep:
                import pvporcupine
            elif "webrtcvad" in dep:
                import webrtcvad
            
            optional_deps[dep] = True
            print(f"✅ {dep}")
        except ImportError:
            print(f"⚠️  {dep}")
    
    # Check .env file
    print(f"\nConfiguration:")
    if check_environment():
        print("✅ .env file found")
    else:
        print("❌ .env file missing")
    
    # Summary
    core_missing = [dep for dep, status in deps_status.items() if not status]
    
    if not core_missing:
        print(f"\n🎉 All core requirements satisfied!")
        print("You can run both Desktop and Server modes.")
    else:
        print(f"\n⚠️  Missing core dependencies: {', '.join(core_missing)}")
        print("Install them with: pip install -r requirements.txt")
    
    input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    print_banner()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="JARVIS AI Assistant Launcher")
    parser.add_argument(
        "--mode", 
        choices=["desktop", "server", "check"], 
        help="Launch mode: desktop (GUI), server (API), or check (requirements)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Server host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Server port (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Check environment first
    if not check_environment() and args.mode != "check":
        return
    
    # Handle command line arguments
    if args.mode == "desktop":
        run_desktop()
    elif args.mode == "server":
        print(f"🌐 Launching JARVIS API Server on {args.host}:{args.port}...")
        try:
            import uvicorn
            uvicorn.run(
                "backend.main:app",
                host=args.host,
                port=args.port,
                reload=True,
                log_level="info"
            )
        except Exception as e:
            print(f"❌ Server launch failed: {e}")
    elif args.mode == "check":
        check_system_requirements()
    else:
        # Interactive mode
        interactive_launcher()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 JARVIS shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()