import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Add backend directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent))

from prompt_optimizer import enhance_prompt, optimize_prompt_for_search
from image_generator import ImageGenerator
from internet_image_search import InternetImageSearcher

app = FastAPI(
    title="VoiToImg API",
    description="Voice & Text-Driven Photorealistic Image Generation & Global Web Image Search API",
    version="1.1.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
image_generator = ImageGenerator()
internet_searcher = InternetImageSearcher()

# Request Models
class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="User input prompt from voice agent or text bar")
    style_preset: str = Field(default="real_photo", description="Style preset e.g. real_photo, cinematic, studio_portrait, landscape, architecture")
    aspect_ratio: str = Field(default="1:1", description="Aspect ratio: 1:1, 16:9, 9:16, 4:3, 3:4")
    enhance: bool = Field(default=True, description="Whether to apply photorealistic prompt enhancement")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional dynamic Gemini API Key")

class EnhancePromptRequest(BaseModel):
    prompt: str
    style_preset: str = "real_photo"
    gemini_api_key: Optional[str] = None

class InternetSearchRequest(BaseModel):
    prompt: str = Field(..., description="User input search query or voice command")
    limit: int = Field(default=20, ge=1, le=60, description="Max number of images to return from the internet")
    enhance: bool = Field(default=True, description="Whether to optimize prompt for search engine query using Gemini LLM")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional dynamic Gemini API Key")

# API Endpoints
@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "VoiToImg API",
        "provider": os.getenv("IMAGE_API_PROVIDER", "gemini"),
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "internet_search_enabled": True
    }

@app.post("/api/enhance-prompt")
def api_enhance_prompt(req: EnhancePromptRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    enhanced = enhance_prompt(req.prompt, req.style_preset, req.gemini_api_key)
    return {
        "original_prompt": req.prompt,
        "enhanced_prompt": enhanced,
        "style_preset": req.style_preset
    }

@app.post("/api/generate")
def api_generate_image(req: GenerateRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    
    # 1. Enhance prompt if requested
    final_prompt = enhance_prompt(req.prompt, req.style_preset, req.gemini_api_key) if req.enhance else req.prompt
    
    try:
        # 2. Generate image
        result = image_generator.generate(
            prompt=final_prompt,
            aspect_ratio=req.aspect_ratio,
            gemini_key=req.gemini_api_key
        )
        result["original_prompt"] = req.prompt
        result["enhanced_prompt"] = final_prompt
        return result
    except Exception as e:
        print(f"[API Error] Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

@app.post("/api/search-internet-images")
def api_search_internet_images(req: InternetSearchRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    
    # 1. Optimize search query using Gemini LLM or NLP fallback if requested
    search_info = optimize_prompt_for_search(req.prompt, req.gemini_api_key) if req.enhance else {"search_query": req.prompt.strip(), "method": "raw"}
    target_query = search_info.get("search_query") or req.prompt.strip()

    try:
        # 2. Query total internet for images matching the query
        search_res = internet_searcher.search(target_query, limit=req.limit)
        search_res["original_prompt"] = req.prompt
        search_res["optimized_query"] = target_query
        search_res["optimization_method"] = search_info.get("method", "raw")
        return search_res
    except Exception as e:
        print(f"[API Error] Internet image search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internet image search failed: {str(e)}")


# Mount static files for frontend if frontend directory exists
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
def serve_index():
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse({
        "message": "VoiToImg Backend API is running.",
        "documentation": "/docs",
        "health": "/api/health"
    })

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    print(f"🚀 Starting VoiToImg FastAPI Backend at http://{host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug)
