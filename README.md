# PlotTwist 🏗️

AI-powered real estate development opportunity analysis for Boston properties.

## Overview

PlotTwist automatically analyzes Boston real estate properties and identifies development opportunities using AI. It scrapes property data from city records, gathers market intelligence, and generates comprehensive development feasibility reports.

## Features

- **Property Data Extraction**: Scrapes Boston city assessor records for property details, values, and ownership
- **AI Analysis**: Uses Google Gemini to evaluate development potential as an expert real estate advisor  
- **Market Intelligence**: Integrates web search for recent news, zoning changes, and area developments
- **Comprehensive Reports**: Generates detailed feasibility studies with financial projections and recommendations

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   export GOOGLE_API_KEY="your_gemini_api_key"
   export TAVILY_API_KEY="your_tavily_api_key"
   ```

3. **Run analysis**:
   ```python
   from main import get_parcel_basics
   from llm import ask_real_estate_agent
   
   # Get property data
   property_data = get_parcel_basics("", "263", "N HARVARD", "", "")
   
   # Analyze development opportunities
   report = ask_real_estate_agent(property_data)
   ```

## Data Sources

- [Boston Property Assessment](https://www.cityofboston.gov/assessing/search/)
- [BPDA Zoning Maps](https://maps.bostonplans.org/zoningviewer/)
- [Development Projects](https://www.bostonplans.org/projects/development-projects)
- Real-time web search via Tavily

## Example Output

Generates professional development opportunity reports including:
- Market analysis and neighborhood trends
- Zoning compliance and development rights
- Financial projections and feasibility metrics
- Community impact and public benefits assessment

---
*Hackathon Project - Built for rapid real estate opportunity identification*
