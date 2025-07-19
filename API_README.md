# Real Estate Agent API

A FastAPI application that provides real estate development analysis using Google's Gemini AI and web search capabilities.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## To Run the API

Start the FastAPI server:
```bash
python app.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### POST /analyze-property

Analyzes a property for real estate development opportunities.

**Request Body:**
```json
{
  "property_info": "Detailed property information including zoning, dimensions, etc."
}
```

**Response:**
```json
{
  "analysis": "AI-generated analysis of development opportunities"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Testing the API

1. Start the server:
```bash
python app.py
```

2. In another terminal, run the test script:
```bash
python test_api.py
```

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Example Usage

```python
import requests

url = "http://localhost:8000/analyze-property"
payload = {
    "property_info": "Your property information here..."
}

response = requests.post(url, json=payload)
result = response.json()
print(result["analysis"])
```

## Features

- Real-time web search integration via Tavily
- Google Gemini AI analysis
- Automatic function calling for tool usage
- Structured property analysis
- Error handling and validation 