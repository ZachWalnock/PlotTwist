import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Optional

base_url = "https://www.cityofboston.gov/assessing/search/"

def get_parcel_information(parcelID: str, headers=None) -> Dict[str, Optional[str]]:
    params = {
        'pid': parcelID,
    }

    response = requests.get(base_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    module_elements = soup.find_all(class_="mainCategoryModuleText")
    
    result = {
        'size': None,
        'image_url': None,
        'living_area': None,
        'owner': None
    }
    
    information_sources = {"Parcel ID": None, "Address": None, "Property Type": None, "Classification Code": None, "Lot Size": None, "Living Area": None, "Owner": None, "Living Area": None, "Owner": None}
    i = 0
    for element in module_elements:
        right_aligned_children = element.find_all(attrs={"align": "right"})
        
        for child in right_aligned_children:
            if i == len(information_sources):
                return information_sources
            topic = list(information_sources.keys())[i]
            text = child.get_text(strip=True)
            information_sources[topic] = text
            i += 1
    
    return information_sources

def get_building_value(soup):
    information = {
        "FY2025 Building value": None,
        "FY2025 Land value": None,
        "FY2025 Total value": None
    }
    
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        for td in tds:
            text = td.get_text(strip=True)
            if "FY2025 Building value:" in text:
                # Get the next td or the text after the colon
                next_td = td.find_next_sibling('td')
                if next_td:
                    information["FY2025 Building value"] = next_td.get_text(strip=True)
                else:
                    # If no next td, try to extract value after colon
                    parts = text.split(":")
                    if len(parts) > 1:
                        information["FY2025 Building value"] = parts[1].strip()
            elif "FY2025 Land value:" in text:
                next_td = td.find_next_sibling('td')
                if next_td:
                    information["FY2025 Land value"] = next_td.get_text(strip=True)
                else:
                    parts = text.split(":")
                    if len(parts) > 1:
                        information["FY2025 Land value"] = parts[1].strip()
            elif "FY2025 Total value:" in text:
                next_td = td.find_next_sibling('td')
                if next_td:
                    information["FY2025 Total value"] = next_td.get_text(strip=True)
                else:
                    parts = text.split(":")
                    if len(parts) > 1:
                        information["FY2025 Total value"] = parts[1].strip()
    
    return information

def get_enhanced_parcel_data(parcelID: str, streetNumber: str, streetName: str, streetSuffix: str, unitNumber: str) -> Dict[str, Optional[str]]:
    """Enhanced parcel data extraction with all property details needed for development analysis"""
    # Headers to mimic a real browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    params = {
        'parcelID': parcelID,
        'streetNumber': streetNumber,
        'streetName': streetName,
        'streetSuffix': streetSuffix,
        'unitNumber': unitNumber
    }
    
    response = requests.get(base_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize comprehensive property data structure
    property_data = {
        # Basic identification
        'parcel_id': parcelID,
        'address': f"{streetNumber} {streetName} {streetSuffix}".strip(),
        'unit_number': unitNumber,
        
        # Property characteristics
        'property_type': None,
        'classification_code': None,
        'lot_size': None,
        'living_area': None,
        'year_built': None,
        'bedrooms': None,
        'bathrooms': None,
        'parking_spaces': None,
        'stories': None,
        
        # Financial data
        'fy2025_building_value': None,
        'fy2025_land_value': None,
        'fy2025_total_value': None,
        'previous_year_value': None,
        
        # Ownership
        'owner': None,
        'owner_address': None,
        
        # Additional details
        'zoning': None,
        'land_use': None,
        'building_use': None,
        'exterior_condition': None,
    }
    
    # Extract building values
    building_values = get_building_value(soup)
    property_data.update({
        'fy2025_building_value': building_values.get("FY2025 Building value"),
        'fy2025_land_value': building_values.get("FY2025 Land value"),
        'fy2025_total_value': building_values.get("FY2025 Total value")
    })
    
    # Extract detailed property information from tables
    # Look for property details in various table structures
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)
                
                # Map labels to our property data fields
                if 'year built' in label or 'built' in label:
                    property_data['year_built'] = value
                elif 'lot size' in label:
                    property_data['lot_size'] = value
                elif 'living area' in label or 'floor area' in label:
                    property_data['living_area'] = value
                elif 'bedrooms' in label or 'bed' in label:
                    property_data['bedrooms'] = value
                elif 'bathrooms' in label or 'bath' in label:
                    property_data['bathrooms'] = value
                elif 'parking' in label:
                    property_data['parking_spaces'] = value
                elif 'stories' in label or 'floors' in label:
                    property_data['stories'] = value
                elif 'owner' in label and not property_data['owner']:
                    property_data['owner'] = value
                elif 'property type' in label:
                    property_data['property_type'] = value
                elif 'classification' in label:
                    property_data['classification_code'] = value
                elif 'zoning' in label:
                    property_data['zoning'] = value
                elif 'land use' in label:
                    property_data['land_use'] = value
                elif 'building use' in label:
                    property_data['building_use'] = value
                elif 'condition' in label:
                    property_data['exterior_condition'] = value
    
    # Try to find owner address in owner information section
    owner_sections = soup.find_all(text=re.compile(r'owner', re.IGNORECASE))
    for section in owner_sections:
        parent = section.parent
        if parent:
            # Look for address patterns in nearby text
            for sibling in parent.find_next_siblings():
                text = sibling.get_text(strip=True)
                if re.search(r'\d+.*(?:st|ave|rd|blvd|street|avenue|road|boulevard)', text, re.IGNORECASE):
                    property_data['owner_address'] = text
                    break
    
    return property_data

def get_parcel_basics(parcelID: str, streetNumber: str, streetName: str, streetSuffix: str, unitNumber: str) -> Dict[str, Optional[str]]:
    # Use the enhanced version instead of the old function
    return get_enhanced_parcel_data(parcelID, streetNumber, streetName, streetSuffix, unitNumber)

if __name__ == "__main__":
    print(get_parcel_basics("", "263", "N HARVARD", "", ""))