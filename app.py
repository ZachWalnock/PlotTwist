from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from llm import ask_real_estate_agent
import uvicorn
import os

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
    """
    Analyze a property for real estate development opportunities.
    
    Args:
        request: PropertyRequest containing property information
        
    Returns:
        PropertyResponse containing the analysis
    """
    try:
        analysis = ask_real_estate_agent(request.property_info)
        return PropertyResponse(analysis=analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing property: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "PlotTwist Real Estate Analyzer"}

@app.get("/info")
async def app_info():
    """Application information for hackathon demo"""
    return {
        "name": "PlotTwist",
        "description": "AI-powered real estate development opportunity analyzer",
        "version": "1.0.0",
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

