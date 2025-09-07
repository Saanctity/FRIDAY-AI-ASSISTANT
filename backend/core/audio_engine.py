"""
Enhanced Audio Engine for JARVIS - FIXED VERSION
Handles audio processing including wake word detection, recording, and playbook
"""

import os
import struct
import time
import threading
import platform
import tempfile
from typing import Optional, Callable

from backend.config.settings import get_settings

# Audio imports with graceful fallback
try:
    import pvporcupine
    import pyaudio
    import webrtcvad
    HAS_AUDIO = True
    print("✅ Audio libraries loaded successfully")
except ImportError as e:
    print(f"❌ Audio libraries not available: {e}")
    HAS_AUDIO = False
    pvporcupine = None
    pyaudio = None
    webrtcvad = None
try:
    import pygame
    pygame.mixer.init()
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class AudioEngine:
    """Enhanced Audio Engine with improved recording and playback"""
    
    def __init__(self):
        self.settings = get_settings()
        self.porcupine = None
        self.vad = None
        self.audio_stream = None
        self.recording_stream = None
        self.pa = None
        

        # State variables
        self.is_listening = False
        self.is_recording = False
        self.is_initialized = False
        self.recording_stopped = False
        
        # Threading
        self.wake_word_thread = None
        
        # Audio settings
        self.chunk_size = 1024
        self.format = pyaudio.paInt16 if HAS_AUDIO else None
        self.channels = 1
        self.rate = 16000
        
    def initialize(self) -> bool:
        """Initialize audio components with better error handling"""
        if not HAS_AUDIO:
            print("⚠️ Audio libraries not available - voice features disabled")
            return False
            
        try:
            print("🔧 Initializing audio engine...")
            
            # Initialize PyAudio first
            self.pa = pyaudio.PyAudio()
            print("✅ PyAudio initialized")
            
            # List available audio devices for debugging
            self._list_audio_devices()
            
            # Initialize VAD with more permissive settings
            self.vad = webrtcvad.Vad(1)  # Less aggressive VAD
            print("✅ VAD initialized with permissive settings")
            
            # Initialize wake word detection
            if self._initialize_wake_word():
                print("✅ Wake word detection ready")
            else:
                print("⚠️ Wake word detection disabled - manual voice activation only")
            
            self.is_initialized = True
            print("✅ Audio engine fully initialized")
            return True
            
        except Exception as e:
            print(f"❌ Audio initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _list_audio_devices(self):
        """List available audio devices for debugging"""
        if not self.pa:
            return
        
        print("🎤 Available audio devices:")
        try:
            for i in range(self.pa.get_device_count()):
                info = self.pa.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"   Device {i}: {info['name']} (Input: {info['maxInputChannels']} channels)")
        except Exception as e:
            print(f"   Error listing devices: {e}")
    
    def _initialize_wake_word(self) -> bool:
        """Initialize wake word detection for 'Pink Bloomy'"""
        if not self.settings.enable_wake_word:
            return False
        
        # For now, we'll disable Porcupine wake word since you want "Pink Bloomy"
        # Porcupine requires custom trained models for custom wake words
        # We'll implement a simple keyword detection instead
        print("⚠️ Custom wake word 'Pink Bloomy' requires manual voice activation")
        print("   Click the microphone button to record commands")
        return False
    
    def record_audio_improved(self, max_duration: int = 10) -> Optional[bytes]:
        """Improved audio recording with better error handling"""
        if not self.is_initialized or not self.pa:
            print("❌ Audio not initialized")
            return None
        
        try:
            print("🎙️ Starting audio recording...")
            
            # Create a separate stream for recording
            recording_stream = self.pa.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=None  # Use default device
            )
            
            print("✅ Recording stream opened")
            
            self.is_recording = True
            self.recording_stopped = False
            frames = []
            silence_threshold = 30  # Number of silent chunks before stopping
            silence_count = 0
            min_recording_chunks = 10  # Minimum chunks to record
            
            print("🎤 Recording... (speak now)")
            start_time = time.time()
            
            while self.is_recording and (time.time() - start_time) < max_duration:
                try:
                    # Read audio chunk
                    data = recording_stream.read(self.chunk_size, exception_on_overflow=False)
                    frames.append(data)
                    
                    # Simple volume-based voice detection
                    # Convert to integers and check volume
                    audio_data = struct.unpack(f'{self.chunk_size}h', data)
                    volume = max(abs(x) for x in audio_data)
                    
                    if volume > 500:  # Voice detected (adjust threshold as needed)
                        silence_count = 0
                    else:
                        silence_count += 1
                    
                    # Stop recording after silence (but ensure minimum recording time)
                    if len(frames) > min_recording_chunks and silence_count > silence_threshold:
                        print("🔇 Silence detected - stopping recording")
                        break
                        
                except Exception as e:
                    print(f"Recording chunk error: {e}")
                    break
            
            # Close recording stream
            recording_stream.stop_stream()
            recording_stream.close()
            
            self.is_recording = False
            
            if frames:
                print(f"✅ Recorded {len(frames)} audio chunks")
                return b''.join(frames)
            else:
                print("❌ No audio data recorded")
                return None
                
        except Exception as e:
            print(f"❌ Recording error: {e}")
            import traceback
            traceback.print_exc()
            self.is_recording = False
            return None
    
    def stop_recording(self):
        """Stop current recording"""
        print("⏹️ Stopping recording...")
        self.is_recording = False
        self.recording_stopped = True
    
    def play_audio_improved(self, audio_data: bytes) -> bool:
        """Improved audio playback with pygame and multiple fallbacks"""
        if not audio_data:
            print("❌ No audio data to play")
            return False
    
        print("🔊 Playing audio response...")
    
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                tmp_file.write(audio_data)
        
            success = False
        
            # Method 1: Try pygame (best for MP3 files from gTTS)
            if HAS_PYGAME and self._play_with_pygame(tmp_path):
                success = True
            # Method 2: Platform-specific playback
            elif self._play_with_system_command(tmp_path):
                success = True
            # Method 3: Try opening with default application
            elif self._play_with_default_app(tmp_path):
                success = True
        
            # Cleanup after a delay
            def cleanup_file():
                try:
                    time.sleep(2)  # Give time for playback to complete
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                except:
                    pass
        
            threading.Thread(target=cleanup_file, daemon=True).start()
        
            if success:
                print("✅ Audio playback completed")
            else:
                print("❌ All audio playback methods failed")
        
            return success
        
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
            return False

    def _play_with_pygame(self, filepath: str) -> bool:
        """Play audio using pygame mixer"""
        try:
            # Load and play the audio file
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
        
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        
            return True
        
        except Exception as e:
            print(f"Pygame playback error: {e}")
            return False
    
    def _play_with_system_command(self, filepath: str) -> bool:
        """Play audio using system commands"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                if HAS_WINSOUND:
                    import threading
                    # Play in separate thread to avoid blocking
                    def play_async():
                        try:
                            winsound.PlaySound(filepath, winsound.SND_FILENAME)
                        except Exception as e:
                            print(f"Winsound error: {e}")
                    
                    threading.Thread(target=play_async, daemon=True).start()
                    return True
                else:
                    # Fallback to start command
                    os.system(f'start /min "" "{filepath}"')
                    return True
                    
            elif system == "darwin":  # macOS
                os.system(f'afplay "{filepath}" &')
                return True
                
            else:  # Linux
                # Try multiple Linux audio players
                players = ['aplay', 'paplay', 'pulseaudio']
                for player in players:
                    try:
                        os.system(f'{player} "{filepath}" &')
                        return True
                    except:
                        continue
                        
            return False
            
        except Exception as e:
            print(f"System command playback error: {e}")
            return False
    
    def _play_with_pyaudio(self, filepath: str) -> bool:
        """Play audio using PyAudio"""
        try:
            import wave
            
            # Open wave file
            with wave.open(filepath, 'rb') as wf:
                # Create PyAudio stream
                stream = self.pa.open(
                    format=self.pa.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # Play audio
                data = wf.readframes(1024)
                while data:
                    stream.write(data)
                    data = wf.readframes(1024)
                
                # Cleanup
                stream.stop_stream()
                stream.close()
                
            return True
            
        except Exception as e:
            print(f"PyAudio playback error: {e}")
            return False
    
    def _play_with_default_app(self, filepath: str) -> bool:
        """Play audio by opening with default application"""
        try:
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(filepath)}')
            return True
        except Exception as e:
            print(f"Default app playback error: {e}")
            return False
    
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
        print("🎤 Testing microphone...")
        
        if not self.is_initialized:
            print("❌ Audio engine not initialized")
            return False
        
        try:
            # Test recording for 2 seconds
            test_audio = self.record_audio_improved(max_duration=3)
            
            if test_audio and len(test_audio) > 1000:  # At least some audio data
                print(f"✅ Microphone test passed - recorded {len(test_audio)} bytes")
                return True
            else:
                print("❌ Microphone test failed - no audio recorded")
                return False
                
        except Exception as e:
            print(f"❌ Microphone test error: {e}")
            return False
    
    def test_speakers(self) -> bool:
        """Test speaker functionality"""
        print("🔊 Testing speakers...")
        
        try:
            # Generate a simple test tone
            import wave
            import math
            
            # Create a simple beep
            duration = 0.5  # seconds
            sample_rate = 22050
            frequency = 440  # Hz (A4 note)
            
            frames = []
            for i in range(int(duration * sample_rate)):
                value = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
                frames.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            # Create wave data
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(bytes(frames))
                
                # Read the file back as bytes
                with open(tmp_file.name, 'rb') as f:
                    test_audio = f.read()
                
                # Test playback
                success = self.play_audio_improved(test_audio)
                
                # Cleanup
                try:
                    os.unlink(tmp_file.name)
                except:
                    pass
                
                return success
                
        except Exception as e:
            print(f"❌ Speaker test error: {e}")
            return False
    
    def _play_with_pygame(self, filepath: str) -> bool:
        """Play audio using pygame mixer with better error handling"""
        try:
            # Initialize mixer for MP3 support
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
            # Load and play the audio file
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
        
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        
            return True
        
        except Exception as e:
            print(f"Pygame playback error: {e}")
            return False    

    def get_audio_info(self) -> dict:
        """Get audio system information"""
        info = {
            'initialized': self.is_initialized,
            'has_audio_libs': HAS_AUDIO,
            'recording': self.is_recording,
            'listening': self.is_listening,
            'sample_rate': self.rate,
            'channels': self.channels,
            'chunk_size': self.chunk_size
        }
        
        if self.pa:
            try:
                info['device_count'] = self.pa.get_device_count()
                info['default_input'] = self.pa.get_default_input_device_info()['name']
                info['default_output'] = self.pa.get_default_output_device_info()['name']
            except:
                pass
        
        return info
    
    def cleanup(self):
        """Enhanced cleanup with better error handling"""
        print("🔧 Cleaning up audio engine...")
        
        # Stop all operations
        self.is_listening = False
        self.is_recording = False
        
        # Wait for threads to finish
        if self.wake_word_thread:
            self.wake_word_thread.join(timeout=2.0)
        
        # Close streams
        if self.audio_stream:
            try:
                self.audio_stream.close()
            except:
                pass
        
        if self.recording_stream:
            try:
                self.recording_stream.close()
            except:
                pass
        
        # Terminate PyAudio
        if self.pa:
            try:
                self.pa.terminate()
            except:
                pass
        
        # Delete Porcupine
        if self.porcupine:
            try:
                self.porcupine.delete()
            except:
                pass
        
        self.is_initialized = False
        print("✅ Audio engine cleanup complete")

# Global instance
_audio_engine = None

def get_audio_engine() -> AudioEngine:
    """Get global audio engine instance"""
    global _audio_engine
    if _audio_engine is None:
        _audio_engine = AudioEngine()
    return _audio_engine