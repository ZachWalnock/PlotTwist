# boston_zoning_article_from_coords.py
import json
import re
import requests
from typing import Dict, Optional

BPDA_SUBDISTRICTS = "https://gis.bostonplans.org/hosting/rest/services/Zoning_Subdistricts_Data/FeatureServer/0/query"
BPDA_DISTRICTS    = "https://gis.bostonplans.org/hosting/rest/services/Zoning_Districts/FeatureServer/0/query"

# Known direct links to the "main" article page in Municode (not just the Tables page).
# This doesn't need to be exhaustive—there's a robust fallback below that always works.
ARTICLE_MAIN = {
    "13": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART13DIRE_S13-1DIRE",
    "50": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART50RONEDI",
    "51": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART51ALIGNEDI_REGULATIONS_APPLICABLE_PLANNED_DEVELOPMENT_AREAS_S51-49PLDEARPUBE",
    "53": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART53EABONEDI",
    "54": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART54NOENNEDI_IN_GENERAL_S54-6NOENCEARAR",
    "55": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART55JAPLNEDI",
    "56": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART56WERONEDI_REGULATIONS_GOVERNING_DESIGN_S56-37SCBURE",
    "59": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART59MIHINEDI_REGULATIONS_APPLICABLE_COMMUNITY_FACILITIES_SUBDISTRICTS_S59-20ESCOFASU",
    "61": "https://mcclibraryweb.azurewebsites.us/ma/boston/codes/redevelopment_authority?nodeId=ART61AUCINEDI_MISCELLANEOUS_PROVISIONS_S61-29DE",
    "62": "https://www.bostonplans.org/getattachment/b4ec97de-0c3c-4142-aaf9-b2301ec0aaa2",  # official PDF (Municode slugs vary)
    "65": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART65DONEDI_REGULATIONS_APPLICABLE_GREENBELT_PROTECTION_OVERLAY_DISTRICTS_S65-34ESGRPROVDI",
    "66": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART66TA",  # Fenway: tables are very helpful
    "67": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART67RONEDI_IN_GENERAL_S67-5COPA",
    "68": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART68SOBONEDI",
    "69": "https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART69AP",  # Appendix landing works; tables fallback below
    # Add more as you prefer; the fallback below covers everything else.
}

NEIGHBORHOOD_ARTICLES = {50,51,53,54,55,56,58,59,61,62,64,65,66,67,68,69}

def _arcgis_point_query(url: str, lat: float, lon: float, out_fields: str):
    """
    Spatially query an ArcGIS FeatureServer layer with a (lon,lat) point (WGS84).
    Returns the features list (may be empty).
    """
    params = {
        "f": "json",
        "returnGeometry": "false",
        "spatialRel": "esriSpatialRelIntersects",
        "geometry": json.dumps({"x": float(lon), "y": float(lat)}),
        "geometryType": "esriGeometryPoint",
        "inSR": 4326,  # WGS84
        "outFields": out_fields,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        # ArcGIS errors sometimes show in 200 responses
        raise RuntimeError(f"ArcGIS error: {data['error']}")
    return data.get("features", [])

def _first_numeric(s: str) -> Optional[str]:
    m = re.search(r"\d{1,3}", s or "")
    return m.group(0) if m else None

def _pick_best_article(candidates: Dict[str, dict]) -> Optional[str]:
    """
    If multiple overlapping polygons are returned (overlays etc.), prefer a neighborhood article (50–69, plus 64).
    Otherwise, just pick the first.
    """
    # Prefer neighborhood articles
    for art, _ in candidates.items():
        try:
            if int(art) in NEIGHBORHOOD_ARTICLES:
                return art
        except ValueError:
            pass
    # Fallback to the first available key
    return next(iter(candidates.keys()), None)

def municode_article_url(article_num: str) -> Dict[str, Optional[str]]:
    """
    Return the most useful links we can provide for a given article number.
    Always returns a 'tables' link, and a 'main' link when known.
    """
    tables_url = f"https://library.municode.com/ma/boston/codes/redevelopment_authority?nodeId=ART{article_num}TA"
    main_url = ARTICLE_MAIN.get(article_num)
    return {"main": main_url, "tables": tables_url}

def get_municode_article_from_coords(lat: float, lon: float) -> Dict:
    """
    Given WGS84 coordinates, return the applicable Zoning Article number and useful Municode links.
    """
    # 1) Try subdistricts (has rich fields incl. Article)
    sub_feats = _arcgis_point_query(
        BPDA_SUBDISTRICTS,
        lat, lon,
        out_fields="Article,Zoning_Subdistrict,Zoning_District,Urban_Name,Map_Number,Municode_Reference_to_Restricti"
    )

    candidates = {}
    context = {}
    if sub_feats:
        for f in sub_feats:
            attrs = f.get("attributes", {}) or {}
            art = _first_numeric(str(attrs.get("Article", "")))
            if not art:
                continue
            # Keep one representative per article
            if art not in candidates:
                candidates[art] = attrs
        best = _pick_best_article(candidates)
        if best:
            context = candidates[best]
            urls = municode_article_url(best)
            return {
                "input": {"lat": lat, "lon": lon},
                "article": best,
                "context": {
                    "zoning_district": context.get("Zoning_District"),
                    "zoning_subdistrict": context.get("Zoning_Subdistrict"),
                    "urban_name": context.get("Urban_Name"),
                    "map_number": context.get("Map_Number"),
                    "note": context.get("Municode_Reference_to_Restricti"),
                },
                "municode": urls,
            }

    # 2) Fallback to district layer (also has ARTICLE)
    dist_feats = _arcgis_point_query(
        BPDA_DISTRICTS,
        lat, lon,
        out_fields="ARTICLE,DISTRICT,MAPNO"
    )

    if dist_feats:
        # Usually only one
        attrs = (dist_feats[0].get("attributes") or {})
        art = _first_numeric(str(attrs.get("ARTICLE", "")))
        if art:
            urls = municode_article_url(art)
            return {
                "input": {"lat": lat, "lon": lon},
                "article": art,
                "context": {
                    "zoning_district": attrs.get("DISTRICT"),
                    "map_number": attrs.get("MAPNO"),
                },
                "municode": urls,
            }

    # 3) Outside Boston or no zoning polygon found
    return {
        "input": {"lat": lat, "lon": lon},
        "article": None,
        "error": "No Boston zoning polygon found at this location."
    }

if __name__ == "__main__":
    # Example: Allston (approx.)
    result = get_municode_article_from_coords(42.3539, -71.1337)
    print(json.dumps(result, indent=2))
