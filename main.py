import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, List, Optional

# Base URL for the Boston assessment search
base_url = 'https://www.cityofboston.gov/assessing/search/'

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

def get_building_value(soup) -> Dict[str, Optional[str]]:
    """Extract building values from the page"""
    values = {}
    
    # Look for value patterns in the text
    page_text = soup.get_text()
    
    # Common patterns for FY2025 values
    fy2025_patterns = [
        (r'FY2025 Building value[:\s]*\$?([\d,]+\.?\d*)', 'FY2025 Building value'),
        (r'FY2025 Land [Vv]alue[:\s]*\$?([\d,]+\.?\d*)', 'FY2025 Land value'),
        (r'FY2025 Total.*?[Vv]alue[:\s]*\$?([\d,]+\.?\d*)', 'FY2025 Total value')
    ]
    
    for pattern, key in fy2025_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '')
            values[key] = f"${value}"
    
    return values

def get_property_data_by_parcel_id(parcel_id: str) -> Dict[str, Optional[str]]:
    """Get property data using just the parcel ID"""
    
    # Use empty strings for street components when we only have parcel ID
    return get_enhanced_parcel_data(parcel_id, "", "", "", "")

def format_property_data_for_llm(property_data: Dict[str, Optional[str]]) -> str:
    """
    Format property data in a structured way that's conducive for LLM processing.
    
    Args:
        property_data: Dictionary containing property information
        
    Returns:
        Formatted string with property information organized in clear sections
    """
    if not property_data:
        return "No property data available."
    
    # Initialize sections
    sections = []
    
    # Basic Property Information
    basic_info = []
    if property_data.get('address'):
        basic_info.append(f"Address: {property_data['address']}")
    if property_data.get('unit_number'):
        basic_info.append(f"Unit: {property_data['unit_number']}")
    if property_data.get('parcel_id'):
        basic_info.append(f"Parcel ID: {property_data['parcel_id']}")
    if property_data.get('property_type'):
        basic_info.append(f"Property Type: {property_data['property_type']}")
    if property_data.get('classification_code'):
        basic_info.append(f"Classification: {property_data['classification_code']}")
    
    if basic_info:
        sections.append("PROPERTY IDENTIFICATION:\n" + "\n".join(basic_info))
    
    # Physical Characteristics
    physical_info = []
    if property_data.get('lot_size'):
        physical_info.append(f"Lot Size: {property_data['lot_size']}")
    if property_data.get('living_area'):
        physical_info.append(f"Living Area: {property_data['living_area']}")
    if property_data.get('year_built'):
        physical_info.append(f"Year Built: {property_data['year_built']}")
    if property_data.get('stories'):
        physical_info.append(f"Stories: {property_data['stories']}")
    if property_data.get('building_style'):
        physical_info.append(f"Style: {property_data['building_style']}")
    
    if physical_info:
        sections.append("PHYSICAL CHARACTERISTICS:\n" + "\n".join(physical_info))
    
    # Interior Details
    interior_info = []
    if property_data.get('bedrooms'):
        interior_info.append(f"Bedrooms: {property_data['bedrooms']}")
    if property_data.get('bathrooms'):
        interior_info.append(f"Bathrooms: {property_data['bathrooms']}")
    if property_data.get('total_rooms'):
        interior_info.append(f"Total Rooms: {property_data['total_rooms']}")
    if property_data.get('number_of_kitchens'):
        interior_info.append(f"Kitchens: {property_data['number_of_kitchens']}")
    if property_data.get('parking_spaces'):
        interior_info.append(f"Parking Spaces: {property_data['parking_spaces']}")
    
    if interior_info:
        sections.append("INTERIOR DETAILS:\n" + "\n".join(interior_info))
    
    # Condition and Features
    condition_info = []
    if property_data.get('interior_condition'):
        condition_info.append(f"Interior Condition: {property_data['interior_condition']}")
    if property_data.get('exterior_condition'):
        condition_info.append(f"Exterior Condition: {property_data['exterior_condition']}")
    if property_data.get('exterior_finish'):
        condition_info.append(f"Exterior Finish: {property_data['exterior_finish']}")
    if property_data.get('foundation'):
        condition_info.append(f"Foundation: {property_data['foundation']}")
    if property_data.get('heat_type'):
        condition_info.append(f"Heating: {property_data['heat_type']}")
    if property_data.get('ac_type'):
        condition_info.append(f"Air Conditioning: {property_data['ac_type']}")
    
    if condition_info:
        sections.append("CONDITION AND FEATURES:\n" + "\n".join(condition_info))
    
    # Financial Information
    financial_info = []
    if property_data.get('fy2025_building_value'):
        financial_info.append(f"Building Value: {property_data['fy2025_building_value']}")
    if property_data.get('fy2025_land_value'):
        financial_info.append(f"Land Value: {property_data['fy2025_land_value']}")
    if property_data.get('fy2025_total_value'):
        financial_info.append(f"Total Assessed Value: {property_data['fy2025_total_value']}")
    if property_data.get('previous_year_value'):
        financial_info.append(f"Previous Year Value: {property_data['previous_year_value']}")
    
    if financial_info:
        sections.append("FINANCIAL INFORMATION:\n" + "\n".join(financial_info))
    
    # Ownership Information
    ownership_info = []
    if property_data.get('owner'):
        ownership_info.append(f"Owner: {property_data['owner']}")
    if property_data.get('owner_address'):
        ownership_info.append(f"Owner Address: {property_data['owner_address']}")
    
    if ownership_info:
        sections.append("OWNERSHIP INFORMATION:\n" + "\n".join(ownership_info))
    
    # Zoning and Land Use
    zoning_info = []
    if property_data.get('zoning'):
        zoning_info.append(f"Zoning: {property_data['zoning']}")
    if property_data.get('land_use'):
        zoning_info.append(f"Land Use: {property_data['land_use']}")
    if property_data.get('building_use'):
        zoning_info.append(f"Building Use: {property_data['building_use']}")
    
    if zoning_info:
        sections.append("ZONING AND LAND USE:\n" + "\n".join(zoning_info))
    
    # Combine all sections with clear separators
    formatted_output = "\n\n".join(sections)
    
    return formatted_output


if __name__ == "__main__":
    # Test with a few different properties
    test_address = "263 N Harvard St"
    print(f"Testing parcel data extraction for: {test_address}")
    
    # Test the enhanced parcel data function
    result = get_enhanced_parcel_data("", "263", "N Harvard", "St", "")
    
    print(f"\nResults for {test_address}:")
    print(json.dumps(result, indent=2))
    
    # Test the LLM formatting function with example data
    print("\n" + "="*50)
    print("TESTING LLM FORMATTING FUNCTION")
    print("="*50)
    
    # Example property data (the one provided by user)
    example_data = {
        'parcel_id': '2201486000',
        'address': '263 N Harvard St',
        'unit_number': '',
        'property_type': 'Two Family',
        'classification_code': '0104 (Residential Property  / TWO-FAM DWELLING)',
        'lot_size': '11,525 sq ft',
        'living_area': '3,539 sq ft',
        'year_built': '1890',
        'bedrooms': '6',
        'bathrooms': '3',
        'parking_spaces': '7',
        'stories': '2.0',
        'fy2025_building_value': '$923,500.00',
        'fy2025_land_value': '$684,200.00',
        'fy2025_total_value': '$1,607,700.00',
        'previous_year_value': None,
        'owner': 'THE HELPING HAND TRUST',
        'owner_address': '316 NORTH HARVARD ST C/O JAMES GEORGES ALLSTON MA 02134',
        'zoning': None,
        'land_use': '104 - TWO-FAM DWELLING',
        'building_use': None,
        'exterior_condition': 'Average',
        'building_style': 'Conventional',
        'total_rooms': '11',
        'number_of_kitchens': '2',
        'ac_type': 'None',
        'heat_type': 'Ht Water/Steam',
        'interior_condition': 'Average',
        'exterior_finish': 'Wood Shake',
        'foundation': 'Stone'
    }
    
    formatted_output = format_property_data_for_llm(example_data)
    print(formatted_output)
