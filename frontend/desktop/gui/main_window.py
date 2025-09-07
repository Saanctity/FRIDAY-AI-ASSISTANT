"""
Enhanced Main GUI Window for FRIDAY - FIXED VERSION
Automatic wake word detection with Friday, enhanced system commands
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import time
from datetime import datetime
from typing import Optional
from PIL import Image, ImageTk

from backend.config.settings import get_settings, UIColors
from backend.core.ai_engine import AIEngine
from backend.core.audio_engine import get_audio_engine
from backend.core.video_engine import get_video_engine
from backend.core.friday_wake_word import get_friday_wake_detector
from backend.services.system_controller import SystemController

class FRIDAYMainWindow:
    """Enhanced FRIDAY GUI Window with automatic wake word detection"""
    
    def __init__(self):
        self.settings = get_settings()
        self.colors = UIColors.as_dict()
        
        # Initialize components
        self.ai_engine = AIEngine()
        self.audio_engine = get_audio_engine()
        self.video_engine = get_video_engine()
        self.wake_detector = get_friday_wake_detector()
        self.system_controller = SystemController()
        
        # GUI components - Initialize to None first
        self.root = None
        self.status_var = None
        self.chat_display = None
        self.text_input = None
        self.video_label = None
        self.info_text = None
        self.status_label = None
        
        # Control buttons
        self.voice_btn = None
        self.camera_btn = None
        self.cam_toggle_btn = None
        self.wake_toggle_btn = None
        self.capture_btn = None
        self.wake_status_label = None
        
        # State variables
        self.is_voice_active = False
        self.is_camera_active = False
        self.is_recording = False
        self.is_speaking = False
        self.wake_word_active = False
        self.camera_active = False
        
        # Video components
        self.video_frame = None
        
        # Setup window first, then video panel
        self.setup_window()
        
    def setup_window(self):
        """Setup main window with enhanced styling"""
        self.root = tk.Tk()
        self.root.title("🤖 F.R.I.D.A.Y - Female Replacement Intelligent Digital Assistant Youth")
        self.root.geometry(f"{self.settings.window_width}x{self.settings.window_height}")
        self.root.minsize(800, 600)
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Configure window properties
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center window on screen
        self.center_window()
        
        # State variables
        self.status_var = tk.StringVar(value="Initializing FRIDAY...")
        
        # Setup GUI components
        self.setup_styles()
        self.create_interface()
        
        # Initialize components
        self.initialize_components()
    
    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.settings.window_width // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.settings.window_height // 2)
        self.root.geometry(f"{self.settings.window_width}x{self.settings.window_height}+{x}+{y}")
    
    def setup_styles(self):
        """Setup custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Header.TLabel', 
                       background=self.colors['highlight'], 
                       foreground=self.colors['text_primary'],
                       font=('Arial', 16, 'bold'))
    
    def create_interface(self):
        """Create main interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True)
        
        # Create sections
        self.create_header(main_container)
        self.create_content_area(main_container)
    
    def create_header(self, parent):
        """Create modern header with title and status"""
        header = tk.Frame(parent, bg=self.colors['highlight'], height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Left side - Title and subtitle
        left_header = tk.Frame(header, bg=self.colors['highlight'])
        left_header.pack(side="left", fill="y", padx=20)
        
        title_label = tk.Label(
            left_header, 
            text="🤖 F.R.I.D.A.Y", 
            bg=self.colors['highlight'], 
            fg=self.colors['text_primary'],
            font=("Arial", 24, "bold")
        )
        title_label.pack(anchor="w", pady=(15, 0))
        
        subtitle_label = tk.Label(
            left_header,
            text="Female Replacement Intelligent Digital Assistant Youth",
            bg=self.colors['highlight'],
            fg=self.colors['text_secondary'], 
            font=("Arial", 10, "italic")
        )
        subtitle_label.pack(anchor="w")
        
        # Right side - Status and controls
        right_header = tk.Frame(header, bg=self.colors['highlight'])
        right_header.pack(side="right", fill="y", padx=20)
        
        # Status
        status_frame = tk.Frame(right_header, bg=self.colors['highlight'])
        status_frame.pack(anchor="e", pady=(10, 5))
        
        tk.Label(status_frame, text="Status:", bg=self.colors['highlight'], 
                fg=self.colors['text_secondary'], font=("Arial", 10)).pack(side="left")
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=self.colors['highlight'],
            fg=self.colors['success'], 
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side="left", padx=(5, 0))
        
        # Wake word toggle button
        self.wake_toggle_btn = tk.Button(
            right_header,
            text="🎯 Enable Wake Word",
            command=self.toggle_wake_word,
            bg=self.colors['warning'],
            fg=self.colors['bg_primary'],
            font=("Arial", 8),
            relief="flat"
        )
        self.wake_toggle_btn.pack(anchor="e", pady=(0, 10))
    
    def create_content_area(self, parent):
        """Create main content area"""
        content_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel (chat + controls)
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_primary'])
        left_panel.pack(side="left", fill="both", expand=True)
        
        # Right panel (video + info)
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_secondary'], width=320)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        # Setup panels
        self.create_chat_area(left_panel)
        self.create_input_area(left_panel)
        self.create_right_panel(right_panel)
    
    def create_chat_area(self, parent):
        """Create enhanced chat area"""
        chat_frame = tk.LabelFrame(
            parent, 
            text="💬 Conversation with FRIDAY", 
            bg=self.colors['bg_primary'], 
            fg=self.colors['text_primary'], 
            font=("Arial", 12, "bold")
        )
        chat_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            bg=self.colors['bg_secondary'], 
            fg=self.colors['text_primary'],
            font=("Consolas", 11),
            state="disabled",
            wrap="word",
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['highlight']
        )
        self.chat_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure text tags for styling
        self.chat_display.tag_configure("user", foreground="#64B5F6")
        self.chat_display.tag_configure("friday", foreground="#4CAF50") 
        self.chat_display.tag_configure("system", foreground="#FFA726")
        self.chat_display.tag_configure("timestamp", foreground="#9E9E9E", font=("Consolas", 9))
        self.chat_display.tag_configure("speaking", foreground="#FF6B6B", font=("Consolas", 10, "italic"))
        self.chat_display.tag_configure("wake", foreground="#00FF00", font=("Consolas", 10, "bold"))
    
    def create_input_area(self, parent):
        """Create enhanced input area with better controls"""
        input_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        input_frame.pack(fill="x", pady=(0, 5))
        
        # Text input with placeholder
        self.text_input = tk.Entry(
            input_frame,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'], 
            font=("Arial", 12),
            insertbackground=self.colors['text_primary'],
            relief="flat",
            bd=1
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
        self.text_input.bind("<Return>", self.send_message)
        self.text_input.bind("<FocusIn>", self.on_input_focus)
        self.text_input.insert(0, "Type your message or say 'Friday' to wake me...")
        self.text_input.configure(fg=self.colors['text_secondary'])
        
        # Control buttons
        self.create_control_buttons(input_frame)
    
    def create_control_buttons(self, parent):
        """Create enhanced control buttons"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        btn_frame.pack(side="right")
        
        # Send button
        self.send_btn = tk.Button(
            btn_frame,
            text="Send",
            command=self.send_message,
            bg=self.colors['success'],
            fg=self.colors['bg_primary'],
            font=("Arial", 10, "bold"),
            relief="flat",
            padx=20,
            cursor="hand2"
        )
        self.send_btn.pack(side="left", padx=(0, 5))
        
        # Voice button with better state indication
        self.voice_btn = tk.Button(
            btn_frame, 
            text="🎤",
            command=self.manual_voice_recording,
            bg=self.colors['warning'],
            fg=self.colors['bg_primary'],
            font=("Arial", 12, "bold"),
            relief="flat",
            width=4,
            cursor="hand2"
        )
        self.voice_btn.pack(side="left", padx=(0, 5))
        
        # Camera capture button
        self.camera_btn = tk.Button(
            btn_frame,
            text="📷",
            command=self.capture_and_analyze,
            bg=self.colors['highlight'],
            fg=self.colors['text_primary'],
            font=("Arial", 12, "bold"),
            relief="flat", 
            width=4,
            cursor="hand2"
        )
        self.camera_btn.pack(side="left", padx=(0, 5))
        
        # Clear chat button
        clear_btn = tk.Button(
            btn_frame,
            text="🗑️",
            command=self.clear_chat,
            bg=self.colors['error'],
            fg=self.colors['text_primary'],
            font=("Arial", 12, "bold"),
            relief="flat",
            width=4,
            cursor="hand2"
        )
        clear_btn.pack(side="left")
    
    def create_right_panel(self, parent):
        """Create right panel with video and system info"""
        # Wake word status section
        wake_frame = tk.LabelFrame(
            parent, 
            text="🎯 Wake Word Status", 
            bg=self.colors['bg_secondary'], 
            fg=self.colors['text_primary'],
            font=("Arial", 10, "bold")
        )
        wake_frame.pack(fill="x", padx=10, pady=10)
        
        self.wake_status_label = tk.Label(
            wake_frame,
            text="❌ Wake word disabled\nSay 'Friday' to activate",
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary'],
            font=("Arial", 10),
            justify="center"
        )
        self.wake_status_label.pack(padx=5, pady=5)
        
        # Video section
        video_frame = tk.LabelFrame(
            parent, 
            text="📹 Visual Input", 
            bg=self.colors['bg_secondary'], 
            fg=self.colors['text_primary'],
            font=("Arial", 10, "bold")
        )
        video_frame.pack(fill="x", padx=10, pady=10)
        
        # Video display frame - FIXED SIZE
        self.video_frame = tk.Frame(
            video_frame, 
            bg='black', 
            width=300, 
            height=225,
            relief=tk.SUNKEN,
            bd=2
        )
        self.video_frame.pack_propagate(False)  # Critical: prevents shrinking
        self.video_frame.pack(padx=5, pady=5)
        
        # Video display label
        self.video_label = tk.Label(
            self.video_frame,
            text="📷\nCamera Offline\n\nClick 'Start Camera' to begin",
            bg='black',
            fg='white',
            font=('Arial', 10),
            justify=tk.CENTER
        )
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Camera controls
        cam_control_frame = tk.Frame(video_frame, bg=self.colors['bg_secondary'])
        cam_control_frame.pack(pady=5)
        
        self.cam_toggle_btn = tk.Button(
            cam_control_frame,
            text="Start Camera",
            command=self.toggle_camera,
            bg=self.colors['bg_accent'],
            fg=self.colors['text_primary'],
            font=("Arial", 9, "bold"),
            relief="flat",
            cursor="hand2"
        )
        self.cam_toggle_btn.pack(side=tk.LEFT, padx=2)
        
        # Capture button
        self.capture_btn = tk.Button(
            cam_control_frame,
            text="Capture",
            command=self.capture_image,
            bg=self.colors['success'],
            fg=self.colors['bg_primary'],
            font=("Arial", 9, "bold"),
            relief="flat",
            state=tk.DISABLED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=2)
        
        # System info section
        self.create_system_info(parent)
    
    def create_system_info(self, parent):
        """Create system information panel"""
        info_frame = tk.LabelFrame(
            parent,
            text="ℹ️ System Status",
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=("Arial", 10, "bold")
        )
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.info_text = tk.Text(
            info_frame,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_secondary'],
            font=("Consolas", 9),
            height=6,
            state="disabled",
            wrap="word"
        )
        self.info_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Start periodic updates
        self.update_system_info()
    
    def toggle_camera(self):
        """Toggle camera on/off with proper error handling"""
        try:
            if not hasattr(self, 'video_engine') or not self.video_engine:
                from backend.core.video_engine import get_video_engine
                self.video_engine = get_video_engine()
                if not self.video_engine.initialize():
                    self.show_status("Failed to initialize video engine", "error")
                    return
        
            if self.video_engine.is_camera_active:
                # Stop camera
                self.video_engine.stop_camera()
                self.cam_toggle_btn.config(text="Start Camera", bg=self.colors['bg_accent'])
                self.capture_btn.config(state=tk.DISABLED)
                self.video_label.config(
                    text="📷\nCamera Offline\n\nClick 'Start Camera' to begin",
                    image=""
                )
                self.camera_active = False
                self.is_camera_active = False
                print("Camera stopped")
            
            else:
                # Start camera
                success = self.video_engine.start_camera(camera_index=0)
                if success:
                    # Set proper resolution
                    self.video_engine.set_frame_size(640, 480)
                
                    self.cam_toggle_btn.config(text="Stop Camera", bg=self.colors['error'])
                    self.capture_btn.config(state=tk.NORMAL)
                    self.camera_active = True
                    self.is_camera_active = True
                    
                    # Start video feed updates
                    self.update_video_feed()
                    print("Camera started")
                    self.add_system_message("✅ Camera started")
                else:
                    self.show_status("Failed to start camera", "error")
                
        except Exception as e:
            print(f"Camera toggle error: {e}")
            self.show_status(f"Camera error: {str(e)}", "error")

    def update_video_feed(self):
        """Update video feed with proper image scaling"""
        if not self.camera_active or not hasattr(self, 'video_engine') or not self.video_engine:
            return
    
        if self.video_engine and self.video_engine.is_camera_active:
            try:
                # Get frame from video engine
                pil_image = self.video_engine.capture_image_for_display()
            
                if pil_image:
                    # Resize to exact display dimensions
                    display_width = 296  # Slightly smaller than frame for padding
                    display_height = 221
                
                    # Resize while maintaining aspect ratio
                    img_width, img_height = pil_image.size
                    aspect = img_width / img_height
                
                    if aspect > display_width / display_height:
                        # Image is wider
                        new_width = display_width
                        new_height = int(display_width / aspect)
                    else:
                        # Image is taller
                        new_height = display_height
                        new_width = int(display_height * aspect)
                
                    pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(pil_image)
                
                    # Update display
                    self.video_label.configure(image=photo, text="")
                    self.video_label.image = photo  # Keep reference to prevent garbage collection
                
                else:
                    self.video_label.configure(
                        text="📷\nNo Signal\nChecking camera...",
                        image=""
                    )
                
            except Exception as e:
                print(f"Video update error: {e}")
                self.video_label.configure(
                    text=f"📷\nCamera Error\n{str(e)[:20]}...",
                    image=""
                )
    
        # Schedule next update (30 FPS)
        if self.camera_active:
            self.root.after(33, self.update_video_feed)

    def capture_image(self):
        """Capture current frame and optionally analyze with AI"""
        if not self.camera_active or not hasattr(self, 'video_engine'):
            self.show_status("Camera not active", "error")
            return
    
        try:
            # Capture image for AI analysis
            ai_image = self.video_engine.capture_image_for_ai()
            if ai_image:
                # Save the image
                timestamp = int(time.time())
                filename = f"friday_capture_{timestamp}.jpg"
                filepath = self.video_engine.save_frame(filename)
            
                if filepath:
                    self.show_status(f"Image captured: {filename}", "success")
                
                    # Optionally analyze with AI
                    analyze = messagebox.askyesno(
                        "Image Captured", 
                        "Image captured successfully!\nWould you like FRIDAY to analyze it?"
                    )    
                
                    if analyze:
                        self.analyze_captured_image(ai_image)
                else:
                    self.show_status("Failed to save captured image", "error")
            else:
                self.show_status("Failed to capture image", "error")
            
        except Exception as e:
            print(f"Image capture error: {e}")
            self.show_status(f"Capture error: {str(e)}", "error")

    def analyze_captured_image(self, image):
        """Analyze captured image with AI"""
        try:
            if hasattr(self, 'ai_engine') and self.ai_engine:
                # Ask user what they want to know about the image
                question = simpledialog.askstring(
                    "Image Analysis",
                    "What would you like FRIDAY to tell you about this image?",
                    initialvalue="What do you see in this image?"
                )
            
                if question:
                    # Show processing message
                    self.show_status("FRIDAY is analyzing the image...", "info")
                
                    # Analyze in separate thread
                    def analyze_thread():
                        try:
                            analysis = self.ai_engine.analyze_image(image, question)
                        
                            # Update UI in main thread
                            self.root.after(0, lambda: self.display_analysis_result(analysis))
                        
                        except Exception as e:
                            self.root.after(0, lambda: self.show_status(f"Analysis error: {e}", "error"))
                
                    threading.Thread(target=analyze_thread, daemon=True).start()
            else:
                self.show_status("AI engine not available", "error")
            
        except Exception as e:
            print(f"Image analysis error: {e}")
            self.show_status(f"Analysis error: {str(e)}", "error")

    def display_analysis_result(self, analysis: str):
        """Display AI analysis result"""
        # Add analysis to chat area
        self.add_message("friday", analysis)
    
        # Convert to speech
        if hasattr(self, 'ai_engine') and self.ai_engine:
            def speak_analysis():
                try:
                    audio_data = self.ai_engine.text_to_speech(analysis)
                    if audio_data and hasattr(self, 'audio_engine') and self.audio_engine:
                        self.audio_engine.play_audio_improved(audio_data)
                except Exception as e:
                    print(f"Speech error: {e}")
            
            threading.Thread(target=speak_analysis, daemon=True).start()
    
    def show_status(self, message, status_type="info"):
        """Show status message"""
        if hasattr(self, 'status_label') and self.status_label:
            color = {
                "info": "#00ff41",
                "error": "#ff4444",
                "success": "#00ff41",
                "warning": "#ffaa00"
            }.get(status_type, "#00ff41")
            
            self.status_var.set(message)
        else:
            print(f"Status ({status_type}): {message}")
    
    def initialize_components(self):
        """Initialize all components with progress feedback"""
        def init_thread():
            try:
                # AI Engine
                self.update_status("🔧 Initializing FRIDAY AI Engine...")
                if self.ai_engine.initialize():
                    self.add_system_message("✅ FRIDAY AI Engine online")
                    
                    # Test AI
                    if self.ai_engine.test_ai_response():
                        self.add_system_message("✅ AI response test passed")
                    else:
                        self.add_system_message("⚠️ AI response test failed")
                else:
                    self.add_system_message("❌ FRIDAY AI Engine initialization failed")
                    return
                
                # Audio Engine
                self.update_status("🔧 Initializing Audio Engine...")
                if self.audio_engine.initialize():
                    self.add_system_message("✅ Audio Engine online")
                else:
                    self.add_system_message("❌ Audio Engine initialization failed")
                
                # Wake Word Detector
                self.update_status("🔧 Initializing Friday Wake Word Detector...")
                if self.wake_detector.initialize():
                    self.add_system_message("✅ FRIDAY wake word detector ready")
                    self.add_system_message("🎯 Say 'Friday' to activate voice commands")
                else:
                    self.add_system_message("⚠️ Wake word detector initialization failed")
                
                # Video Engine
                self.update_status("🔧 Initializing Video Engine...")
                if self.video_engine.initialize():
                    self.add_system_message("✅ Video Engine online")
                else:
                    self.add_system_message("❌ Video Engine initialization failed")
                
                # Welcome message
                welcome_msg = "Hello! FRIDAY is online and ready to assist. Say 'Friday' followed by your command, or type messages below."
                self.add_message("friday", welcome_msg)
                
                # Convert welcome to speech
                self.speak_response(welcome_msg)
                
                # Enable wake word by default
                self.root.after(2000, self.enable_wake_word_automatically)
                
                self.update_status("👂 Listening for 'Friday'...")
                
            except Exception as e:
                self.add_system_message(f"❌ Initialization error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        threading.Thread(target=init_thread, daemon=True).start()
    
    def enable_wake_word_automatically(self):
        """Automatically enable wake word detection on startup"""
        if not self.wake_word_active:
            self.toggle_wake_word()
    
    def toggle_wake_word(self):
        """Toggle wake word detection on/off"""
        if not self.wake_detector.recognizer:
            messagebox.showwarning("Wake Word Not Available", 
                                 "Wake word detection not initialized. Please check your microphone.")
            return
        
        if not self.wake_word_active:
            # Start wake word detection
            if self.wake_detector.start_listening(self.on_wake_word_detected):
                self.wake_word_active = True
                self.wake_toggle_btn.configure(text="🎯 Disable Wake Word", bg=self.colors['error'])
                self.wake_status_label.configure(
                    text="✅ Wake word active\nSay 'Friday' to give commands",
                    fg=self.colors['success']
                )
                self.add_system_message("✅ Wake word detection enabled - say 'Friday' to activate")
                self.update_status("👂 Listening for 'Friday'...")
            else:
                self.add_system_message("❌ Failed to start wake word detection")
        else:
            # Stop wake word detection
            self.wake_detector.stop_listening()
            self.wake_word_active = False
            self.wake_toggle_btn.configure(text="🎯 Enable Wake Word", bg=self.colors['warning'])
            self.wake_status_label.configure(
                text="❌ Wake word disabled\nClick to enable listening",
                fg=self.colors['text_secondary']
            )
            self.add_system_message("⏹️ Wake word detection disabled")
            self.update_status("💤 Ready (wake word disabled)")
    
    def on_wake_word_detected(self):
        """Handle wake word detection"""
        print("🎯 FRIDAY wake word detected - starting voice recording")
        
        # Update UI to show wake word detected
        self.root.after(0, lambda: self.add_wake_word_message("🎯 Wake word detected - listening for command..."))
        
        # Start voice recording automatically
        self.root.after(0, self.start_automatic_voice_recording)
    
    def add_wake_word_message(self, message: str):
        """Add wake word detection message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{timestamp}] ", "timestamp")
        self.chat_display.insert("end", f"{message}\n\n", "wake")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def start_automatic_voice_recording(self):
        """Start voice recording automatically after wake word"""
        if self.is_recording:
            return  # Already recording
        
        self.is_recording = True
        self.voice_btn.configure(text="⏹️", bg=self.colors['error'])
        self.update_status("🎙️ Recording command... (will stop automatically)")
        
        threading.Thread(target=self._automatic_voice_recording, daemon=True).start()
    
    def _automatic_voice_recording(self):
        """Record voice command automatically with auto-stop"""
        try:
            # Record audio with longer timeout for commands
            audio_data = self.audio_engine.record_audio_improved(max_duration=8)
            
            # Reset UI
            self.root.after(0, lambda: self.voice_btn.configure(text="🎤", bg=self.colors['warning']))
            
            if audio_data and len(audio_data) > 2000:
                self.root.after(0, lambda: self.update_status("🔄 Processing your command..."))
                
                # Transcribe
                user_input = self.ai_engine.transcribe_audio(audio_data)
                
                if user_input and len(user_input.strip()) > 0:
                    print(f"✅ Command transcribed: '{user_input}'")
                    self.root.after(0, lambda: self.add_message("user", f"🎤 {user_input}"))
                    
                    # Process the command
                    threading.Thread(
                        target=self.process_message,
                        args=(user_input,),
                        daemon=True
                    ).start()
                else:
                    self.root.after(0, lambda: self.add_system_message("❌ Could not understand the command - try speaking more clearly"))
            else:
                self.root.after(0, lambda: self.add_system_message("❌ No clear audio recorded - try speaking louder"))
                
        except Exception as e:
            print(f"❌ Automatic voice recording error: {e}")
            self.root.after(0, lambda: self.add_system_message("❌ Voice recording failed"))
        finally:
            self.is_recording = False
            self.root.after(0, lambda: self.update_status("👂 Listening for 'Friday'..."))
    
    def manual_voice_recording(self):
        """Manual voice recording (backup method)"""
        if not self.audio_engine.is_initialized:
            messagebox.showwarning("Audio Not Available", 
                                 "Audio system not initialized. Check your microphone and speakers.")
            return
        
        if not self.is_recording:
            self.start_voice_recording()
        else:
            self.stop_voice_recording()
    
    def start_voice_recording(self):
        """Start voice recording with visual feedback"""
        self.is_recording = True
        self.voice_btn.configure(text="⏹️", bg=self.colors['error'])
        self.update_status("🎙️ Recording... (speak now, click to stop)")
        
        # Add recording indicator to chat
        self.add_recording_indicator()
        
        threading.Thread(target=self._record_voice_command, daemon=True).start()
    
    def stop_voice_recording(self):
        """Stop voice recording"""
        self.is_recording = False
        self.audio_engine.stop_recording()
        self.voice_btn.configure(text="🎤", bg=self.colors['warning'])
        self.update_status("🔄 Processing audio...")
    
    def _record_voice_command(self):
        """Record voice command with better error handling"""
        try:
            # Record audio
            audio_data = self.audio_engine.record_audio_improved(max_duration=10)
            
            # Reset UI
            self.root.after(0, lambda: self.voice_btn.configure(
                text="🎤", bg=self.colors['warning']))
            
            if audio_data and len(audio_data) > 2000:
                self.root.after(0, lambda: self.update_status("🔄 Transcribing audio..."))
                
                # Transcribe
                user_input = self.ai_engine.transcribe_audio(audio_data)
                
                if user_input and len(user_input.strip()) > 0:
                    print(f"✅ Transcribed: '{user_input}'")
                    self.root.after(0, lambda: self.add_message("user", f"🎤 {user_input}"))
                    self.process_message(user_input)
                else:
                    self.root.after(0, lambda: self.add_system_message("❌ Could not understand speech"))
            else:
                self.root.after(0, lambda: self.add_system_message("❌ No clear audio recorded"))
                
        except Exception as e:
            print(f"❌ Voice recording error: {e}")
            self.root.after(0, lambda: self.add_system_message("❌ Voice recording failed"))
        finally:
            self.is_recording = False
            self.root.after(0, lambda: self.update_status("👂 Listening for 'Friday'..." if self.wake_word_active else "💤 Ready"))
            self.root.after(0, self.remove_recording_indicator)
    
    def send_message(self, event=None):
        """Send text message with better validation"""
        message = self.text_input.get().strip()
        
        # Handle placeholder text
        if not message or message == "Type your message or say 'Friday' to wake me...":
            return
        
        self.text_input.delete(0, "end")
        self.text_input.insert(0, "Type your message or say 'Friday' to wake me...")
        self.text_input.configure(fg=self.colors['text_secondary'])
        
        self.add_message("user", message)
        
        # Process message in background
        threading.Thread(
            target=self.process_message,
            args=(message,),
            daemon=True
        ).start()
    
    def process_message(self, message: str):
        """Process user message with AI-driven intent recognition"""
        self.update_status("🤔 Thinking...")
    
        try:
            # Quick intent analysis for common patterns
            message_lower = message.lower().strip()
        
            # Check for camera-related requests
            camera_keywords = ['camera', 'see', 'look', 'view', 'visual', 'watch', 'observe']
            control_keywords = ['open', 'start', 'enable', 'activate', 'turn on', 'close', 'stop', 'disable']
            analysis_keywords = ['what do you see', 'describe', 'analyze', 'look around', 'tell me what', 'show me what']
        
            has_camera_word = any(word in message_lower for word in camera_keywords)
            has_control_word = any(word in message_lower for word in control_keywords)
            has_analysis_word = any(phrase in message_lower for phrase in analysis_keywords)
        
            # Handle camera control
            if has_camera_word and has_control_word:
                response = self.handle_camera_control(message)
                if response:
                    self.add_message("friday", response)
                    self.speak_response(response)
                    return
        
            # Handle visual analysis requests
            elif has_camera_word and (has_analysis_word or any(word in message_lower for word in ['see', 'look', 'view'])):
                self.handle_visual_analysis(message)
                return
        
            # Handle other system commands
            elif self.is_enhanced_system_command(message):
                response = self.handle_enhanced_system_commands(message)
                if response:
                    self.add_message("friday", response)
                    self.speak_response(response)
                    return
        
            # Normal AI conversation
            response = self.ai_engine.get_response(message)
            self.add_message("friday", response)
            self.speak_response(response)
        
        except Exception as e:
            error_msg = f"I apologize, I encountered an error: {str(e)}"
            self.add_message("friday", error_msg)
            print(f"❌ Message processing error: {e}")
        finally:
            status = "👂 Listening for 'Friday'..." if self.wake_word_active else "💤 Ready"
            self.update_status(status)
    
    def is_enhanced_system_command(self, message: str) -> bool:
        """Enhanced system command detection"""
        message_lower = message.lower().strip()
        
        # Enhanced command patterns
        command_patterns = [
            # YouTube commands
            'play', 'watch', 'show me', 'search for',
            # Browser commands  
            'open', 'go to', 'browse', 'visit',
            # System commands
            'open settings', 'show settings', 'control panel',
            'open calculator', 'open notepad', 'open paint',
            # Search commands
            'search google', 'google search', 'look up'
        ]
        
        # Check if message contains command indicators
        has_command = any(pattern in message_lower for pattern in command_patterns)
        
        # Avoid treating questions as commands
        question_words = ['what is', 'tell me about', 'explain', 'how does', 'why does']
        is_question = any(q in message_lower for q in question_words)
        
        return has_command and not is_question
    
    def handle_enhanced_system_commands(self, message: str) -> Optional[str]:
        """Handle enhanced system commands"""
        message_lower = message.lower().strip()
        
        try:
            # YouTube commands
            if any(cmd in message_lower for cmd in ['play', 'watch']) and 'youtube' not in message_lower:
                # Extract what to play
                search_terms = message_lower.replace('play', '').replace('watch', '').replace('show me', '').strip()
                if search_terms:
                    return self.system_controller.play_youtube_video(search_terms)
                else:
                    return self.system_controller.open_website("youtube.com")
            
            # Direct YouTube search
            elif 'youtube' in message_lower:
                if any(cmd in message_lower for cmd in ['search', 'look up', 'find']):
                    search_terms = message_lower.split('youtube')[-1].strip()
                    if search_terms:
                        return self.system_controller.search_youtube(search_terms)
                else:
                    return self.system_controller.open_website("youtube.com")
            
            # Google search commands
            elif any(cmd in message_lower for cmd in ['google search', 'search google', 'search for']):
                search_terms = message_lower.replace('google search', '').replace('search google', '').replace('search for', '').strip()
                if search_terms:
                    return self.system_controller.search_web(search_terms, "google")
                else:
                    return self.system_controller.open_website("google.com")
            
            # Website commands
            elif any(cmd in message_lower for cmd in ['open', 'go to', 'browse', 'visit']):
                # Extract website name
                for cmd in ['open', 'go to', 'browse to', 'visit']:
                    if cmd in message_lower:
                        site = message_lower.replace(cmd, '').strip()
                        if site:
                            return self.system_controller.open_specific_website(site)
            
            # Application commands
            elif any(cmd in message_lower for cmd in ['calculator', 'notepad', 'paint', 'settings', 'cmd', 'task manager', 'explorer']):
                app_name = None
                if 'calculator' in message_lower:
                    app_name = "calculator"
                elif 'notepad' in message_lower:
                    app_name = "notepad"
                elif 'paint' in message_lower:
                    app_name = "paint"
                elif 'settings' in message_lower:
                    app_name = "settings"
                elif 'cmd' in message_lower or 'command prompt' in message_lower:
                    app_name = "cmd"
                elif 'task manager' in message_lower:
                    app_name = "task manager"
                elif 'explorer' in message_lower or 'files' in message_lower:
                    app_name = "file explorer"
                
                if app_name:
                    return self.system_controller.open_application(app_name)
        except Exception as e:
            print(f"Command handling error: {e}")
            return None
        
        return None
    
    def handle_visual_analysis(self, original_message: str):
        """Handle any request that involves visual analysis"""
    
        # Ensure camera is active
        if not self.is_camera_active:
            self.toggle_camera()
            time.sleep(2)
    
        if self.is_camera_active:
            image = self.video_engine.capture_image_for_ai()
            if image:
                # Let AI determine what specific analysis to do
                analysis = self.ai_engine.analyze_image(image, original_message)
                self.add_message("friday", analysis)
                self.speak_response(analysis)
            else:
                response = "I'm having trouble capturing an image from the camera."
                self.add_message("friday", response)
                self.speak_response(response)
        else:
            response = "I cannot access the camera right now."
            self.add_message("friday", response)
            self.speak_response(response)    

    def handle_camera_control(self, message: str):
        """Handle camera control commands"""
        message_lower = message.lower().strip()
    
        if any(cmd in message_lower for cmd in ['open', 'start', 'enable', 'turn on']):
            if not self.is_camera_active:
                self.toggle_camera()
                return "Camera activated. I can now see what's in front of me."
            else:
                return "Camera is already active and ready."
        elif any(cmd in message_lower for cmd in ['close', 'stop', 'disable', 'turn off']):
            if self.is_camera_active:
                self.toggle_camera()
                return "Camera deactivated."
            else:
                return "Camera is already off."
    
        return "I'm not sure what you want me to do with the camera."

    def speak_response(self, text: str):
        """Convert response to speech with better error handling"""
        if self.is_speaking:
            return  # Don't overlap speech
        
        def speak_async():
            try:
                self.is_speaking = True
                self.root.after(0, lambda: self.update_status("🗣️ FRIDAY speaking..."))
                
                print(f"🔊 Converting to speech: '{text[:50]}{'...' if len(text) > 50 else ''}'")
                
                audio_data = self.ai_engine.text_to_speech(text)
                if audio_data:
                    success = self.audio_engine.play_audio_improved(audio_data)
                    if not success:
                        self.root.after(0, lambda: self.add_system_message("⚠️ Speech playback failed"))
                else:
                    self.root.after(0, lambda: self.add_system_message("⚠️ Speech generation failed"))
                    
            except Exception as e:
                print(f"❌ Speech error: {e}")
                self.root.after(0, lambda: self.add_system_message("❌ Speech system error"))
            finally:
                self.is_speaking = False
                status = "👂 Listening for 'Friday'..." if self.wake_word_active else "💤 Ready"
                self.root.after(0, lambda: self.update_status(status))
        
        threading.Thread(target=speak_async, daemon=True).start()
    
    def capture_and_analyze(self):
        """Capture image and analyze with better error handling"""
        if not self.video_engine.is_camera_active:
            messagebox.showinfo("Camera Not Active", "Please enable camera first using the 'Start Camera' button.")
            return
        
        image = self.video_engine.capture_image_for_ai()
        if not image:
            self.add_system_message("❌ Failed to capture image")
            return
        
        # Ask what to analyze
        question = simpledialog.askstring(
            "Image Analysis", 
            "What would you like to know about this image?",
            initialvalue="What do you see in this image?"
        )
        
        if question:
            self.add_message("user", f"📷 {question}")
            
            # Analyze in background
            threading.Thread(
                target=self._analyze_image,
                args=(image, question),
                daemon=True
            ).start()
    
    def _analyze_image(self, image: Image.Image, question: str):
        """Analyze image with AI"""
        self.update_status("👁️ Analyzing image...")
        
        try:
            response = self.ai_engine.analyze_image(image, question)
            self.add_message("friday", response)
            self.speak_response(response)
        except Exception as e:
            error_msg = f"Image analysis failed: {str(e)}"
            self.add_system_message(error_msg)
        finally:
            status = "👂 Listening for 'Friday'..." if self.wake_word_active else "💤 Ready"
            self.update_status(status)
    
    def clear_chat(self):
        """Clear chat and conversation history"""
        if messagebox.askyesno("Clear Chat", "Clear conversation history?"):
            self.chat_display.configure(state="normal")
            self.chat_display.delete(1.0, "end")
            self.chat_display.configure(state="disabled")
            
            self.ai_engine.clear_history()
            self.add_system_message("🗑️ Conversation cleared")
    
    def add_message(self, sender: str, message: str):
        """Add message to chat display with enhanced formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state="normal")
        
        # Add timestamp
        self.chat_display.insert("end", f"[{timestamp}] ", "timestamp")
        
        # Add sender and message
        if sender == "user":
            self.chat_display.insert("end", "👤 You: ", "user")
            self.chat_display.insert("end", f"{message}\n\n")
        elif sender == "friday":
            self.chat_display.insert("end", "🤖 FRIDAY: ", "friday")
            self.chat_display.insert("end", f"{message}\n\n")
        
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def add_system_message(self, message: str):
        """Add system message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{timestamp}] ", "timestamp")
        self.chat_display.insert("end", f"🔧 System: {message}\n\n", "system")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def add_recording_indicator(self):
        """Add visual recording indicator"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{timestamp}] ", "timestamp")
        self.chat_display.insert("end", "🎤 Recording... (speak now)\n\n", "speaking")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def remove_recording_indicator(self):
        """Remove recording indicator"""
        try:
            self.chat_display.configure(state="normal")
            content = self.chat_display.get("1.0", "end")
            lines = content.split('\n')
            
            if lines and "Recording..." in lines[-3]:
                self.chat_display.delete("end-3l", "end-1l")
            
            self.chat_display.configure(state="disabled")
        except:
            pass
    
    def update_status(self, status: str):
        """Update status display"""
        self.status_var.set(status)
    
    def update_system_info(self):
        """Update system information display"""
        try:
            from backend.core.audio_engine import HAS_AUDIO
            from backend.core.video_engine import HAS_VIDEO
            import platform
            
            audio_info = self.audio_engine.get_audio_info() if self.audio_engine else {}
            
            info = f"""🔊 Audio: {'✅ Ready' if HAS_AUDIO and self.audio_engine.is_initialized else '❌ Not Ready'}
📹 Video: {'✅ Ready' if HAS_VIDEO and self.video_engine.is_initialized else '❌ Not Ready'}
🎯 Wake Word: {'🟢 Active' if self.wake_word_active else '⚪ Inactive'}
📷 Camera: {'🟢 Active' if self.is_camera_active else '⚪ Inactive'}

🤖 AI Engine: {'🟢 Ready' if self.ai_engine.is_initialized else '❌ Not Ready'}
🎙️ Audio Engine: {'🟢 Ready' if self.audio_engine and self.audio_engine.is_initialized else '❌ Not Ready'}
📺 Video Engine: {'🟢 Ready' if self.video_engine and self.video_engine.is_initialized else '❌ Not Ready'}
🎯 Wake Detector: {'🟢 Ready' if self.wake_detector.recognizer else '❌ Not Ready'}

🕐 Time: {datetime.now().strftime('%H:%M:%S')}
📅 Date: {datetime.now().strftime('%Y-%m-%d')}
💻 Platform: {platform.system()}

💬 Conversation: {len(self.ai_engine.conversation_history) if self.ai_engine else 0} exchanges
🗣️ Speaking: {'Yes' if self.is_speaking else 'No'}
🎤 Recording: {'Yes' if self.is_recording else 'No'}"""
            
            if audio_info:
                info += f"\n\n🎵 Audio Details:"
                info += f"\n   TTS Mode: {self.ai_engine.tts_mode if hasattr(self.ai_engine, 'tts_mode') else 'Unknown'}"
                info += f"\n   Sample Rate: {audio_info.get('sample_rate', 'Unknown')}"
                if 'default_input' in audio_info:
                    info += f"\n   Input: {audio_info['default_input'][:20]}..."
            
            self.info_text.configure(state="normal")
            self.info_text.delete(1.0, "end")
            self.info_text.insert(1.0, info)
            self.info_text.configure(state="disabled")
            
        except Exception as e:
            print(f"❌ System info update error: {e}")
        
        # Schedule next update
        self.root.after(3000, self.update_system_info)
    
    def on_input_focus(self, event):
        """Handle input focus - clear placeholder text"""
        current_text = self.text_input.get()
        if current_text == "Type your message or say 'Friday' to wake me...":
            self.text_input.delete(0, "end")
            self.text_input.configure(fg=self.colors['text_primary'])
    
    def on_closing(self):
        """Handle window closing with confirmation"""
        if messagebox.askokcancel("Quit FRIDAY", "Are you sure you want to quit FRIDAY?"):
            self.cleanup()
            self.root.destroy()
    
    def cleanup(self):
        """Cleanup all resources"""
        print("🔧 Shutting down FRIDAY...")
        
        # Stop all operations
        self.is_camera_active = False
        self.is_recording = False
        self.is_speaking = False
        self.wake_word_active = False
        
        # Cleanup engines
        try:
            if self.wake_detector:
                self.wake_detector.stop_listening()
            if self.audio_engine:
                self.audio_engine.cleanup()
            if self.video_engine:
                self.video_engine.cleanup()
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
        
        print("👋 FRIDAY offline")
    
    def run(self):
        """Run the application with error handling"""
        try:
            print("🚀 Starting FRIDAY GUI...")
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n⏹️ Interrupted by user")
        except Exception as e:
            print(f"❌ Application error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()