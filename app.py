from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm import ask_real_estate_agent
import uvicorn

app = FastAPI(title="Real Estate Agent API", description="API for real estate development analysis")

class PropertyRequest(BaseModel):
    property_info: str

class PropertyResponse(BaseModel):
    analysis: str

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
    """Health check endpoint"""
    return {"status": "healthy"}

