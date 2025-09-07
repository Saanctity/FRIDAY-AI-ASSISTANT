"""
Video Engine for JARVIS
Handles camera input and video processing
"""

import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
import threading
import time

from backend.config.settings import get_settings

# Video imports with graceful fallback
try:
    import cv2
    HAS_VIDEO = True
except ImportError:
    print("OpenCV not available - camera features disabled")
    HAS_VIDEO = False
    cv2 = None

class VideoEngine:
    """Handles camera input and video processing for JARVIS"""
    
    def __init__(self):
        self.settings = get_settings()
        self.camera = None
        self.is_camera_active = False
        self.is_initialized = False
        self.current_frame = None
        self.capture_thread = None
        self.capture_lock = threading.Lock()
        
        # Camera settings
        self.camera_index = 0
        self.frame_width = 640
        self.frame_height = 480
        self.fps = 30
        
    def initialize(self) -> bool:
        """Initialize video engine"""
        if not HAS_VIDEO:
            print("⚠️ OpenCV not available - camera features disabled")
            return False
            
        if not self.settings.enable_video:
            print("⚠️ Video disabled in settings")
            return False
            
        try:
            self.is_initialized = True
            print("✅ Video engine initialized")
            return True
            
        except Exception as e:
            print(f"❌ Video initialization error: {e}")
            return False
    
    def start_camera(self, camera_index: int = 0) -> bool:
        """Start camera capture"""
        if not self.is_initialized:
            print("⚠️ Video engine not initialized")
            return False
            
        try:
            self.camera_index = camera_index
            self.camera = cv2.VideoCapture(camera_index)
            
            if not self.camera.isOpened():
                print(f"❌ Cannot open camera {camera_index}")
                return False
            
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.fps)
            
            self.is_camera_active = True
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            print(f"✅ Camera {camera_index} started")
            return True
            
        except Exception as e:
            print(f"❌ Camera start error: {e}")
            return False
    
    def stop_camera(self):
        """Stop camera capture"""
        if not self.is_camera_active:
            return
            
        self.is_camera_active = False
        
        # Wait for capture thread to finish
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.camera = None
        
        with self.capture_lock:
            self.current_frame = None
        
        print("⏹️ Camera stopped")
    
    def _capture_loop(self):
        """Continuous capture loop"""
        while self.is_camera_active and self.camera:
            try:
                ret, frame = self.camera.read()
                if ret:
                    with self.capture_lock:
                        self.current_frame = frame
                else:
                    print("⚠️ Failed to capture frame")
                    time.sleep(0.1)
            except Exception as e:
                print(f"Capture loop error: {e}")
                break
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture current frame"""
        if not self.is_camera_active or not self.camera:
            return None
        
        with self.capture_lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        
        return None
    
    def capture_image_for_ai(self) -> Optional[Image.Image]:
        """Capture image formatted for AI processing"""
        frame = self.capture_frame()
        if frame is None:
            return None
        
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)
            
            return pil_image
            
        except Exception as e:
            print(f"Image conversion error: {e}")
            return None
    
    def capture_image_for_display(self) -> Optional[Image.Image]:
        """Capture image formatted for GUI display with proper sizing"""
        frame = self.capture_frame()
        if frame is None:
            return None
    
        try:
            # Don't resize here - let the GUI handle sizing
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
            # Convert to PIL Image
            pil_image = Image.fromarray(rgb_frame)
        
            return pil_image
        
        except Exception as e:
            print(f"Display image conversion error: {e}")
            return None
    
    def save_frame(self, filename: str = None) -> Optional[str]:
        """Save current frame to file"""
        frame = self.capture_frame()
        if frame is None:
            return None
        
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"capture_{timestamp}.jpg"
            
            filepath = f"{self.settings.temp_dir}/{filename}"
            cv2.imwrite(filepath, frame)
            
            print(f"✅ Frame saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Save frame error: {e}")
            return None
    
    def get_camera_info(self) -> dict:
        """Get camera information"""
        if not self.camera:
            return {}
        
        try:
            info = {
                'index': self.camera_index,
                'width': int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': int(self.camera.get(cv2.CAP_PROP_FPS)),
                'active': self.is_camera_active
            }
            return info
        except:
            return {'active': False}
    
    def list_cameras(self) -> list:
        """List available cameras"""
        cameras = []
        
        if not HAS_VIDEO:
            return cameras
        
        # Test camera indices 0-4
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cameras.append({
                        'index': i,
                        'name': f"Camera {i}",
                        'available': True
                    })
                    cap.release()
                else:
                    cameras.append({
                        'index': i,
                        'name': f"Camera {i}",
                        'available': False
                    })
            except:
                continue
        
        return cameras
    
    def test_camera(self, camera_index: int = 0) -> bool:
        """Test if camera is working"""
        if not HAS_VIDEO:
            return False
        
        try:
            test_camera = cv2.VideoCapture(camera_index)
            if test_camera.isOpened():
                ret, frame = test_camera.read()
                test_camera.release()
                return ret and frame is not None
            return False
        except:
            return False
    
    def apply_filter(self, frame: np.ndarray, filter_type: str = "none") -> np.ndarray:
        """Apply filter to frame"""
        if frame is None:
            return None
        
        try:
            if filter_type == "gray":
                return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            elif filter_type == "blur":
                return cv2.GaussianBlur(frame, (15, 15), 0)
            elif filter_type == "edge":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                return cv2.Canny(gray, 50, 150)
            else:
                return frame
        except Exception as e:
            print(f"Filter error: {e}")
            return frame
    
    def get_frame_dimensions(self) -> Tuple[int, int]:
        """Get current frame dimensions"""
        if self.camera:
            width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return self.frame_width, self.frame_height
    
    def set_frame_size(self, width: int, height: int) -> bool:
        """Set camera frame size"""
        if not self.camera:
            return False
        
        try:
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.frame_width = width
            self.frame_height = height
            return True
        except Exception as e:
            print(f"Set frame size error: {e}")
            return False
    
    def cleanup(self):
        """Cleanup video resources"""
        print("🔧 Cleaning up video engine...")
        self.stop_camera()
        self.is_initialized = False
        print("✅ Video engine cleanup complete")

# Global instance
_video_engine = None

def get_video_engine() -> VideoEngine:
    """Get global video engine instance"""
    global _video_engine
    if _video_engine is None:
        _video_engine = VideoEngine()
    return _video_engine