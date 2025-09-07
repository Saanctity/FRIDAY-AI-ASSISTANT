"""
FRIDAY Web API - Simple Backend for hosting
Lightweight API wrapper that uses existing AI engine
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import logging
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="FRIDAY Web API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple AI Engine for web (without desktop dependencies)
class WebAIEngine:
    """Simplified AI engine for web use"""
    
    def __init__(self):
        self.model = None
        self.conversation_history = []
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize AI engine"""
        try:
            import google.generativeai as genai
            
            # Get API key from environment
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("GEMINI_API_KEY not found in environment")
                return False
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_initialized = True
            
            logger.info("✅ FRIDAY Web AI initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ AI initialization error: {e}")
            return False
    
    def get_response(self, user_input: str) -> str:
        """Generate AI response with enhanced reasoning"""
        if not self.model:
            return "AI engine not initialized"
        
        try:
            # Add to history
            self.conversation_history.append(("user", user_input))
        
            # Enhanced reasoning prompt
            system_prompt = f"""You are FRIDAY (Female Replacement Intelligent Digital Assistant Youth), an advanced AI assistant with sophisticated reasoning capabilities. You are:

- Highly intelligent with strong analytical and reasoning abilities
- Able to break down complex problems and provide step-by-step solutions
- Capable of understanding context, implications, and nuanced requests
- Proactive in offering relevant follow-up information or suggestions
- Skilled at connecting different concepts and providing comprehensive insights

When responding:
- Use logical reasoning to understand the true intent behind requests
- Provide thorough, well-reasoned answers that anticipate user needs
- Offer multiple perspectives when relevant
- Explain your reasoning process when helpful
- Be proactive in suggesting related information or next steps
- Adapt your communication style to match the complexity of the topic

Context from recent conversation:
{self._get_conversation_context()}

Current user request: {user_input}

Think through this request carefully and provide an intelligent, reasoned response."""

            response = self.model.generate_content(system_prompt)
            ai_response = response.text.strip()
        
            # Add to history
            self.conversation_history.append(("assistant", ai_response))
        
            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        
            return ai_response
        
        except Exception as e:
            logger.error(f"AI response error: {e}")
            return "I'm experiencing technical difficulties while processing your request."
    def _get_conversation_context(self) -> str:
        """Get relevant conversation context"""
        if len(self.conversation_history) < 2:
            return "This is the beginning of our conversation."
    
        recent = self.conversation_history[-4:]  # Last 2 exchanges
        context = "Recent conversation:\n"
        for role, message in recent:
            context += f"{role.title()}: {message[:100]}{'...' if len(message) > 100 else ''}\n"
    
        return context
    
    def analyze_image(self, image: Image.Image, question: str) -> str:
        """Analyze image with AI"""
        try:
            prompt = f"""You are FRIDAY, an advanced AI assistant. Analyze this image and answer: {question}

Provide a detailed but conversational analysis. Be professional but friendly."""
            
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"❌ Image analysis error: {e}")
            return "I'm having trouble analyzing this image."

# Initialize AI engine
ai_engine = WebAIEngine()

# Request/Response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# Initialize on startup
@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting FRIDAY Web API...")
    if ai_engine.initialize():
        logger.info("✅ FRIDAY Web API ready!")
    else:
        logger.error("❌ Failed to initialize AI")

# API Routes
@app.get("/")
async def root():
    return {"message": "FRIDAY Web API is online", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    if ai_engine.is_initialized:
        return {"status": "healthy", "message": "FRIDAY is operational"}
    else:
        raise HTTPException(status_code=503, detail="AI not initialized")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        if not ai_engine.is_initialized:
            raise HTTPException(status_code=503, detail="AI not available")
        
        response = ai_engine.get_response(request.message)
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    question: str = Form("What do you see in this image?")
):
    try:
        if not ai_engine.is_initialized:
            raise HTTPException(status_code=503, detail="AI not available")
        
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Analyze
        analysis = ai_engine.analyze_image(image, question)
        return ChatResponse(response=analysis)
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-chat")
async def clear_chat():
    if ai_engine:
        ai_engine.conversation_history = []
        return {"message": "Chat cleared", "status": "success"}
    raise HTTPException(status_code=503, detail="AI not available")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)