"""
JARVIS Setup Script
Automated setup and configuration for JARVIS AI Assistant
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"🤖 {text}")
    print("=" * 60)

def run_command(command, description):
    """Run command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def create_env_file():
    """Create .env file template"""
    env_template = """# JARVIS AI Assistant Configuration
# Copy this file to .env and fill in your API keys

# Required API Keys
GEMINI_API_KEY=your_gemini_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional API Keys
PICOVOICE_ACCESS_KEY=your_picovoice_access_key_here

# Server Configuration
JARVIS_HOST=localhost
JARVIS_PORT=8000
JARVIS_DEBUG=False

# Audio Configuration  
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
VAD_AGGRESSIVENESS=3
SILENCE_DURATION=1.5

# Voice Configuration
ELEVENLABS_VOICE_ID=kdmDKE6EkgrWrrykO9Qt
WAKE_WORD_FILE=assets/audio/friday_windows_2024-08-28_v3_0_0.ppn

# UI Configuration
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800

# AI Configuration
GEMINI_MODEL=gemini-1.5-flash
TTS_MODEL=eleven_multilingual_v2
CONVERSATION_HISTORY_LIMIT=20
MAX_RECORDING_DURATION=10

# Feature Toggles
ENABLE_WAKE_WORD=True
ENABLE_VIDEO=True
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env template...")
        with open(env_file, "w") as f:
            f.write(env_template)
        print("✅ .env template created")
        print("⚠️  Please edit .env and add your API keys!")
        return False
    else:
        print("✅ .env file already exists")
        return True

def create_directories():
    """Create required directories"""
    directories = [
        "assets",
        "assets/audio", 
        "assets/images",
        "assets/temp",
        "backend/config",
        "backend/core",
        "backend/api",
        "backend/api/routes",
        "backend/services", 
        "backend/utils",
        "frontend/desktop",
        "frontend/desktop/gui",
        "frontend/desktop/gui/components",
        "frontend/web",
        "shared",
        "shared/models",
        "tests",
        "tests/backend",
        "tests/frontend"
    ]
    
    print("📁 Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if any(part in directory for part in ["backend", "frontend", "shared"]):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Directory structure created")

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Not in a virtual environment!")
        create_venv = input("Create virtual environment? (y/n): ").lower().strip() == 'y'
        if create_venv:
            if not run_command("python -m venv venv", "Creating virtual environment"):
                return False
            
            # Activate virtual environment
            if os.name == 'nt':  # Windows
                activate_cmd = "venv\\Scripts\\activate && pip install -r requirements.txt"
            else:  # Unix/Linux/Mac
                activate_cmd = "source venv/bin/activate && pip install -r requirements.txt"
            
            print("🔧 Please activate the virtual environment and run setup again:")
            if os.name == 'nt':
                print("   venv\\Scripts\\activate")
            else:
                print("   source venv/bin/activate")
            return False
    
    # Install core dependencies
    core_deps = [
        "google-generativeai>=0.3.0",
        "assemblyai>=0.17.0", 
        "elevenlabs>=0.2.24",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "Pillow>=10.0.0",
        "requests>=2.31.0"
    ]
    
    print("📦 Installing core dependencies...")
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep.split('>=')[0]}"):
            print(f"⚠️  Failed to install {dep}")
    
    # Install optional dependencies with error handling
    optional_deps = [
        ("opencv-python>=4.8.0", "Video processing"),
        ("pyaudio>=0.2.11", "Audio recording"),
        ("webrtcvad>=2.0.10", "Voice activity detection"), 
        ("psutil>=5.9.0", "System monitoring")
    ]
    
    print("\n📦 Installing optional dependencies...")
    for dep, description in optional_deps:
        print(f"🔧 Installing {dep.split('>=')[0]} ({description})...")
        result = subprocess.run(f"pip install {dep}", shell=True, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {dep.split('>=')[0]} installed")
        else:
            print(f"⚠️  {dep.split('>=')[0]} failed - {description} will be disabled")
    
    return True

def download_wake_word_model():
    """Download wake word model if needed"""
    model_path = Path("assets/audio/friday_windows_2024-08-28_v3_0_0.ppn")
    
    if model_path.exists():
        print("✅ Wake word model already exists")
        return True
    
    print("📥 Wake word model not found")
    print("⚠️  To enable wake word detection:")
    print("   1. Sign up at https://console.picovoice.ai/")
    print("   2. Create a 'Friday' wake word model")
    print("   3. Download the .ppn file")
    print("   4. Place it in assets/audio/")
    print("   5. Add your Picovoice API key to .env")
    
    return False

def run_tests():
    """Run basic tests"""
    print_header("Running Tests")
    
    # Test imports
    test_imports = [
        ("google.generativeai", "Gemini AI"),
        ("assemblyai", "AssemblyAI"),
        ("elevenlabs.client", "ElevenLabs"),
        ("fastapi", "FastAPI"),
        ("PIL", "Pillow")
    ]
    
    print("🧪 Testing core imports...")
    all_passed = True
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            all_passed = False
    
    # Test optional imports
    optional_imports = [
        ("cv2", "OpenCV"),
        ("pyaudio", "PyAudio"), 
        ("pvporcupine", "Porcupine"),
        ("webrtcvad", "WebRTC VAD")
    ]
    
    print("\n🧪 Testing optional imports...")
    for module, name in optional_imports:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"⚠️  {name} (optional)")
    
    return all_passed

def main():
    """Main setup function"""
    print_header("JARVIS AI Assistant Setup")
    
    try:
        # Create directory structure
        create_directories()
        
        # Create .env template
        env_exists = create_env_file()
        
        # Install dependencies
        if not install_dependencies():
            return
        
        # Check wake word model
        download_wake_word_model()
        
        # Run tests
        tests_passed = run_tests()
        
        # Final status
        print_header("Setup Complete")
        
        if tests_passed and env_exists:
            print("🎉 JARVIS setup completed successfully!")
            print("\n🚀 You can now run JARVIS:")
            print("   python main.py --mode desktop")
            print("   python main.py --mode server")
        else:
            print("⚠️  Setup completed with warnings:")
            if not env_exists:
                print("   - Please configure your API keys in .env")
            if not tests_passed:
                print("   - Some dependencies failed to install")
                print("   - Some features may not work")
            
            print(f"\n🔧 Run 'python main.py --mode check' to verify your setup")
        
    except KeyboardInterrupt:
        print("\n⏹️ Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()