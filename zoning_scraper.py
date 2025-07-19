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
        # Try Boston GIS Planning services first with multiple potential layers
        planning_base_url = f"{BOSTON_GIS_BASE}/Planning"
        
        # Try different service endpoints
        service_endpoints = [
            f"{planning_base_url}/OpenData/MapServer/identify",
            f"{BOSTON_GIS_BASE}/OpenData/MapServer/identify", 
            f"https://services.arcgis.com/sFnw0xNflSi8J0qw/ArcGIS/rest/services/Zoning_Subdistricts/FeatureServer/0/query"
        ]
        
        for endpoint in service_endpoints:
            try:
                if "query" in endpoint:
                    # For ArcGIS Feature Service query
                    params = {
                        'f': 'json',
                        'where': '1=1',
                        'geometry': f'{lon},{lat}',
                        'geometryType': 'esriGeometryPoint',
                        'spatialRel': 'esriSpatialRelIntersects',
                        'outFields': '*',
                        'returnGeometry': 'false'
                    }
                else:
                    # For MapServer identify service
                    params = {
                        'f': 'json',
                        'tolerance': 10,
                        'returnGeometry': 'false',
                        'imageDisplay': '1,1,96',
                        'mapExtent': f'{lon-0.001},{lat-0.001},{lon+0.001},{lat+0.001}',
                        'geometry': f'{{"x":{lon},"y":{lat},"spatialReference":{{"wkid":4326}}}}',
                        'geometryType': 'esriGeometryPoint',
                        'sr': '4326',
                        'layers': 'all'
                    }
                
                print(f"Trying zoning lookup at: {endpoint}")
                response = requests.get(endpoint, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Handle different response structures
                    results = []
                    if 'results' in data:
                        results = data['results']
                    elif 'features' in data and data['features']:
                        results = [{'attributes': feature['attributes']} for feature in data['features']]
                    
                    if results:
                        print(f"Found {len(results)} zoning features")
                        
                        # Extract zoning information from results
                        for result in results:
                            attributes = result.get('attributes', {})
                            
                            # Try multiple field name patterns for zoning district
                            for key, value in attributes.items():
                                if value is None or value == '' or str(value).lower() in ['null', 'none', '<null>']:
                                    continue
                                    
                                key_lower = str(key).lower()
                                value_str = str(value).strip()
                                
                                # Skip obviously invalid values
                                if len(value_str) < 2 or value_str.lower() in ['null', 'none', 'n/a', '']:
                                    continue
                                
                                # Zoning district patterns - be more specific
                                if any(pattern in key_lower for pattern in ['zone', 'district', 'subdistrict']):
                                    if not zoning_data['zoning_district'] and len(value_str) <= 20:  # Reasonable length
                                        zoning_data['zoning_district'] = value_str
                                        print(f"Found zoning district: '{value_str}' in field '{key}'")
                                
                                # Other zoning attributes
                                elif 'height' in key_lower and not zoning_data['height_limit'] and any(char.isdigit() for char in value_str):
                                    zoning_data['height_limit'] = value_str
                                elif ('far' in key_lower or 'floor area ratio' in key_lower) and not zoning_data['far_limit'] and any(char.isdigit() for char in value_str):
                                    zoning_data['far_limit'] = value_str
                                elif 'overlay' in key_lower and not zoning_data['overlay_district']:
                                    zoning_data['overlay_district'] = value_str
                                elif any(word in key_lower for word in ['plan', 'area', 'neighborhood']) and not zoning_data['planning_area']:
                                    if len(value_str) > 3 and len(value_str) <= 50:  # Reasonable length
                                        zoning_data['planning_area'] = value_str
                        
                        # If we got a valid zoning district, set source and break
                        if zoning_data['zoning_district'] and zoning_data['zoning_district'].lower() not in ['null', 'none']:
                            zoning_data['zoning_source'] = 'Boston GIS Services'
                            print(f"Successfully found zoning: {zoning_data['zoning_district']}")
                            break
                        else:
                            print("No valid zoning district found in this endpoint's results")
                            
            except Exception as e:
                print(f"Error with endpoint {endpoint}: {e}")
                continue
    
    except Exception as e:
        print(f"Error with GIS services: {e}")
    
    # Try alternative data sources if no zoning found
    if not zoning_data['zoning_district']:
        try:
            # Try Boston Open Data portal
            data_portal_endpoints = [
                "https://data.boston.gov/api/3/action/datastore_search",
                "https://opendata.boston.gov/api/3/action/datastore_search"
            ]
            
            for portal_url in data_portal_endpoints:
                try:
                    # Search for zoning-related datasets
                    list_params = {'action': 'package_list'}
                    list_response = requests.get(portal_url.replace('datastore_search', 'package_list'), 
                                               params=list_params, timeout=10)
                    
                    if list_response.status_code == 200:
                        packages = list_response.json().get('result', [])
                        zoning_packages = [p for p in packages if 'zon' in str(p).lower()]
                        print(f"Found potential zoning datasets: {zoning_packages[:3]}")
                        
                except Exception as e:
                    print(f"Error exploring data portal {portal_url}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error with data portal search: {e}")
    
    # If still no data, try to infer basic zoning from neighborhood patterns
    if not zoning_data['zoning_district']:
        neighborhood_zone = infer_zoning_from_location(lat, lon)
        if neighborhood_zone:
            zoning_data.update(neighborhood_zone)
            zoning_data['zoning_source'] = 'Inferred from location'
    
    return zoning_data

def infer_zoning_from_location(lat: float, lon: float) -> Dict[str, Optional[str]]:
    """Infer basic zoning information from geographic location in Boston"""
    
    # Basic Boston neighborhood zones based on approximate coordinates
    # This is a fallback when APIs don't work
    
    inferred_data = {}
    
    # Allston/Brighton area (approximate bounds)
    if 42.34 <= lat <= 42.37 and -71.15 <= lon <= -71.11:
        inferred_data = {
            'zoning_district': '2F-5000',  # Common in Allston/Brighton
            'zoning_code': 'Allston/Brighton Neighborhood District',
            'height_limit': '35 ft',
            'far_limit': '0.6',
            'planning_area': 'Allston/Brighton Neighborhood District',
            'allowed_uses': 'Two-family dwelling, Single-family dwelling'
        }
    
    # Back Bay/South End area
    elif 42.34 <= lat <= 42.36 and -71.09 <= lon <= -71.06:
        inferred_data = {
            'zoning_district': 'R-8',
            'zoning_code': 'High-density residential', 
            'height_limit': '80 ft',
            'far_limit': '3.0',
            'planning_area': 'Back Bay/South End'
        }
    
    # Downtown/Financial District
    elif 42.35 <= lat <= 42.36 and -71.06 <= lon <= -71.05:
        inferred_data = {
            'zoning_district': 'B-8',
            'zoning_code': 'High-density commercial',
            'height_limit': 'No limit',
            'far_limit': '8.0+',
            'planning_area': 'Downtown'
        }
    
    # Cambridge Street Corridor
    elif 42.36 <= lat <= 42.37 and -71.07 <= lon <= -71.05:
        inferred_data = {
            'zoning_district': 'B-2',
            'zoning_code': 'Neighborhood business',
            'height_limit': '55 ft', 
            'far_limit': '2.0',
            'planning_area': 'Cambridge Street District'
        }
        
    # North End
    elif 42.36 <= lat <= 42.37 and -71.06 <= lon <= -71.04:
        inferred_data = {
            'zoning_district': 'R-4',
            'zoning_code': 'Multi-family residential',
            'height_limit': '35 ft',
            'far_limit': '1.0',
            'planning_area': 'North End'
        }
    
    # Dorchester
    elif 42.28 <= lat <= 42.32 and -71.10 <= lon <= -71.05:
        inferred_data = {
            'zoning_district': 'R-2',
            'zoning_code': 'Two-family residential',
            'height_limit': '35 ft',
            'far_limit': '0.7',
            'planning_area': 'Dorchester'
        }
    
    # Roxbury
    elif 42.31 <= lat <= 42.34 and -71.10 <= lon <= -71.08:
        inferred_data = {
            'zoning_district': 'R-2',
            'zoning_code': 'Mixed residential',
            'height_limit': '35 ft',
            'far_limit': '0.8',
            'planning_area': 'Roxbury'
        }
    
    # Jamaica Plain
    elif 42.30 <= lat <= 42.33 and -71.12 <= lon <= -71.10:
        inferred_data = {
            'zoning_district': 'R-4', 
            'zoning_code': 'Multi-family residential',
            'height_limit': '35 ft',
            'far_limit': '1.0',
            'planning_area': 'Jamaica Plain'
        }
        
    return inferred_data

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
            'side_setback': '8 ft',
            'rear_setback': '25 ft',
            'max_lot_coverage': '50%',
            'allowed_uses': ['Two-family dwelling', 'Single-family dwelling', 'Accessory uses'],
            'conditional_uses': ['Home occupation', 'Accessory dwelling unit'],
            'design_standards': ['Must comply with Allston-Brighton Neighborhood District requirements']
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
    
    if zoning_district and zoning_district in zoning_mappings:
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
    
    # Analyze based on zoning district (with proper null checks)
    district = zoning_info.get('zoning_district', '')
    
    if district and isinstance(district, str):
        if district.startswith('R-') or '2F-' in district:
            potential['mixed_use_potential'] = 'Limited'
            potential['article_80_required'] = 'If over 20,000 sq ft'
            potential['development_complexity'] = 'Medium'
        elif district.startswith('B-'):
            potential['mixed_use_potential'] = 'High'
            potential['article_80_required'] = 'If over 20,000 sq ft'
            potential['development_complexity'] = 'Medium'
            
        # Specific analysis for 2F-5000
        if district == '2F-5000':
            potential['upzoning_opportunity'] = 'Possible - two-family to multi-family conversion'
            potential['density_bonus_eligible'] = 'Transit-oriented development potential'
            potential['affordable_housing_req'] = 'Required if >10 units'
    
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