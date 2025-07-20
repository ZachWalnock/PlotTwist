from fastapi import FastAPI, HTTPException
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
        return f"PlotTwist API Analysis for: {property_info}\n\nThis is the backend API. Full AI analysis requires API keys.\n\nProperty: {property_info}\nStatus: API mode - placeholder analysis.\n\nTo enable full analysis, set GOOGLE_API_KEY environment variable."

app = FastAPI(title="PlotTwist API - Backend", 
              description="Backend API for real estate development opportunity analysis")

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this with your Next.js domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PropertyRequest(BaseModel):
    property_info: str

class PropertyResponse(BaseModel):
    analysis: str

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
    """API information and capabilities"""
    return {
        "name": "PlotTwist API",
        "description": "Backend API for real estate development opportunity analysis",
        "version": "1.0.0",
        "llm_available": LLM_AVAILABLE,
        "features": [
            "Property data extraction from Boston Assessment records",
            "Zoning analysis and development potential assessment",
            "Market intelligence and neighborhood analysis", 
            "AI-powered strategic recommendations",
            "Development feasibility scoring"
        ],
        "endpoints": {
            "analyze": "/create-report",
            "health": "/health",
            "info": "/info"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

