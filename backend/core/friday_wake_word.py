"""
FRIDAY Wake Word Detection System
Implements keyword spotting for "Friday" using multiple methods
"""

import threading
import time
import re
from typing import Callable, Optional

from backend.config.settings import get_settings

# Try to import speech_recognition
try:
    import speech_recognition as sr
    HAS_SPEECH_RECOGNITION = True
except ImportError:
    HAS_SPEECH_RECOGNITION = False
    sr = None

class FridayWakeWordDetector:
    """Wake word detector specifically for 'Friday'"""
    
    def __init__(self):
        self.settings = get_settings()
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.wake_phrases = [
            "friday",
            "hey friday", 
            "ok friday",
            "hello friday",
            "hi friday"
        ]
        self.listen_thread = None
        self.callback_function = None
        
    def initialize(self) -> bool:
        """Initialize wake word detector"""
        if not HAS_SPEECH_RECOGNITION:
            print("⚠️ speech_recognition library not available")
            print("   Install with: pip install SpeechRecognition")
            return False
        
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Calibrate for ambient noise
            print("🔧 Calibrating microphone for 'Friday' wake word detection...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # Make it more sensitive for wake words
                self.recognizer.energy_threshold = min(self.recognizer.energy_threshold, 300)
            
            print("✅ FRIDAY wake word detector initialized")
            print(f"🎯 Listening for: {', '.join(self.wake_phrases)}")
            return True
            
        except Exception as e:
            print(f"❌ Wake word detector initialization failed: {e}")
            return False
    
    def start_listening(self, callback: Callable) -> bool:
        """Start listening for Friday wake word"""
        if not self.recognizer:
            print("❌ Wake word detector not initialized")
            return False
        
        if self.is_listening:
            print("⚠️ Already listening for wake word")
            return True
        
        self.callback_function = callback
        self.is_listening = True
        
        self.listen_thread = threading.Thread(
            target=self._continuous_listen,
            daemon=True
        )
        self.listen_thread.start()
        
        print(f"👂 Started listening for FRIDAY wake word...")
        return True
    
    def stop_listening(self):
        """Stop wake word detection"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2.0)
        print("⏹️ Stopped FRIDAY wake word detection")
    
    def _continuous_listen(self):
        """Continuous listening loop for wake word"""
        print("🎧 FRIDAY wake word listener active...")
        
        while self.is_listening:
            try:
                # Listen for audio with short timeout
                with self.microphone as source:
                    # Quick listen for potential wake word
                    audio = self.recognizer.listen(
                        source, 
                        timeout=0.5,  # Short timeout to be responsive
                        phrase_time_limit=3  # Max 3 seconds per phrase
                    )
                
                # Process in separate thread to avoid blocking
                threading.Thread(
                    target=self._process_audio_chunk,
                    args=(audio,),
                    daemon=True
                ).start()
                
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening
                continue
            except Exception as e:
                print(f"⚠️ Wake word listening error: {e}")
                time.sleep(0.5)  # Brief pause before retrying
    
    def _process_audio_chunk(self, audio):
        """Process audio chunk for wake word detection"""
        try:
            # Use faster recognition with timeout
            text = self.recognizer.recognize_google(audio, language='en-US').lower().strip()
            
            if text:
                print(f"🎧 Heard: '{text}'")
                
                # Check for wake phrases
                if self._contains_wake_word(text):
                    print(f"🎯 FRIDAY wake word detected!")
                    if self.callback_function:
                        # Call the callback in the main thread
                        self.callback_function()
                    
                    # Brief pause after wake word detection
                    time.sleep(1)
                    
        except sr.UnknownValueError:
            # No speech detected or unclear audio
            pass
        except sr.RequestError as e:
            print(f"⚠️ Speech recognition service error: {e}")
        except Exception as e:
            print(f"⚠️ Audio processing error: {e}")
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains any wake word variations"""
        text = text.lower().strip()
        
        # Direct matches
        for phrase in self.wake_phrases:
            if phrase in text:
                return True
        
        # Fuzzy matching for better detection
        wake_word_patterns = [
            r'\bfriday\b',        # Exact word boundary match
            r'\bfri+day\b',       # Handle pronunciation variations
            r'\bfridie\b',        # Common mispronunciation
            r'\bfridey\b',        # Another variation
        ]
        
        for pattern in wake_word_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def test_detection(self, timeout: int = 10) -> bool:
        """Test wake word detection"""
        if not self.recognizer:
            print("❌ Wake word detector not initialized")
            return False
        
        print(f"🧪 Testing FRIDAY wake word detection...")
        print(f"   Say 'Friday' or 'Hey Friday' within {timeout} seconds...")
        
        try:
            start_time = time.time()
            detected = False
            
            def test_callback():
                nonlocal detected
                detected = True
                print("✅ Wake word detection test PASSED!")
            
            # Temporarily start listening
            original_callback = self.callback_function
            was_listening = self.is_listening
            
            if not was_listening:
                self.start_listening(test_callback)
            else:
                self.callback_function = test_callback
            
            # Wait for detection or timeout
            while time.time() - start_time < timeout and not detected:
                time.sleep(0.1)
            
            # Restore original state
            if not was_listening:
                self.stop_listening()
            self.callback_function = original_callback
            
            if not detected:
                print("❌ Wake word not detected within timeout")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Wake word test failed: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get wake word detector status"""
        return {
            'initialized': self.recognizer is not None,
            'listening': self.is_listening,
            'wake_phrases': self.wake_phrases,
            'thread_active': self.listen_thread is not None and self.listen_thread.is_alive()
        }
    
    def set_sensitivity(self, level: str = "medium"):
        """Set detection sensitivity"""
        if not self.recognizer:
            return False
        
        try:
            if level == "high":
                self.recognizer.energy_threshold = 200
                self.recognizer.dynamic_energy_threshold = True
            elif level == "low":
                self.recognizer.energy_threshold = 500
                self.recognizer.dynamic_energy_threshold = False
            else:  # medium
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
            
            print(f"✅ Wake word sensitivity set to {level}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set sensitivity: {e}")
            return False
    
    def add_wake_phrase(self, phrase: str):
        """Add custom wake phrase"""
        phrase = phrase.lower().strip()
        if phrase and phrase not in self.wake_phrases:
            self.wake_phrases.append(phrase)
            print(f"✅ Added wake phrase: '{phrase}'")
    
    def remove_wake_phrase(self, phrase: str):
        """Remove wake phrase"""
        phrase = phrase.lower().strip()
        if phrase in self.wake_phrases and len(self.wake_phrases) > 1:
            self.wake_phrases.remove(phrase)
            print(f"✅ Removed wake phrase: '{phrase}'")
        else:
            print(f"⚠️ Cannot remove '{phrase}' - not found or last remaining phrase")

# Global instance
_friday_wake_detector = None

def get_friday_wake_detector() -> FridayWakeWordDetector:
    """Get global FRIDAY wake word detector instance"""
    global _friday_wake_detector
    if _friday_wake_detector is None:
        _friday_wake_detector = FridayWakeWordDetector()
    return _friday_wake_detector