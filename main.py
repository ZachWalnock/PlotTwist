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
        for i, td in enumerate(tds):
            text = td.get_text(strip=True)
            if "FY2025 Building value:" in text:
                # Look for the next td with align="right" in the same row
                if i + 1 < len(tds):
                    next_td = tds[i + 1]
                    if next_td.get('align') == 'right':
                        information["FY2025 Building value"] = next_td.get_text(strip=True)
            elif "FY2025 Land value:" in text:
                if i + 1 < len(tds):
                    next_td = tds[i + 1]
                    if next_td.get('align') == 'right':
                        information["FY2025 Land value"] = next_td.get_text(strip=True)
            elif "FY2025 Total value:" in text:
                if i + 1 < len(tds):
                    next_td = tds[i + 1]
                    if next_td.get('align') == 'right':
                        information["FY2025 Total value"] = next_td.get_text(strip=True)
    
    return information

def get_parcel_basics(parcelID: str, streetNumber: str, streetName: str, streetSuffix: str, unitNumber: str) -> Dict[str, Optional[str]]:
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
    
    # Find the "Details" link
    details_link = soup.find('a', string=re.compile(r'Details', re.IGNORECASE), href=True)
    if not details_link:
        print("No details link found on search page")
    
    map_link = soup.find('a', string=re.compile(r'Map', re.IGNORECASE), href=True)
    if not map_link:
        print("No map link found on search page")
    
    # return get_parcel_information(details_link.get('href')), get_building_value(soup)
    return get_building_value(soup)

print(get_parcel_basics("", "263", "N HARVARD", "", ""))