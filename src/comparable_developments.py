from __future__ import annotations

import csv
import time
import asyncio
from dataclasses import dataclass
from typing import List, Optional, Dict
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import aiohttp
from bs4 import BeautifulSoup
import json


@dataclass
class Development:
    address: str
    link: str
    latitude: float
    longitude: float
    distance: float = 0.0


BASE = "https://www.bostonplans.org"
LIST_URL = f"{BASE}/projects/development-projects"

def haversine_distance_miles(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (specified in decimal degrees).
    Returns distance in miles.
    """
    from math import radians, sin, cos, sqrt, atan2

    # Radius of Earth in miles
    R = 3958.8

    # Convert decimal degrees to radians
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


# ========== ASYNC GEOCODING FUNCTIONS ==========

async def geocode_boston_address_async(address: str) -> Optional[Dict]:
    """
    Asynchronous version of geocoding that makes concurrent requests to all services.
    Much faster than the sequential version.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        # Create tasks for all geocoding methods
        tasks = [
            _geocode_with_arcgis_world_async(session, address),
            _geocode_with_boston_arcgis_async(session, address),
            _geocode_with_nominatim_async(session, address)
        ]
        
        # Wait for the first successful result
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                if result:
                    return {
                        'latitude': result['y'],
                        'longitude': result['x'],
                        'score': result['score'],
                        'address': result['address'],
                        'method': result.get('method', 'unknown')
                    }
            except Exception as e:
                continue
        
        return None

async def _geocode_with_arcgis_world_async(session: aiohttp.ClientSession, address: str) -> Optional[Dict]:
    """Async version of ArcGIS World geocoding"""
    try:
        geocode_url = "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"
        params = {
            'SingleLine': address,
            'f': 'json',
            'outSR': '4326',
            'maxLocations': 1,
            'category': 'Address',
            'countryCode': 'USA'
        }
        
        async with session.get(geocode_url, params=params) as response:
            data = await response.json()
            
            if data.get('candidates') and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                location = candidate['location']
                return {
                    'x': location['x'],
                    'y': location['y'],
                    'score': candidate['score'],
                    'address': candidate['address'],
                    'method': 'arcgis_world'
                }
    except Exception:
        pass
    return None

async def _geocode_with_boston_arcgis_async(session: aiohttp.ClientSession, address: str) -> Optional[Dict]:
    """Async version of Boston ArcGIS geocoding"""
    try:
        geocode_url = "https://services.arcgis.com/sFnw0xNflSi8J0qw/arcgis/rest/services/Boston_Composite_Locator/GeocodeServer/findAddressCandidates"
        params = {
            'SingleLine': address,
            'f': 'json',
            'outSR': '4326',
            'maxLocations': 1
        }
        
        async with session.get(geocode_url, params=params) as response:
            data = await response.json()
            
            if data.get('candidates') and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                location = candidate['location']
                return {
                    'x': location['x'],
                    'y': location['y'],
                    'score': candidate['score'],
                    'address': candidate['address'],
                    'method': 'boston_arcgis'
                }
    except Exception:
        pass
    return None

async def _geocode_with_nominatim_async(session: aiohttp.ClientSession, address: str) -> Optional[Dict]:
    """Async version of Nominatim geocoding"""
    try:
        geocode_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'us',
            'bounded': 1,
            'viewbox': '-71.191155,42.227925,-70.986365,42.400819'
        }
        headers = {'User-Agent': 'BostonZoningTool/1.0'}
        
        async with session.get(geocode_url, params=params, headers=headers) as response:
            data = await response.json()
            
            if data and len(data) > 0:
                result = data[0]
                return {
                    'x': float(result['lon']),
                    'y': float(result['lat']),
                    'score': 100,
                    'address': result['display_name'],
                    'method': 'nominatim'
                }
    except Exception:
        pass
    return None

# ========== BATCH GEOCODING FUNCTIONS ==========

async def geocode_addresses_batch_async(developments: List[Development], batch_size: int = 10) -> List[Optional[Dict]]:
    """
    Asynchronous batch geocoding with controlled concurrency.
    Most efficient for large numbers of addresses.
    
    Args:
        addresses: List of address strings
        batch_size: Number of addresses to process concurrently
    
    Returns:
        List of results, one per address (None if geocoding failed)
    """
    results = [None] * len(developments)
    
    # Process in batches to avoid overwhelming the APIs
    for i in range(0, len(developments), batch_size):
        batch = developments[i:i + batch_size]
        batch_tasks = [geocode_boston_address_async(d.address) for d in batch]
        
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        # Store results
        for j, result in enumerate(batch_results):
            if isinstance(result, Exception):
                print(f"Geocoding failed for address at index {i+j}: {result}")
                results[i + j] = None
            else:
                results[i + j] = result
        
        # Small delay between batches to be respectful to APIs
        if i + batch_size < len(developments):
            await asyncio.sleep(0.1)
    
    return results


def parse_list_page(html: str, base_url: str) -> List[Development]:
    """
    Parse one listing page. Tries the classes you observed first,
    then falls back to a generic selector for project links.
    """
    soup = BeautifulSoup(html, "html.parser")
    devs: List[Development] = []

    # 1) Primary path: your observed DOM
    wrapper = soup.find("div", class_="projectTableWrapper")
    if wrapper:
        for card in wrapper.find_all("div", class_="devprojectTable"):
            a = card.find("a", href=True)
            if a:
                address = a.get_text(strip=True)
                link = urljoin(base_url, a["href"])
                if address and "/projects/development-projects" in link:
                    devs.append(Development(address=address, link=link))
    # 2) Fallback path: any project links in the list view
    if not devs:
        # These anchors are the project entries (their text is often the address)
        for a in soup.select('a[href*="/projects/development-projects/"]'):
            text = a.get_text(strip=True)
            href = a.get("href", "")
            if not text or not href:
                continue
            # Skip obvious non-item links (nav, category headers, etc.)
            if "Development Projects & Plans" in text or "Projects & Plans" in text:
                continue
            link = urljoin(base_url, href)
            devs.append(Development(address=text, link=link, latitude=float('nan'), longitude=float('nan')))

        # Deduplicate by link
        seen = set()
        unique = []
        for d in devs:
            if d.link not in seen:
                seen.add(d.link)
                unique.append(d)
        devs = unique

    return devs


def scrape_developments(num_pages: int = 100, delay_sec: float = 0.4) -> List[Development]:
    """
    Scrape up to `num_pages` pages of the Development Projects listing.
    Page 1 is the base URL (no ?page=), pages >= 2 use ?page=N.
    """
    session = requests.Session()
    session.headers.update({
        # Friendly UA; helps some sites serve full HTML
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36"
    })

    all_devs: List[Development] = []

    for page in range(1, num_pages + 1):
        url = LIST_URL if page == 1 else f"{LIST_URL}?page={page}"
        resp = session.get(url, timeout=30)
        resp.raise_for_status()

        page_devs = parse_list_page(resp.text, BASE)
        all_devs.extend(page_devs)

        print(f"Page {page}: {len(page_devs)} items")
        time.sleep(delay_sec)  # be polite

    return all_devs


async def main_async():
    target_address = "263 N Harvard St, Allston, MA 02134"
    print("Geocoding target address...")
    target_result = await geocode_boston_address_async(target_address)
    if not target_result:
        print("Failed to geocode target address!")
        return
        
    print(f"Target coords: {target_result['latitude']}, {target_result['longitude']}")
    
    print("Scraping developments...")
    developments = scrape_developments(num_pages=20)
    print(f"Found {len(developments)} developments")
    
    with open("cached-developments.json", "r", encoding="utf-8") as f:
        cached_developments = json.load(f)
    cached_addresses = [d["address"] for d in cached_developments]
    # Extract addresses for batch geocoding
    developments_to_geocode = [d for d in developments if d.address not in cached_addresses]
    print(f"Geocoding {len(developments_to_geocode)} developments...")
    geocoded_developments = [d for d in developments if d.address in cached_addresses]
    for d in geocoded_developments:
        for c in cached_developments:
            if c["address"] == d.address:
                d.latitude = c["latitude"]
                d.longitude = c["longitude"]
                d.distance = haversine_distance_miles(
                    d.latitude, d.longitude, 
                    target_result['latitude'], target_result['longitude']
                )
                break
    
    print("Batch geocoding all addresses (async)...")
    start_time = time.time()
    geocode_results = await geocode_addresses_batch_async(developments_to_geocode, batch_size=10)
    end_time = time.time()
    
    print(f"Geocoded {len(developments_to_geocode)} addresses in {end_time - start_time:.2f} seconds")
    
    # Set coordinates and distances for developments that were geocoded
    for i, (dev, result) in enumerate(zip(developments_to_geocode, geocode_results)):
        if result:
            dev.latitude = result['latitude']
            dev.longitude = result['longitude']
            distance = haversine_distance_miles(
                dev.latitude, dev.longitude, 
                target_result['latitude'], target_result['longitude']
            )
            dev.distance = distance
            cached_developments.append(dev)
        else:
            dev.distance = float('inf')  # Failed geocoding
    
    developments = geocoded_developments + developments_to_geocode
    # Sort by distance
    developments.sort(key=lambda d: d.distance)
    
    # Write the 30 closest developments to a markdown file
    closest_developments = [d for d in developments if not (d.latitude == 0 and d.longitude == 0)][:30]
    with open("closest_developments.md", "w", encoding="utf-8") as md_file:
        for d in closest_developments:
            # Write address as a markdown heading with embedded link
            md_file.write(f"## [{d.address}]({d.link})\n")
            # Write distance below
            md_file.write(f"Distance from target: {d.distance:.2f} miles\n\n")
    print(f"\nWrote {len(closest_developments)} closest developments to closest_developments.md")
    

    with open("cached-developments.json", "w", encoding="utf-8") as f:
        json.dump(cached_developments, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(developments)} developments to cached-developments.json")


if __name__ == "__main__":
    asyncio.run(main_async())
