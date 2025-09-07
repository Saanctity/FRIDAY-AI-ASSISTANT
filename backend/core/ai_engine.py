"""
Enhanced AI Engine for FRIDAY - FIXED VERSION
Better TTS handling with fallbacks, improved audio processing
"""

import os
import wave
import tempfile
from datetime import datetime
from typing import Optional, List, Tuple
import google.generativeai as genai
import assemblyai as aai
from elevenlabs.client import ElevenLabs
from PIL import Image
import platform
#from notegpt_tts import NoteGPTTTS
from dotenv import load_dotenv

from backend.config.settings import get_settings

# TTS fallback imports
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

#try:
 #   from notegpt_tts import NoteGPTTTS
  #  HAS_NOTEGPT = True
#except ImportError:
 #   HAS_NOTEGPT = False
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False
    pyttsx3 = None

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class AIEngine:
    """Enhanced AI Engine with TTS fallbacks and better error handling"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model = None
        self.transcriber = None
        self.tts_client = None
        self.local_tts = None  # Local TTS fallback
        self.conversation_history: List[Tuple[str, str]] = []
        self.is_initialized = False
        self.tts_mode = "elevenlabs"  # Can be "elevenlabs", "local", or "system"
        
        # System command patterns
        self.command_patterns = {
            'open_website': [
                'open google.com', 'go to google', 'launch google',
                'open youtube.com', 'go to youtube', 'launch youtube',
                'open website', 'go to site', 'browse to'
            ],
            'open_app': [
                'open notepad', 'launch notepad', 'start notepad',
                'open calculator', 'launch calculator', 'start calculator',
                'open application', 'launch app', 'start program'
            ]
        }
        
    def initialize(self) -> bool:
        """Initialize all AI services with better error handling"""
        try:
            print("🔧 Initializing FRIDAY AI engine...")
            
            # Initialize Gemini
            if self.settings.gemini_api_key:
                genai.configure(api_key=self.settings.gemini_api_key)
                self.model = genai.GenerativeModel(self.settings.model_name)
                print("✅ Gemini AI initialized")
            else:
                print("❌ Gemini API key missing")
                return False
            
            # Initialize AssemblyAI
            if self.settings.assemblyai_api_key:
                aai.settings.api_key = self.settings.assemblyai_api_key
                self.transcriber = aai.Transcriber()
                print("✅ AssemblyAI initialized")
            else:
                print("❌ AssemblyAI API key missing")
                return False
            
            # Initialize TTS with fallbacks
            self._initialize_tts()
            
            self.is_initialized = True
            print("✅ FRIDAY AI engine fully initialized")
            return True
            
        except Exception as e:
            print(f"❌ AI initialization error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _initialize_tts(self):
    
        """Initialize TTS with multiple fallback options including NoteGPT and gTTS"""
        # Try ElevenLabs first
        if self.settings.elevenlabs_api_key:
            try:
                self.tts_client = ElevenLabs(api_key=self.settings.elevenlabs_api_key)
                if self._test_elevenlabs():
                    print("✅ ElevenLabs TTS initialized")
                    self.tts_mode = "elevenlabs"
                    return
                else:
                    print("⚠️ ElevenLabs quota exceeded or error - switching to alternatives")
            except Exception as e:
                print(f"⚠️ ElevenLabs error: {e}")
    
        # Try NoteGPT TTS
        #if HAS_NOTEGPT:
        #    try:
         #       self.notegpt_client = NoteGPTTTS()
          #      print("✅ NoteGPT TTS initialized")
           #     self.tts_mode = "notegpt"
            #    return
            #except Exception as e:
             #   print(f"⚠️ NoteGPT TTS error: {e}")
    
        # Try Google TTS (gTTS)
        if HAS_GTTS:
            try:
                # Test gTTS with a simple phrase
                test_tts = gTTS(text="test", lang='en', slow=False)
                print("✅ Google TTS (gTTS) initialized")
                self.tts_mode = "gtts"
                return
            except Exception as e:
                print(f"⚠️ gTTS error: {e}")
    
        # Skip pyttsx3 since it causes issues on your system
        print("⚠️ Skipping pyttsx3 due to known issues")
    
        # Final fallback to system TTS
        print("⚠️ Using system TTS as final fallback")
        self.tts_mode = "system"
    
    def _test_elevenlabs(self) -> bool:
        """Test ElevenLabs TTS with a short phrase"""
        try:
            audio_generator = self.tts_client.text_to_speech.convert(
                text="Test",
                voice_id=self.settings.elevenlabs_voice_id,
                model_id=self.settings.tts_model
            )
            test_audio = next(audio_generator)
            return len(test_audio) > 0
        except Exception as e:
            print(f"ElevenLabs test failed: {e}")
            return False
    
    def transcribe_audio(self, audio_data: bytes, filename: str = None) -> Optional[str]:
        """Enhanced transcription with better error handling"""
        if not self.transcriber:
            print("❌ Transcriber not initialized")
            return None
        
        if not audio_data or len(audio_data) < 1000:
            print("❌ Insufficient audio data for transcription")
            return None
            
        try:
            print("🔄 Transcribing audio...")
            
            # Create temporary file
            if filename is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                temp_path = temp_file.name
                temp_file.close()
            else:
                temp_path = os.path.join(self.settings.temp_dir, filename)
            
            # Write WAV file with proper header
            with wave.open(temp_path, "wb") as wav_file:
                wav_file.setnchannels(self.settings.channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(self.settings.sample_rate)
                wav_file.writeframes(audio_data)
            
            print(f"📁 Audio saved to: {temp_path}")
            print(f"📊 Audio file size: {os.path.getsize(temp_path)} bytes")
            
            # Transcribe
            print("🔄 Sending to AssemblyAI...")
            transcript = self.transcriber.transcribe(temp_path)
            
            # Cleanup
            try:
                os.remove(temp_path)
            except:
                pass
            
            if transcript.status == aai.TranscriptStatus.completed:
                result = transcript.text.strip()
                print(f"✅ Transcription result: '{result}'")
                return result if result else None
            else:
                print(f"❌ Transcription failed: {transcript.error}")
                return None
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_system_command(self, text: str) -> bool:
        """Check if text is a system command"""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # Command indicators
        command_indicators = [
            'open ', 'launch ', 'start ', 'go to ', 'browse to ',
            'show me ', 'take me to ', 'navigate to '
        ]
        
        has_command_indicator = any(
            indicator in text_lower for indicator in command_indicators
        )
        
        if not has_command_indicator:
            return False
        
        # System targets
        system_targets = [
            'google.com', 'google', 'youtube.com', 'youtube',
            'notepad', 'calculator', 'browser', 'website'
        ]
        
        # Question patterns
        question_patterns = [
            'what is', 'tell me about', 'explain', 'how does',
            'why does', 'can you help', 'do you know about'
        ]
        
        # If it's a question, don't treat as command
        if any(pattern in text_lower for pattern in question_patterns):
            return False
        
        return any(target in text_lower for target in system_targets)
    
    def get_response(self, user_input: str, image_data: Optional[Image.Image] = None) -> str:
        """Generate AI response with FRIDAY personality"""
        if not self.model:
            return "AI engine not initialized"
            
        try:
            # Add to conversation history
            self.conversation_history.append(("user", user_input))
            
            # Build context
            context = self._build_conversation_context()
            
            # Create FRIDAY system prompt
            system_prompt = self._create_friday_prompt(context)
            
            # Generate response
            if image_data:
                response = self.model.generate_content([
                    system_prompt + f"\n\nUser: {user_input}", 
                    image_data
                ])
            else:
                full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nFRIDAY:"
                response = self.model.generate_content(full_prompt)
            
            ai_response = response.text.strip()
            
            # Add to history
            self.conversation_history.append(("assistant", ai_response))
            
            # Maintain history limit
            if len(self.conversation_history) > self.settings.conversation_history_limit:
                self.conversation_history = self.conversation_history[-self.settings.conversation_history_limit:]
            
            return ai_response
            
        except Exception as e:
            print(f"❌ AI response error: {e}")
            import traceback
            traceback.print_exc()
            return "I apologize, I'm experiencing some technical difficulties at the moment."
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """Enhanced TTS with multiple providers"""
        if not text or not text.strip():
            print("❌ No text provided for TTS")
            return None
        
        try:
            clean_text = self._clean_text_for_tts(text)
            print(f"🔊 Converting to speech ({self.tts_mode}): '{clean_text[:50]}{'...' if len(clean_text) > 50 else ''}'")
        
            if self.tts_mode == "elevenlabs" and self.tts_client:
                return self._elevenlabs_tts(clean_text)
            #elif self.tts_mode == "notegpt" and hasattr(self, 'notegpt_client'):
             #   return self._notegpt_tts(clean_text)
            elif self.tts_mode == "gtts":
                return self._gtts_tts(clean_text)
            else:
                return self._system_tts(clean_text)
        
        except Exception as e:
            print(f"❌ TTS error: {e}")
            # Try next available fallback
            self._switch_to_next_provider()
            if self.tts_mode != "system":
               return self.text_to_speech(text)
        return None

    
    def _elevenlabs_tts(self, text: str) -> Optional[bytes]:
        """ElevenLabs TTS with error handling"""
        try:
            audio_generator = self.tts_client.text_to_speech.convert(
                text=text,
                voice_id=self.settings.elevenlabs_voice_id,
                model_id=self.settings.tts_model
            )
            
            audio_chunks = []
            for chunk in audio_generator:
                audio_chunks.append(chunk)
            
            if audio_chunks:
                audio_data = b''.join(audio_chunks)
                print(f"✅ Generated {len(audio_data)} bytes of audio")
                return audio_data
            else:
                raise Exception("No audio data generated")
                
        except Exception as e:
            print(f"❌ ElevenLabs TTS failed: {e}")
            # Switch to local TTS
            self.tts_mode = "local"
            return self._local_tts(text)
        
    def _gtts_tts(self, text: str) -> Optional[bytes]:
        """Google TTS (gTTS) implementation"""
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
        
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            temp_path = temp_file.name
            temp_file.close()
        
            # Generate speech
            tts.save(temp_path)
        
            # Read the generated file
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            # Cleanup
            os.remove(temp_path)
        
            if len(audio_data) > 1000:  # Valid audio file
                print(f"✅ gTTS generated {len(audio_data)} bytes")
                return audio_data
            else:
                raise Exception("Invalid audio file generated")
        except Exception as e:
            print(f"❌ gTTS failed: {e}")
            return self._system_tts(text)
    
    def _local_tts(self, text: str) -> Optional[bytes]:
        """Local TTS using pyttsx3"""
        try:
            if not self.local_tts:
                if HAS_PYTTSX3:
                    self.local_tts = pyttsx3.init()
                else:
                    return self._system_tts(text)
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Generate speech
            self.local_tts.save_to_file(text, temp_path)
            self.local_tts.runAndWait()
            
            # Read the generated file
            try:
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                os.remove(temp_path)
                
                if len(audio_data) > 1000:  # Valid audio file
                    print(f"✅ Local TTS generated {len(audio_data)} bytes")
                    return audio_data
                else:
                    raise Exception("Invalid audio file generated")
                    
            except Exception as e:
                print(f"❌ Local TTS file error: {e}")
                return self._system_tts(text)
                
        except Exception as e:
            print(f"❌ Local TTS error: {e}")
            return self._system_tts(text)
    
    def _system_tts(self, text: str) -> Optional[bytes]:
        """System TTS fallback (doesn't return bytes, just plays)"""
        try:
            system = platform.system().lower()
            
            if system == "windows":
                # Use Windows SAPI
                import subprocess
                subprocess.run([
                    'PowerShell', '-Command',
                    f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{text}")'
                ], check=True)
                print("✅ Windows TTS played")
                return b"system_tts_played"  # Dummy return to indicate success
                
            elif system == "darwin":  # macOS
                os.system(f'say "{text}"')
                print("✅ macOS TTS played")
                return b"system_tts_played"
                
            else:  # Linux
                # Try espeak or festival
                try:
                    subprocess.run(['espeak', text], check=True)
                    print("✅ Linux TTS played (espeak)")
                    return b"system_tts_played"
                except:
                    subprocess.run(['festival', '--tts'], input=text.encode(), check=True)
                    print("✅ Linux TTS played (festival)")
                    return b"system_tts_played"
                    
        except Exception as e:
            print(f"❌ System TTS error: {e}")
            print(f"🗣️ FRIDAY says: {text}")  # Fallback to text output
            return None
    
    def analyze_image(self, image: Image.Image, question: str) -> str:
        """Analyze image with FRIDAY personality"""
        try:
            prompt = f"""You are FRIDAY, an advanced AI assistant. The user asks: {question}
            
            Provide a detailed but conversational analysis of the image. Be professional but 
            friendly, and remember you're FRIDAY - Tony Stark's AI assistant."""
            
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Image analysis error: {e}")
            return "I'm having trouble analyzing this image at the moment."
    
    def _build_conversation_context(self) -> str:
        """Build conversation context from history"""
        if len(self.conversation_history) <= 1:
            return ""
        
        context = "Recent conversation context:\n"
        recent_history = self.conversation_history[-5:-1]
        
        for role, message in recent_history:
            if role == "user":
                context += f"User: {message[:80]}{'...' if len(message) > 80 else ''}\n"
            else:
                context += f"FRIDAY: {message[:80]}{'...' if len(message) > 80 else ''}\n"
        
        return context
    
    def _create_friday_prompt(self, context: str = "") -> str:
        """Create FRIDAY-specific system prompt"""
        base_prompt = f"""You are FRIDAY (Female Replacement Intelligent Digital Assistant Youth), Tony Stark's advanced AI assistant. You are:

- Intelligent, helpful, and conversational with a sophisticated but approachable personality
- Professional yet friendly, addressing the user respectfully 
- Knowledgeable about technology, science, and various topics
- Able to maintain natural conversation while being informative and helpful
- Capable of remembering and referencing our conversation history

{context}

Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Guidelines:
- Keep responses conversational and engaging
- Be concise unless detail is specifically requested
- Reference previous conversation when relevant
- Maintain your sophisticated but approachable FRIDAY personality
- Don't automatically assume every mention of a website/app is a command to open it
- Only suggest opening applications/websites when the user clearly wants to do so"""

        return base_prompt
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove markdown formatting
        clean_text = text.replace("*", "").replace("_", "").replace("#", "")
        clean_text = clean_text.replace("```", "").replace("`", "")
        
        # Fix abbreviations
        replacements = {
            "e.g.": "for example",
            "i.e.": "that is", 
            "etc.": "etcetera",
            "vs.": "versus",
            "Mr.": "Mister",
            "Dr.": "Doctor",
            "Prof.": "Professor"
        }
        
        for abbrev, replacement in replacements.items():
            clean_text = clean_text.replace(abbrev, replacement)
        
        # Remove excessive punctuation
        clean_text = clean_text.replace("...", ".")
        clean_text = clean_text.replace("!!", "!")
        clean_text = clean_text.replace("??", "?")
        
        # Ensure proper sentence ending
        clean_text = clean_text.strip()
        if clean_text and not clean_text.endswith(('.', '!', '?')):
            clean_text += "."
            
        return clean_text
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🗑️ Conversation history cleared")
    
    def get_conversation_summary(self) -> str:
        """Get conversation summary"""
        if not self.conversation_history:
            return "No conversation history"
        
        total_exchanges = len(self.conversation_history) // 2
        recent_topics = []
        
        for role, message in self.conversation_history[-6:]:
            if role == "user":
                recent_topics.append(message[:50] + "..." if len(message) > 50 else message)
        
        return f"Conversation: {total_exchanges} exchanges. Recent topics: {', '.join(recent_topics[:3])}"
    
    def test_ai_response(self) -> bool:
        """Test AI response functionality"""
        try:
            test_response = self.get_response("Hello FRIDAY, can you hear me?")
            return bool(test_response and len(test_response) > 10)
        except Exception as e:
            print(f"AI response test failed: {e}")
            return False
    
    def get_engine_status(self) -> dict:
        """Get detailed engine status"""
        return {
            'initialized': self.is_initialized,
            'model_ready': self.model is not None,
            'transcriber_ready': self.transcriber is not None,
            'tts_mode': self.tts_mode,
            'tts_ready': self.tts_client is not None or self.local_tts is not None,
            'conversation_length': len(self.conversation_history),
            'settings_loaded': self.settings is not None
        }