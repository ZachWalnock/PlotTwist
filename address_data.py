import requests
import sys
def geocode_address(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
    }
    headers = {
        "User-Agent": "PlotTwist/1.0 (https://github.com/yourusername/plotTwist; your@email.com)"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    return None

coords = geocode_address("1 City Hall Square, Boston, MA")
print(coords)