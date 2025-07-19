# 🚀 PlotTwist - Google Cloud Run Hackathon Deployment

## 🎯 What is PlotTwist?

**PlotTwist** is an AI-powered real estate development opportunity analyzer built for the Google Cloud Run GPU Hackathon. It combines:

- 🏠 **Real property data** from Boston Assessment records
- 🗺️ **Zoning analysis** and development constraints  
- 🧠 **AI-powered insights** using Google Gemini
- 📊 **Market intelligence** and strategic recommendations

## ⚡ Quick Deploy (5 minutes)

### Prerequisites
- Google Cloud account with billing enabled
- `gcloud` CLI installed and authenticated
- Docker installed

### Deploy to Cloud Run

1. **Set your project ID:**
   ```bash
   export PROJECT_ID="your-hackathon-project-id"
   gcloud config set project $PROJECT_ID
   ```

2. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com
   ```

3. **Deploy with one command:**
   ```bash
   ./deploy.sh $PROJECT_ID
   ```

4. **Set environment variables** (after first deploy):
   ```bash
   gcloud run services update plottwist \
     --region=us-central1 \
     --set-env-vars="GOOGLE_API_KEY=your-gemini-api-key,TAVILY_API_KEY=your-tavily-key"
   ```

## 🧪 Test Your Deployment

### Web Interface
Visit your Cloud Run URL to see the beautiful demo interface!

### API Testing
```bash
curl -X POST "https://your-service-url/create-report" \
  -H "Content-Type: application/json" \
  -d '{"property_info": "263 N Harvard St, Boston, MA"}'
```

### Health Check
```bash
curl https://your-service-url/health
```

## 🏆 Hackathon Demo Features

### ✅ What Works Now
- **Property Analysis**: Extracts 25+ data fields from Boston records
- **Zoning Intelligence**: Smart coordinate-based zoning inference
- **Market Context**: 9+ Boston neighborhoods with trends
- **AI Recommendations**: Gemini-powered strategic analysis
- **Development Scoring**: FAR calculations, feasibility ratings

### 🎨 Demo Interface
- Beautiful responsive web UI
- Real-time property analysis
- Example Boston addresses
- Professional development reports

### 📊 Sample Analysis Output
```
## Property Analysis Report

### Property Summary
- Address: 263 N Harvard St
- Property Type: Two Family
- Year Built: 1890
- Total Value: $1,607,700

### Development Assessment
- Current FAR: 0.31
- Maximum FAR: 0.6
- Density Increase Possible: TRUE (94% expansion opportunity!)

### Market Context
- Neighborhood: Allston
- Market Trends: Student housing demand, gentrification
- Transit: Green Line B accessible
```

## 🛠️ Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Web Demo   │ -> │  FastAPI App    │ -> │  Boston APIs    │
│  (HTML/JS)  │    │  (Cloud Run)    │    │  (Property Data)│
└─────────────┘    └─────────────────┘    └─────────────────┘
                          │
                          v
                   ┌─────────────────┐
                   │  Google Gemini  │
                   │  (AI Analysis)  │
                   └─────────────────┘
```

## 🎯 Hackathon Pitch Points

1. **Real Business Value**: Helps developers find $1M+ opportunities
2. **AI-Powered**: Uses Gemini for strategic insights
3. **Data Integration**: Combines multiple Boston data sources
4. **Production Ready**: Professional reports, error handling
5. **Scalable**: Cloud Run serverless deployment

## 🚀 Live Demo Script

1. **Show the interface** at your Cloud Run URL
2. **Try these addresses**:
   - `263 N Harvard St` - $1.6M Allston two-family (94% density upside)
   - `100 Boylston St` - $195M Back Bay commercial (premium location)
   - `123 Centre St` - $860K residential opportunity

3. **Highlight key features**:
   - Real-time property data extraction
   - AI-powered market analysis  
   - Development feasibility scoring
   - Strategic recommendations

## 🏆 Why PlotTwist Wins

- **Practical**: Solves real $B+ real estate market problems
- **Technical**: Sophisticated data integration + AI analysis  
- **Complete**: Full-stack app with beautiful UI
- **Scalable**: Cloud Run serverless architecture
- **Innovative**: Novel application of AI to real estate development

---

**Built for the Google Cloud Run GPU Hackathon 2025** 🚀

*Good luck and may the best agentic application win!* 🏆 