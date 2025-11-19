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
        
            # Try multiple model names as fallback
            model_names = [
                'gemini-1.5-flash-latest',
                'gemini-1.5-flash',
                'gemini-pro'
            ]
        
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    logger.info(f"✅ Using model: {model_name}")
                    self.is_initialized = True
                    return True
                except Exception as e:
                    logger.warning(f"Model {model_name} failed: {e}")
                    continue
        
            logger.error("❌ No working model found")
            return False
        
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
        
            # MUCH SIMPLER prompt - direct conversation style
            system_prompt = f"""You are FRIDAY, Tony Stark's AI assistant. You are intelligent, helpful, and conversational.

IMPORTANT GUIDELINES:
- Respond directly to the user in first person
- Keep responses natural and conversational 
- Don't analyze the user's request or explain your reasoning process
- Don't refer to "the user" - speak directly to them
- Be concise unless they ask for detailed explanations
- Maintain FRIDAY's professional but friendly personality

User says: {user_input}

Respond naturally as FRIDAY:"""

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
            return "I'm experiencing technical difficulties at the moment."
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

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    question: str = Form("What do you see in this image?")
):
    try:
        logger.info(f"Received image analysis request: {file.filename}, question: {question}")
        
        if not ai_engine.is_initialized:
            raise HTTPException(status_code=503, detail="AI not available")
        
        # Validate file type and size
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        image_data = await file.read()
        logger.info(f"Image size: {len(image_data)} bytes")
        
        if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="Image too large")
        
        # Process image
        try:
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        
        # Analyze
        analysis = ai_engine.analyze_image(image, question)
        logger.info(f"Analysis completed successfully")
        
        return ChatResponse(response=analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

@app.get("/api/list-models")
async def list_models():
    try:
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name)
        
        return {"models": models}
    except Exception as e:
        return {"error": str(e)}