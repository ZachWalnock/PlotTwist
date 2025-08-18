import requests
import json
import time
from urllib.parse import quote
import re

class BostonZoningScraper:
    def __init__(self):
        self.base_url = "https://maps.bostonplans.org"
        self.session = requests.Session()
        # Set headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://maps.bostonplans.org/zoningviewer/',
        })
    
    def geocode_address(self, address):
        """
        Convert address to coordinates using multiple geocoding services
        """
        # Try multiple geocoding services in order of preference
        geocoding_methods = [
            self._geocode_with_arcgis_world,
            self._geocode_with_nominatim,
            self._geocode_with_boston_arcgis
        ]
        
        for method in geocoding_methods:
            try:
                result = method(address)
                if result:
                    print(f"Successfully geocoded with {method.__name__}")
                    return result
            except Exception as e:
                print(f"Geocoding attempt failed with {method.__name__}: {e}")
                continue
        
        return None
    
    def _geocode_with_arcgis_world(self, address):
        """
        Use ArcGIS World Geocoding Service (requires no API key for basic usage)
        """
        geocode_url = "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
        
        params = {
            'SingleLine': f"{address}",
            'f': 'json',
            'outSR': '4326',
            'maxLocations': 1,
            'category': 'Address',
            'countryCode': 'USA'
        }
        
        response = self.session.get(geocode_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('candidates') and len(data['candidates']) > 0:
            candidate = data['candidates'][0]
            location = candidate['location']
            return {
                'x': location['x'],
                'y': location['y'],
                'score': candidate['score'],
                'address': candidate['address']
            }
        return None
    
    def _geocode_with_nominatim(self, address):
        """
        Use OpenStreetMap Nominatim geocoding service
        """
        geocode_url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            'q': f"{address}",
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us',
            'bounded': 1,
            'viewbox': '-71.191155,42.227925,-70.986365,42.400819'  # Boston area bounding box
        }
        
        # Add a custom user agent as required by Nominatim
        headers = self.session.headers.copy()
        headers['User-Agent'] = 'BostonZoningTool/1.0'
        
        response = self.session.get(geocode_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            result = data[0]
            return {
                'x': float(result['lon']),
                'y': float(result['lat']),
                'score': 100,  # Nominatim doesn't provide scores
                'address': result['display_name']
            }
        return None
    
    def _geocode_with_boston_arcgis(self, address):
        """
        Try Boston's ArcGIS Online services
        """
        # Try Boston's main ArcGIS server
        geocode_url = "https://services.arcgis.com/sFnw0xNflSi8J0qw/arcgis/rest/services/Boston_Composite_Locator/GeocodeServer/findAddressCandidates"
        
        params = {
            'SingleLine': address,
            'f': 'json',
            'outSR': '4326',
            'maxLocations': 1
        }
        
        response = self.session.get(geocode_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('candidates') and len(data['candidates']) > 0:
            candidate = data['candidates'][0]
            location = candidate['location']
            return {
                'x': location['x'],
                'y': location['y'],
                'score': candidate['score'],
                'address': candidate['address']
            }
        return None
    
    def get_zoning_info(self, x, y):
        """
        Query the zoning layer using coordinates - try multiple endpoints
        """
        zoning_methods = [
            self._query_boston_zoning_primary,
            self._query_boston_zoning_secondary,
            self._query_boston_zoning_legacy
        ]
        
        for method in zoning_methods:
            try:
                result = method(x, y)
                if result:
                    print(f"Successfully found zoning info with {method.__name__}")
                    return result
            except Exception as e:
                print(f"Zoning query attempt failed with {method.__name__}: {e}")
                continue
        
        return None
    
    def _query_boston_zoning_primary(self, x, y):
        """
        Query the primary Boston zoning service - Boston Open Data
        """
        # Boston Open Data ArcGIS service endpoint
        zoning_url = "https://services.arcgis.com/sFnw0xNflSi8J0qw/arcgis/rest/services/Boston_Zoning_Subdistricts/FeatureServer/0/query"
        
        params = {
            'geometry': f'{x},{y}',
            'geometryType': 'esriGeometryPoint',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',
            'returnGeometry': 'false',
            'f': 'json'
        }
        
        response = self.session.get(zoning_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('features') and len(data['features']) > 0:
            feature = data['features'][0]
            attributes = feature['attributes']
            
            return {
                'zoning_code': attributes.get('zoning_sub') or attributes.get('ZONING_SUBDISTRICT') or attributes.get('ZONING') or attributes.get('ZONE') or 'Not found',
                'district': attributes.get('zoning') or attributes.get('ZONING_DISTRICT') or attributes.get('DISTRICT') or 'Not found',
                'subdistrict': attributes.get('zoning_sub') or attributes.get('ZONING_SUBDISTRICT') or attributes.get('SUBDISTRICT') or 'Not found',
                'overlay': attributes.get('OVERLAY') or attributes.get('OVERLAY_ZONE') or 'None',
            }
        return None
    
    def _query_boston_zoning_secondary(self, x, y):
        """
        Try alternative Boston zoning service endpoint - Districts
        """
        # Try the zoning districts service instead of subdistricts
        zoning_url = "https://services.arcgis.com/sFnw0xNflSi8J0qw/arcgis/rest/services/Boston_Zoning_Districts/FeatureServer/0/query"
        
        params = {
            'geometry': f'{x},{y}',
            'geometryType': 'esriGeometryPoint',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': '*',
            'returnGeometry': 'false',
            'f': 'json'
        }
        
        response = self.session.get(zoning_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('features') and len(data['features']) > 0:
            feature = data['features'][0]
            attributes = feature['attributes']
            
            return {
                'zoning_code': attributes.get('zoning') or attributes.get('ZONE_CLASS') or attributes.get('ZONING') or attributes.get('ZONE') or 'Not found',
                'district': attributes.get('zoning') or attributes.get('ZONE_CLASS') or attributes.get('DISTRICT') or 'Not found',
                'subdistrict': attributes.get('zoning') or attributes.get('ZONE_CLASS') or 'Not found',
                'overlay': 'None',
            }
        return None
    
    def _query_boston_zoning_legacy(self, x, y):
        """
        Try Boston Open Data REST API directly
        """
        # Use the direct REST service for Boston Open Data
        zoning_url = "https://gisdata.boston.gov/server/rest/services/OpenData/Property_Assessment/MapServer/0/query"
        
        params = {
            'geometry': f'{x},{y}',
            'geometryType': 'esriGeometryPoint',
            'inSR': '4326',
            'spatialRel': 'esriSpatialRelIntersects',
            'outFields': 'ZONING,ZONE_CLASS,DISTRICT',
            'returnGeometry': 'false',
            'f': 'json'
        }
        
        response = self.session.get(zoning_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('features') and len(data['features']) > 0:
            feature = data['features'][0]
            attributes = feature['attributes']
            
            return {
                'zoning_code': attributes.get('ZONING') or attributes.get('ZONE_CLASS') or 'Not found',
                'district': attributes.get('ZONING') or attributes.get('ZONE_CLASS') or 'Not found',
                'subdistrict': attributes.get('ZONING') or attributes.get('ZONE_CLASS') or 'Not found',
                'overlay': 'None',
            }
        return None
    
    def get_municode_link(self, zoning_code):
        """
        Generate municode library link based on zoning code
        Boston's zoning code is in Article 66 of the municode library
        """
        base_municode_url = "https://library.municode.com/ma/boston/codes/code_of_ordinances"
        
        # Map common zoning codes to their sections
        zoning_sections = {
            # Residential zones
            'R-1': '?nodeId=TIT6ZOCO_CH66ZO_ART66-2ZODI_66-2REDI',
            'R-2': '?nodeId=TIT6ZOCO_CH66ZO_ART66-2ZODI_66-2REDI',
            'R-3': '?nodeId=TIT6ZOCO_CH66ZO_ART66-2ZODI_66-2REDI',
            'R-4': '?nodeId=TIT6ZOCO_CH66ZO_ART66-2ZODI_66-2REDI',
            'R-5': '?nodeId=TIT6ZOCO_CH66ZO_ART66-2ZODI_66-2REDI',
            'R-6': '?nodeId=TIT6ZOCO_CH66ZO_ART66-2ZODI_66-2REDI',
            
            # Commercial zones
            'B-1': '?nodeId=TIT6ZOCO_CH66ZO_ART66-3BUDI',
            'B-2': '?nodeId=TIT6ZOCO_CH66ZO_ART66-3BUDI',
            'B-3': '?nodeId=TIT6ZOCO_CH66ZO_ART66-3BUDI',
            
            # Mixed use
            'MU': '?nodeId=TIT6ZOCO_CH66ZO_ART66-4MIUSDI',
            
            # Industrial
            'I-1': '?nodeId=TIT6ZOCO_CH66ZO_ART66-5INDI',
            'I-2': '?nodeId=TIT6ZOCO_CH66ZO_ART66-5INDI',
        }
        
        # Try to match the zoning code
        for code, section in zoning_sections.items():
            if zoning_code.startswith(code):
                return base_municode_url + section
        
        # Default to main zoning chapter if no specific match
        return base_municode_url + "?nodeId=TIT6ZOCO_CH66ZO"
    
    def debug_zoning_fields(self, x, y):
        """
        Debug method to see what fields are available in the zoning services
        """
        print("=== DEBUGGING ZONING FIELDS ===")
        
        endpoints = [
            ("Primary (Subdistricts)", "https://services.arcgis.com/sFnw0xNflSi8J0qw/arcgis/rest/services/Boston_Zoning_Subdistricts/FeatureServer/0/query"),
            ("Secondary (Districts)", "https://services.arcgis.com/sFnw0xNflSi8J0qw/arcgis/rest/services/Boston_Zoning_Districts/FeatureServer/0/query"),
            ("Legacy (GIS Data)", "https://gisdata.boston.gov/server/rest/services/OpenData/Property_Assessment/MapServer/0/query"),
        ]
        
        for name, url in endpoints:
            try:
                print(f"\nTesting {name}:")
                print(f"URL: {url}")
                
                params = {
                    'geometry': f'{x},{y}',
                    'geometryType': 'esriGeometryPoint',
                    'inSR': '4326',
                    'spatialRel': 'esriSpatialRelIntersects',
                    'outFields': '*',
                    'returnGeometry': 'false',
                    'f': 'json'
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                print(f"Response status: {response.status_code}")
                
                if 'error' in data:
                    print(f"API Error: {data['error']}")
                elif data.get('features') and len(data['features']) > 0:
                    feature = data['features'][0]
                    attributes = feature['attributes']
                    print("SUCCESS! Available fields:")
                    for key, value in attributes.items():
                        print(f"  {key}: {value}")
                else:
                    print("No features found at this location")
                    
            except Exception as e:
                print(f"Error testing {name}: {e}")
        
        print("=== END DEBUG ===\n")

    def get_address_zoning(self, address, debug=False):
        """
        Main method to get zoning information for an address
        """
        print(f"Looking up zoning information for: {address}")
        
        # Step 1: Geocode the address
        print("Geocoding address...")
        coordinates = self.geocode_address(address)
        
        if not coordinates:
            return {
                'error': 'Could not find coordinates for the given address',
                'address': address
            }
        
        print(f"Found coordinates: ({coordinates['x']}, {coordinates['y']})")
        print(f"Matched address: {coordinates['address']}")
        
        # Debug mode - show all available fields
        if debug:
            self.debug_zoning_fields(coordinates['x'], coordinates['y'])
        
        # Step 2: Get zoning information
        print("Querying zoning information...")
        zoning_info = self.get_zoning_info(coordinates['x'], coordinates['y'])
        
        if not zoning_info:
            return {
                'error': 'Could not find zoning information for these coordinates',
                'address': coordinates['address'],
                'coordinates': coordinates
            }
        
        # Step 3: Generate municode link
        municode_link = self.get_municode_link(zoning_info['zoning_code'])
        
        # Compile results
        result = {
            'address': coordinates['address'],
            'coordinates': {
                'longitude': coordinates['x'],
                'latitude': coordinates['y']
            },
            'zoning_code': zoning_info['zoning_code'],
            'zoning_district': zoning_info['district'],
            'zoning_subdistrict': zoning_info['subdistrict'],
            'overlay': zoning_info['overlay'],
            'municode_link': municode_link,
            'geocoding_score': coordinates['score']
        }
        
        return result

# Example usage
def main():
    scraper = BostonZoningScraper()
    
    # Test with your specific address first, with debug enabled
    test_address = "263 N Harvard St, Boston, MA 02134"
    
    print(f"\n{'='*60}")
    print("RUNNING IN DEBUG MODE TO IDENTIFY CORRECT FIELDS")
    result = scraper.get_address_zoning(test_address, debug=True)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Address: {result['address']}")
        print(f"Zoning Code: {result['zoning_code']}")
        print(f"District: {result['zoning_district']}")
        print(f"Subdistrict: {result['zoning_subdistrict']}")
        print(f"Overlay: {result['overlay']}")
        print(f"Municode Link: {result['municode_link']}")
        print(f"Coordinates: ({result['coordinates']['longitude']:.6f}, {result['coordinates']['latitude']:.6f})")
        print(f"Geocoding Score: {result['geocoding_score']}")
    
    print(f"{'='*60}")

# Simple usage function for after we fix the field mappings
def simple_lookup(address):
    scraper = BostonZoningScraper()
    return scraper.get_address_zoning(address)

if __name__ == "__main__":
    main()