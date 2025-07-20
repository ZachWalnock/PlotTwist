from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

# Try to import LLM function with fallback
try:
    from llm import ask_real_estate_agent
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"LLM import failed: {e}")
    LLM_AVAILABLE = False
    def ask_real_estate_agent(property_info):
        return f"PlotTwist Demo Analysis for: {property_info}\n\nThis is a demo version. Full AI analysis requires API keys.\n\nProperty: {property_info}\nStatus: Demo mode - showing placeholder analysis.\n\nTo enable full analysis, set GOOGLE_API_KEY environment variable."

app = FastAPI(title="PlotTwist - Real Estate Development Analyzer", 
              description="AI-powered API for real estate development opportunity analysis")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class PropertyRequest(BaseModel):
    property_info: str

class PropertyResponse(BaseModel):
    analysis: str

@app.get("/")
async def read_root():
    """Serve the demo HTML page"""
    return FileResponse('static/index.html')

@app.post("/create-report", response_model=PropertyResponse)
async def create_report(request: PropertyRequest):
    try:
        analysis = ask_real_estate_agent(request.property_info)
        return PropertyResponse(analysis=analysis)
    except Exception as e:
        # Return a demo response instead of failing
        demo_analysis = f"""
# PlotTwist Analysis - Demo Mode

## Property: {request.property_info}

### Status: Demo Version
This is a demonstration of the PlotTwist system. The full AI-powered analysis requires API keys.

### What PlotTwist Can Do:
- ✅ Real property data extraction from Boston Assessment records  
- ✅ Zoning analysis and development potential assessment
- ✅ Market intelligence and neighborhood analysis
- ✅ AI-powered strategic recommendations using Google Gemini
- ✅ Development feasibility scoring and FAR calculations

### Sample Output:
**Property Type:** Residential
**Development Potential:** Medium-High  
**Estimated Value:** Contact for full analysis
**Strategic Recommendation:** Full analysis available with API setup

**Error Details (for debugging):** {str(e)}
        """
        return PropertyResponse(analysis=demo_analysis.strip())

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy", 
        "service": "PlotTwist Real Estate Analyzer",
        "llm_available": LLM_AVAILABLE,
        "demo_mode": not LLM_AVAILABLE
    }

@app.get("/info")
async def app_info():
    """Application information for hackathon demo"""
    return {
        "name": "PlotTwist",
        "description": "AI-powered real estate development opportunity analyzer",
        "version": "1.0.0",
        "demo_mode": not LLM_AVAILABLE,
        "features": [
            "Property data extraction from Boston Assessment records",
            "Zoning analysis and development potential assessment",
            "Market intelligence and neighborhood analysis", 
            "AI-powered strategic recommendations",
            "Development feasibility scoring"
        ],
        "endpoints": {
            "demo": "/",
            "analyze": "/create-report",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

