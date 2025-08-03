#!/usr/bin/env python3

import json
import sys
from address_data import geocode_address
from zoning_scraper import get_comprehensive_zoning_data
from main import get_enhanced_parcel_data

def test_complete_scraping(street_num, street_name, street_suffix, unit=""):
    """Test all webscraping components and return JSON output"""
    
    # Build address
    full_address = f"{street_num} {street_name} {street_suffix}"
    if unit:
        full_address += f" Unit {unit}"
    full_address_with_city = f"{full_address}, Boston, MA"
    
    print(f"Testing: {full_address_with_city}")
    print("-" * 60)
    
    # Initialize results
    results = {
        "input_address": full_address_with_city,
        "geocoding": {},
        "property_data": {},
        "zoning_data": {},
        "summary": {},
        "errors": []
    }
    
    # 1. Test Geocoding
    print("1. Running geocoding...")
    try:
        coords = geocode_address(full_address_with_city)
        if coords:
            results["geocoding"] = {
                "latitude": coords[0],
                "longitude": coords[1],
                "success": True
            }
            print(f"   ✓ Geocoded: {coords[0]:.6f}, {coords[1]:.6f}")
        else:
            results["geocoding"] = {"success": False, "error": "No coordinates found"}
            results["errors"].append("Geocoding failed")
            print("   ✗ Geocoding failed")
    except Exception as e:
        results["geocoding"] = {"success": False, "error": str(e)}
        results["errors"].append(f"Geocoding error: {e}")
        print(f"   ✗ Geocoding error: {e}")
    
    # 2. Test Property Data Scraping
    print("2. Running property data scraping...")
    try:
        property_data = get_enhanced_parcel_data("", street_num, street_name, street_suffix, unit)
        
        # Clean up None values for JSON output
        cleaned_property_data = {k: v for k, v in property_data.items() if v is not None}
        results["property_data"] = cleaned_property_data
        
        # Count fields with data
        fields_with_data = len(cleaned_property_data)
        print(f"   ✓ Found {fields_with_data} property fields with data")
        
        # Show key fields
        key_fields = ['parcel_id', 'property_type', 'fy2025_total_value', 'owner']
        for field in key_fields:
            if property_data.get(field):
                print(f"     - {field}: {property_data[field]}")
                
    except Exception as e:
        results["property_data"] = {"error": str(e)}
        results["errors"].append(f"Property scraping error: {e}")
        print(f"   ✗ Property scraping error: {e}")
    
    # 3. Test Zoning Data Scraping
    print("3. Running zoning data scraping...")
    try:
        zoning_data = get_comprehensive_zoning_data(full_address_with_city)
        
        # Clean up None values
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items() if v is not None and v != "" and v != []}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d if item is not None and item != ""]
            else:
                return d
        
        cleaned_zoning_data = clean_dict(zoning_data)
        results["zoning_data"] = cleaned_zoning_data
        
        # Show key zoning info
        zoning_info = zoning_data.get('zoning_info', {})
        district = zoning_info.get('zoning_district', 'Unknown')
        source = zoning_info.get('zoning_source', 'Unknown')
        height = zoning_info.get('height_limit', 'Unknown')
        
        print(f"   ✓ Zoning District: {district}")
        print(f"     - Source: {source}")
        print(f"     - Height Limit: {height}")
        
    except Exception as e:
        results["zoning_data"] = {"error": str(e)}
        results["errors"].append(f"Zoning scraping error: {e}")
        print(f"   ✗ Zoning scraping error: {e}")
    
    # 4. Create Summary
    results["summary"] = {
        "total_errors": len(results["errors"]),
        "geocoding_success": results["geocoding"].get("success", False),
        "property_fields_found": len(results["property_data"]) if "error" not in results["property_data"] else 0,
        "zoning_district": results["zoning_data"].get("zoning_info", {}).get("zoning_district", "Not found"),
        "property_value": results["property_data"].get("fy2025_total_value", "Not found")
    }
    
    return results

def main():
    # Default test addresses
    test_addresses = [
        ("263", "N Harvard", "St"),
        ("100", "Boylston", "St"),
        ("1", "City Hall", "Square")
    ]
    
    if len(sys.argv) >= 4:
        # Use command line arguments
        street_num = sys.argv[1]
        street_name = sys.argv[2]
        street_suffix = sys.argv[3]
        unit = sys.argv[4] if len(sys.argv) > 4 else ""
        
        results = test_complete_scraping(street_num, street_name, street_suffix, unit)
        
        print("\n" + "="*60)
        print("JSON OUTPUT:")
        print("="*60)
        print(json.dumps(results, indent=2))
        
        # Save to file
        filename = f"scraping_test_{street_num}_{street_name.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {filename}")
        
    elif len(sys.argv) == 2 and sys.argv[1] == "--all":
        # Test all default addresses
        all_results = {}
        
        for i, (num, name, suffix) in enumerate(test_addresses):
            print(f"\n{'='*80}")
            print(f"TEST {i+1}: {num} {name} {suffix}")
            print('='*80)
            
            results = test_complete_scraping(num, name, suffix)
            all_results[f"test_{i+1}_{num}_{name.replace(' ', '_')}"] = results
        
        print(f"\n{'='*80}")
        print("COMBINED JSON OUTPUT:")
        print('='*80)
        print(json.dumps(all_results, indent=2))
        
        # Save combined results
        with open("all_scraping_tests.json", 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\nAll results saved to: all_scraping_tests.json")
        
    else:
        # Show usage
        print("Usage:")
        print(f"  {sys.argv[0]} <street_num> <street_name> <street_suffix> [unit]")
        print(f"  {sys.argv[0]} --all")
        print("\nExamples:")
        print(f"  {sys.argv[0]} 263 'N Harvard' St")
        print(f"  {sys.argv[0]} 100 Boylston St")
        print(f"  {sys.argv[0]} --all")

if __name__ == "__main__":
    main() 