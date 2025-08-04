import math, json, urllib.parse, requests
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)


def get_long_lat(address):
    """
    Use the free U S Census geocoder to turn an address into lon/lat.
    """
    url = "https://geocoder.boston.gov/arcgis/rest/services/SAMLocator/GeocodeServer/findAddressCandidates"
    params = {
        "Address": "",
        "Address2": "",
        "Address3": "",
        "Neighborhood": "",
        "City": "",
        "Subregion": "",
        "Region": "",
        "Postal": "",
        "PostalExt": "",
        "CountryCode": "",
        "SingleLine": address,
        "outFields": "*",
        "maxLocations": "",
        "matchOutOfRange": "true",
        "langCode": "",
        "locationType": "",
        "sourceCountry": "",
        "category": "",
        "location": "",
        "searchExtent": "",
        "outSR": "4326",
        "magicKey": "",
        "preferredLabelValues": "",
        "f": "pjson"
    }
    res = requests.get(url, params=params, timeout=20).json()
    return res["candidates"][0]["location"]["x"], res["candidates"][0]["location"]["y"]



def get_zoning_district(lon, lat):
    x, y = transformer.transform(lat, lon)
    print(x, y)
    url = "https://gis.bostonplans.org/hosting/rest/services/Zoning_Viewer_Dist_Subdist/MapServer/identify"
    params = {
        "f": "json",
        "returnFieldName": "true",
        "returnGeometry": "false",
        "returnUnformattedValues": "true",
        "returnZ": "false",
        "tolerance": "0",
        "imageDisplay": "448,793,96",
        "geometry": '{"x":' + str(x) + ',"y":' + str(y) + '}',
        "geometryType": "esriGeometryPoint",
        "sr": "102100",
        "mapExtent": "-7916120.180887967,5207122.958744759,-7911839.707304003,5214699.779173516",
        "layers": "all"
    }
    res = requests.get(url, params=params, timeout=20).json()
    return res



# --- example run ---------------------------------------------------------
if __name__ == "__main__":
    lat, lon = get_long_lat("185 DEVONSHIRE ST STE 800 BOSTON MA 02110-1414 USA")
    print(lon, lat)
    print(get_zoning_district(lon, lat))