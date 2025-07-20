from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from main import get_enhanced_parcel_data, format_property_data_for_llm
from llm import get_similar_developments, get_estate_report
from prompts import DEVELOPMENT_OPPORTUNITIES_PROMPT

app = FastAPI(title="PlotTwist API - Backend", 
              description="Backend API for real estate development opportunity analysis")

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PropertyRequest(BaseModel):
    street_number: str
    street_name: str
    street_suffix: str
    unit_number: str

class PropertyResponse(BaseModel):
    final_report: str
    recent_developments: str
    evidence: str
    data_sources: dict[str, Optional[str]]

@app.post("/create-report", response_model=PropertyResponse)
async def create_report(request: PropertyRequest):
    enhanced_parcel_data = get_enhanced_parcel_data("", request.street_number, request.street_name, request.street_suffix, request.unit_number)
    print(enhanced_parcel_data)
    formatted_property_info = format_property_data_for_llm(enhanced_parcel_data)
    recent_developments = get_similar_developments(formatted_property_info)
    print("="*100)
    print(recent_developments)
    report = get_estate_report(formatted_property_info, recent_developments["content"])
    print("="*100)
    print(report)
    return PropertyResponse(
        final_report=report,
        recent_developments=recent_developments["content"],
        evidence="\n".join(recent_developments["evidence"]),
        data_sources=enhanced_parcel_data
    )

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy", 
        "service": "PlotTwist Real Estate Analyzer",
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

