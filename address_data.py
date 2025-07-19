import requests
import sys

def geocode_address(address):
    """Geocode an address using OpenStreetMap Nominatim service"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "PlotTwist/1.0 (https://github.com/yourusername/plotTwist; your@email.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        if data and len(data) > 0:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return lat, lon
        else:
            print(f"No geocoding results found for: {address}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error geocoding address '{address}': {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Error parsing geocoding response for '{address}': {e}")
        return None
    except Exception as e:
        print(f"Unexpected error geocoding '{address}': {e}")
        return None

if __name__ == "__main__":
    coords = geocode_address("1 City Hall Square, Boston, MA")
    print(coords)