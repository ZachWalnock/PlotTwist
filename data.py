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
    
    # Try to parse the search results table first
    # Look for table rows that contain parcel information
    rows = soup.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 4:  # Parcel results usually have multiple columns
            for i, cell in enumerate(cells):
                cell_text = cell.get_text(strip=True)
                
                # Check if this looks like a parcel ID (numeric)
                if cell_text.isdigit() and len(cell_text) >= 10:
                    property_data['parcel_id'] = cell_text
                
                # Check if this looks like a property value (starts with $)
                if cell_text.startswith('$') and ',' in cell_text:
                    property_data['fy2025_total_value'] = cell_text
                
                # Check for owner information (usually in caps)
                if cell_text.isupper() and len(cell_text) > 5 and ('TRUST' in cell_text or 'LLC' in cell_text or 'CORP' in cell_text):
                    property_data['owner'] = cell_text
    
    # Look for "Details" link to get more detailed information
    details_links = soup.find_all('a', href=True)
    for link in details_links:
        link_text = link.get_text(strip=True).lower()
        link_href = link.get('href', '').lower()
        
        if 'details' in link_href or link_text == 'details':
            details_url = link.get('href')
            
            # Handle different URL formats
            if details_url.startswith('?'):
                details_url = 'https://www.cityofboston.gov/assessing/search/' + details_url
            elif not details_url.startswith('http'):
                details_url = 'https://www.cityofboston.gov' + details_url
            
            print(f"Following details link: {details_url}")
            
            # Fetch detailed property information
            try:
                details_response = requests.get(details_url, headers=headers, timeout=10)
                details_response.raise_for_status()
                details_soup = BeautifulSoup(details_response.content, 'html.parser')
                
                # Extract detailed information from the details page
                detailed_data = parse_property_details(details_soup)
                property_data.update(detailed_data)
                
                print(f"Successfully extracted {len(detailed_data)} additional fields from details page")
                break
                
            except Exception as e:
                print(f"Error fetching property details from {details_url}: {e}")
                continue
    
    # Extract building values if available on main page
    building_values = get_building_value(soup)
    if any(building_values.values()):
        property_data.update({
            'fy2025_building_value': building_values.get("FY2025 Building value"),
            'fy2025_land_value': building_values.get("FY2025 Land value"),
            'fy2025_total_value': building_values.get("FY2025 Total value")
        })
    
    return property_data

def parse_property_details(soup) -> Dict[str, Optional[str]]:
    """Parse detailed property information from the Boston assessment details page"""
    details = {}
    
    # Parse the main property information table (class="mainCategoryModuleText")
    main_rows = soup.find_all('tr', class_='mainCategoryModuleText')
    for row in main_rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            label = cells[0].get_text(strip=True).replace(':', '').lower()
            value = cells[1].get_text(strip=True)
            
            # Map the labels to our data structure
            if 'parcel id' in label:
                details['parcel_id'] = value
            elif 'property type' in label:
                details['property_type'] = value
            elif 'classification code' in label:
                details['classification_code'] = value
            elif 'lot size' in label:
                details['lot_size'] = value
            elif 'living area' in label:
                details['living_area'] = value
            elif 'year built' in label:
                details['year_built'] = value
            elif 'owner on' in label and not details.get('owner'):
                # Extract owner from the link or text
                owner_link = cells[1].find('a')
                if owner_link:
                    details['owner'] = owner_link.get_text(strip=True)
                else:
                    details['owner'] = value
            elif 'owner\'s mailing address' in label:
                details['owner_address'] = value
    
    # Parse financial data from the Value/Tax section
    value_cells = soup.find_all('td')
    for i, cell in enumerate(value_cells):
        text = cell.get_text(strip=True)
        
        if 'FY2025 Building value:' in text:
            # Look for the value in the next cell or extract from current cell
            try:
                if i + 1 < len(value_cells):
                    next_cell = value_cells[i + 1]
                    value_text = next_cell.get_text(strip=True)
                    if value_text.startswith('$'):
                        details['fy2025_building_value'] = value_text
            except:
                pass
                
        elif 'FY2025 Land Value:' in text:
            try:
                if i + 1 < len(value_cells):
                    next_cell = value_cells[i + 1]
                    value_text = next_cell.get_text(strip=True)
                    if value_text.startswith('$'):
                        details['fy2025_land_value'] = value_text
            except:
                pass
                
        elif 'FY2025 Total Assessed Value:' in text:
            try:
                if i + 1 < len(value_cells):
                    next_cell = value_cells[i + 1]
                    value_text = next_cell.get_text(strip=True)
                    if value_text.startswith('$'):
                        details['fy2025_total_value'] = value_text
            except:
                pass
    
    # Parse detailed building attributes (the italicized fields in BUILDING 1 section)
    italic_cells = soup.find_all('i')
    for italic in italic_cells:
        label = italic.get_text(strip=True).replace(':', '').lower()
        
        # Find the corresponding value in the next cell
        parent_row = italic.find_parent('tr')
        if parent_row:
            cells = parent_row.find_all('td')
            if len(cells) >= 2:
                value = cells[1].get_text(strip=True)
                
                # Map detailed attributes
                if 'total rooms' in label:
                    details['total_rooms'] = value
                elif 'bedrooms' in label:
                    details['bedrooms'] = value
                elif 'bathrooms' in label and 'half' not in label:
                    details['bathrooms'] = value
                elif 'number of kitchens' in label:
                    details['number_of_kitchens'] = value
                elif 'parking spots' in label:
                    details['parking_spaces'] = value
                elif 'story height' in label:
                    details['stories'] = value
                elif 'interior condition' in label:
                    details['interior_condition'] = value
                elif 'exterior condition' in label:
                    details['exterior_condition'] = value
                elif 'land use' in label:
                    details['land_use'] = value
                elif 'style' in label and 'bath' not in label and 'kitchen' not in label:
                    details['building_style'] = value
                elif 'heat type' in label:
                    details['heat_type'] = value
                elif 'ac type' in label:
                    details['ac_type'] = value
                elif 'exterior finish' in label:
                    details['exterior_finish'] = value
                elif 'foundation' in label:
                    details['foundation'] = value
    
    return details

def get_parcel_basics(parcelID: str, streetNumber: str, streetName: str, streetSuffix: str, unitNumber: str) -> Dict[str, Optional[str]]:
    # Use the enhanced version instead of the old function
    return get_enhanced_parcel_data(parcelID, streetNumber, streetName, streetSuffix, unitNumber)

if __name__ == "__main__":
    print(get_parcel_basics("", "263", "N HARVARD", "", ""))