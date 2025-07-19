import requests
import json

def test_analyze_property():
    """Test the analyze-property endpoint"""
    
    # Sample property information
    property_info = """## 1. Parcel Overview

- **Parcel ID:** 2201486000
- **Address:** 263 N Harvard St, Allston, MA 02134
- **Lot Size:** 11,525 sq ft
- **Existing Structure:** 3,539 sq ft, Two-Family Dwelling (6 beds, 3 baths, 2 kitchens)
- **Year Built:** 1890
- **Parking:** 7 spaces
- **Owner:** THE HELPING HAND TRUST
- **Owner Mailing Address:** 316 N Harvard St, c/o James Georges, Allston MA 02134

## 2. Zoning Information

- **Zoning District:** 2F-5000 (Two-Family Residential)
- **Zoning Code Source:** Article 51 (Allston-Brighton Neighborhood District)
- **Zoning Map:** Available at [BPDA Zoning Viewer](https://maps.bostonplans.org/zoningviewer/)
- **Allowed Use (By-Right):** 2-family residential structure
- **Overlay:** None reported

## 3. Dimensional Requirements (Article 51)

- **Max Height:** 35 ft
- **Min Lot Area:** 5,000 sq ft per dwelling unit
- **Min Lot Width:** 50 ft
- **Front Setback:** Typically 10–20 ft
- **FAR:** Approx. 0.5–0.6 (varies by parcel)"""

    # API endpoint
    url = "http://localhost:8000/analyze-property"
    
    # Request payload
    payload = {
        "property_info": property_info
    }
    
    try:
        # Make POST request
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis successful!")
            print("=" * 50)
            print("ANALYSIS:")
            print("=" * 50)
            print(result["analysis"])
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_analyze_property() 