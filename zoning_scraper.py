import requests
import json
from typing import Dict, Optional, Tuple
from address_data import geocode_address

# Boston GIS and Planning API endpoints
BOSTON_GIS_BASE = "https://gis.boston.gov/arcgis/rest/services"
ZONING_VIEWER_BASE = "https://maps.bostonplans.org"

def get_zoning_by_coordinates(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Get zoning information using latitude and longitude coordinates"""
    
    zoning_data = {
        'zoning_district': None,
        'zoning_code': None,
        'height_limit': None,
        'far_limit': None,
        'setback_front': None,
        'setback_side': None,
        'setback_rear': None,
        'allowed_uses': None,
        'overlay_district': None,
        'planning_area': None,
        'article_80_required': None,
        'affordable_housing_req': None,
        'parking_requirements': None,
        'lot_coverage_max': None,
        'open_space_req': None,
        'zoning_source': None
    }
    
    try:
        # Try Boston GIS Planning services first
        planning_url = f"{BOSTON_GIS_BASE}/Planning/OpenData/MapServer/identify"
        params = {
            'f': 'json',
            'tolerance': 5,
            'returnGeometry': 'false',
            'imageDisplay': '1,1,96',
            'mapExtent': f'{lon-0.001},{lat-0.001},{lon+0.001},{lat+0.001}',
            'geometry': f'{{"x":{lon},"y":{lat},"spatialReference":{{"wkid":4326}}}}',
            'geometryType': 'esriGeometryPoint',
            'sr': '4326',
            'layers': 'all'
        }
        
        response = requests.get(planning_url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                for result in data['results']:
                    attributes = result.get('attributes', {})
                    
                    # Extract zoning information from attributes
                    for key, value in attributes.items():
                        key_lower = key.lower()
                        if 'zon' in key_lower and 'district' in key_lower:
                            zoning_data['zoning_district'] = value
                        elif 'zon' in key_lower and ('code' in key_lower or 'class' in key_lower):
                            zoning_data['zoning_code'] = value
                        elif 'height' in key_lower:
                            zoning_data['height_limit'] = value
                        elif 'far' in key_lower or 'floor area ratio' in key_lower:
                            zoning_data['far_limit'] = value
                        elif 'overlay' in key_lower:
                            zoning_data['overlay_district'] = value
                        elif 'plan' in key_lower and 'area' in key_lower:
                            zoning_data['planning_area'] = value
    
    except Exception as e:
        print(f"Error with GIS service: {e}")
    
    # Try alternative approaches if primary didn't work
    if not zoning_data['zoning_district']:
        try:
            # Try the city's data portal
            data_portal_url = "https://data.boston.gov/api/3/action/datastore_search"
            params = {
                'resource_id': 'zoning-districts',  # This might need adjustment
                'limit': 1,
                'q': f'lat:{lat} lon:{lon}'
            }
            
            response = requests.get(data_portal_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('result', {}).get('records'):
                    record = data['result']['records'][0]
                    zoning_data['zoning_district'] = record.get('zoning_district')
                    zoning_data['zoning_code'] = record.get('zoning_code')
                    
        except Exception as e:
            print(f"Error with data portal: {e}")
    
    return zoning_data

def get_zoning_by_address(address: str) -> Dict[str, Optional[str]]:
    """Get zoning information by street address"""
    
    # First geocode the address
    coordinates = geocode_address(address)
    if not coordinates:
        return {'error': 'Could not geocode address'}
    
    lat, lon = coordinates
    return get_zoning_by_coordinates(lat, lon)

def get_planning_context(address: str, zoning_district: str = None) -> Dict[str, Optional[str]]:
    """Get broader planning context including development projects and planning initiatives"""
    
    planning_context = {
        'neighborhood': None,
        'planning_district': None,
        'transit_oriented': None,
        'enterprise_zone': None,
        'historic_district': None,
        'flood_zone': None,
        'article_25a_overlay': None,  # Coastal flood resilience
        'article_37_required': None,  # Green building
        'inclusionary_development': None,
        'linkage_required': None,
        'recent_developments': [],
        'pending_rezonings': [],
        'master_plan_area': None
    }
    
    try:
        # Get coordinates for context searches
        coordinates = geocode_address(address)
        if coordinates:
            lat, lon = coordinates
            
            # Search for nearby Article 80 development projects
            article_80_url = "https://data.boston.gov/api/3/action/datastore_search"
            params = {
                'resource_id': 'article-80-development-projects',
                'limit': 10
            }
            
            response = requests.get(article_80_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    records = data.get('result', {}).get('records', [])
                    planning_context['recent_developments'] = records[:5]  # Limit to 5
            
            # Check for special overlay districts
            overlays = check_overlay_districts(lat, lon)
            planning_context.update(overlays)
            
    except Exception as e:
        print(f"Error getting planning context: {e}")
    
    return planning_context

def check_overlay_districts(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Check for special overlay districts at the given location"""
    
    overlays = {
        'flood_zone': None,
        'historic_district': None,
        'article_25a_overlay': None,
        'transit_oriented': None,
        'enterprise_zone': None,
        'opportunity_zone': None
    }
    
    try:
        # Check multiple GIS layers for overlays
        overlay_services = [
            'flood_zones',
            'historic_districts', 
            'coastal_overlay',
            'transit_oriented_development',
            'opportunity_zones'
        ]
        
        for service in overlay_services:
            try:
                url = f"{BOSTON_GIS_BASE}/Overlays/{service}/MapServer/identify"
                params = {
                    'f': 'json',
                    'tolerance': 5,
                    'returnGeometry': 'false',
                    'geometry': f'{{"x":{lon},"y":{lat},"spatialReference":{{"wkid":4326}}}}',
                    'geometryType': 'esriGeometryPoint',
                    'sr': '4326'
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        # Map service names to overlay fields
                        if 'flood' in service:
                            overlays['flood_zone'] = data['results'][0].get('attributes', {}).get('zone_type')
                        elif 'historic' in service:
                            overlays['historic_district'] = data['results'][0].get('attributes', {}).get('district_name')
                        elif 'coastal' in service:
                            overlays['article_25a_overlay'] = 'Yes'
                        elif 'transit' in service:
                            overlays['transit_oriented'] = 'Yes'
                        elif 'opportunity' in service:
                            overlays['opportunity_zone'] = 'Yes'
                            
            except Exception as e:
                continue  # Skip failed services
                
    except Exception as e:
        print(f"Error checking overlays: {e}")
    
    return overlays

def get_zoning_requirements(zoning_district: str) -> Dict[str, Optional[str]]:
    """Get detailed zoning requirements for a specific zoning district"""
    
    requirements = {
        'min_lot_size': None,
        'min_lot_width': None,
        'max_height': None,
        'max_far': None,
        'front_setback': None,
        'side_setback': None,
        'rear_setback': None,
        'max_lot_coverage': None,
        'min_open_space': None,
        'parking_ratio': None,
        'allowed_uses': [],
        'conditional_uses': [],
        'prohibited_uses': [],
        'design_standards': []
    }
    
    # Boston zoning district mappings
    zoning_mappings = {
        # Residential Districts
        'R-1': {
            'min_lot_size': '5,000 sq ft',
            'max_height': '35 ft',
            'max_far': '0.5',
            'front_setback': '20 ft',
            'allowed_uses': ['Single-family dwelling', 'Accessory uses']
        },
        'R-2': {
            'min_lot_size': '3,000 sq ft',
            'max_height': '35 ft', 
            'max_far': '0.6',
            'front_setback': '15 ft',
            'allowed_uses': ['Single-family dwelling', 'Two-family dwelling']
        },
        'R-4': {
            'min_lot_size': '1,500 sq ft per unit',
            'max_height': '35 ft',
            'max_far': '0.8',
            'allowed_uses': ['Multi-family dwelling', 'Townhouse']
        },
        '2F-5000': {
            'min_lot_size': '5,000 sq ft per unit',
            'max_height': '35 ft',
            'max_far': '0.6',
            'front_setback': '10-20 ft',
            'allowed_uses': ['Two-family dwelling', 'Single-family dwelling']
        },
        # Commercial Districts
        'B-2': {
            'max_height': '55 ft',
            'max_far': '2.0',
            'allowed_uses': ['Retail', 'Office', 'Restaurant', 'Mixed-use']
        },
        'B-8': {
            'max_height': '80 ft',
            'max_far': '4.0',
            'allowed_uses': ['High-density commercial', 'Residential', 'Office']
        }
    }
    
    if zoning_district in zoning_mappings:
        requirements.update(zoning_mappings[zoning_district])
    
    return requirements

def get_comprehensive_zoning_data(address: str) -> Dict:
    """Get all zoning and planning information for a property"""
    
    print(f"Getting comprehensive zoning data for: {address}")
    
    result = {
        'address': address,
        'coordinates': None,
        'zoning_info': {},
        'planning_context': {},
        'zoning_requirements': {},
        'development_potential': {}
    }
    
    # Get coordinates
    coordinates = geocode_address(address)
    if coordinates:
        result['coordinates'] = {'lat': coordinates[0], 'lon': coordinates[1]}
        
        # Get zoning information
        result['zoning_info'] = get_zoning_by_coordinates(coordinates[0], coordinates[1])
        
        # Get planning context
        result['planning_context'] = get_planning_context(address, 
                                                         result['zoning_info'].get('zoning_district'))
        
        # Get zoning requirements if we have a district
        if result['zoning_info'].get('zoning_district'):
            result['zoning_requirements'] = get_zoning_requirements(result['zoning_info']['zoning_district'])
        
        # Analyze development potential
        result['development_potential'] = analyze_development_potential(result)
    
    return result

def analyze_development_potential(zoning_data: Dict) -> Dict[str, Optional[str]]:
    """Analyze development potential based on zoning and context"""
    
    potential = {
        'upzoning_opportunity': None,
        'density_bonus_eligible': None,
        'article_80_required': None,
        'affordable_housing_req': None,
        'environmental_review': None,
        'height_variance_possible': None,
        'mixed_use_potential': None,
        'transit_bonus_eligible': None,
        'development_complexity': 'Medium',  # Low/Medium/High
        'timeline_estimate': '18-36 months'  # Typical timeline
    }
    
    zoning_info = zoning_data.get('zoning_info', {})
    planning_context = zoning_data.get('planning_context', {})
    
    # Analyze based on zoning district
    district = zoning_info.get('zoning_district', '')
    
    if district.startswith('R-'):
        potential['mixed_use_potential'] = 'Limited'
        potential['article_80_required'] = 'If over 20,000 sq ft'
    elif district.startswith('B-'):
        potential['mixed_use_potential'] = 'High'
        potential['article_80_required'] = 'If over 20,000 sq ft'
        
    # Check for special circumstances
    if planning_context.get('transit_oriented'):
        potential['transit_bonus_eligible'] = 'Yes'
        potential['density_bonus_eligible'] = 'Possible'
        
    if planning_context.get('article_25a_overlay'):
        potential['environmental_review'] = 'Coastal flood resilience required'
        potential['development_complexity'] = 'High'
        
    if planning_context.get('historic_district'):
        potential['development_complexity'] = 'High'
        potential['timeline_estimate'] = '24-48 months'
    
    return potential

if __name__ == "__main__":
    # Test with the example address
    test_address = "263 N Harvard St, Allston, MA"
    zoning_data = get_comprehensive_zoning_data(test_address)
    print(json.dumps(zoning_data, indent=2)) 