"""
FRIDAY Configuration Settings
Centralized configuration management for the FRIDAY AI Assistant
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class FRIDAYSettings(BaseSettings):
    """FRIDAY Application Settings"""
    
    # API Configuration
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    assemblyai_api_key: str = Field(..., env="ASSEMBLYAI_API_KEY") 
    elevenlabs_api_key: str = Field(..., env="ELEVENLABS_API_KEY")
    picovoice_access_key: Optional[str] = Field(None, env="PICOVOICE_ACCESS_KEY")
    
    # Server Configuration
    host: str = Field("localhost", env="JARVIS_HOST")
    port: int = Field(8000, env="JARVIS_PORT")
    debug: bool = Field(False, env="JARVIS_DEBUG")
    
    # Audio Configuration
    sample_rate: int = Field(16000, env="AUDIO_SAMPLE_RATE")
    channels: int = Field(1, env="AUDIO_CHANNELS")
    chunk_size: int = Field(1024, env="AUDIO_CHUNK_SIZE")
    vad_aggressiveness: int = Field(3, env="VAD_AGGRESSIVENESS")
    silence_duration: float = Field(1.5, env="SILENCE_DURATION")
    
    # Voice Configuration - Updated for FRIDAY
    elevenlabs_voice_id: str = Field("EXAVITQu4vr4xnSDxMaL", env="ELEVENLABS_VOICE_ID")  # Bella voice
    wake_word_phrase: str = Field("Friday", env="WAKE_WORD_PHRASE")
    assistant_name: str = Field("FRIDAY", env="ASSISTANT_NAME")
    
    # File Paths
    temp_dir: str = Field("assets/temp", env="TEMP_DIR")
    assets_dir: str = Field("assets", env="ASSETS_DIR")
    
    # UI Configuration
    window_width: int = Field(1200, env="WINDOW_WIDTH")
    window_height: int = Field(800, env="WINDOW_HEIGHT")
    
    # AI Configuration
    model_name: str = Field("gemini-1.5-flash", env="GEMINI_MODEL")
    tts_model: str = Field("eleven_multilingual_v2", env="TTS_MODEL")
    conversation_history_limit: int = Field(20, env="CONVERSATION_HISTORY_LIMIT")
    
    # System Configuration
    max_recording_duration: int = Field(10, env="MAX_RECORDING_DURATION")
    enable_wake_word: bool = Field(True, env="ENABLE_WAKE_WORD")
    enable_video: bool = Field(True, env="ENABLE_VIDEO")
    
    # TTS Configuration
    enable_local_tts: bool = Field(True, env="ENABLE_LOCAL_TTS")
    tts_fallback_mode: str = Field("local", env="TTS_FALLBACK_MODE")  # "local", "system", "none"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

class UIColors:
    """UI Color Scheme for FRIDAY"""
    BG_PRIMARY = '#0a0a0a'
    BG_SECONDARY = '#1a1a2e'
    BG_ACCENT = '#16213e'
    HIGHLIGHT = '#0f4c75'
    TEXT_PRIMARY = '#ffffff'
    TEXT_SECONDARY = '#b0b0b0'
    SUCCESS = '#00ff41'
    WARNING = '#ffaa00'
    ERROR = '#ff4444'
    
    @classmethod
    def as_dict(cls):
        return {
            'bg_primary': cls.BG_PRIMARY,
            'bg_secondary': cls.BG_SECONDARY,
            'bg_accent': cls.BG_ACCENT,
            'highlight': cls.HIGHLIGHT,
            'text_primary': cls.TEXT_PRIMARY,
            'text_secondary': cls.TEXT_SECONDARY,
            'success': cls.SUCCESS,
            'warning': cls.WARNING,
            'error': cls.ERROR
        }

# Global settings instance
settings = FRIDAYSettings()

def get_settings() -> FRIDAYSettings:
    """Get application settings"""
    return settings

def ensure_directories():
    """Ensure required directories exist"""
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(settings.assets_dir, exist_ok=True)
    os.makedirs(f"{settings.assets_dir}/audio", exist_ok=True)
    os.makedirs(f"{settings.assets_dir}/images", exist_ok=True)
    os.makedirs(f"{settings.assets_dir}/temp", exist_ok=True)

# Initialize directories on import
ensure_directories()