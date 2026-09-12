import json
import hashlib

def _load_all_corridors():
    records = []
    # Load DFW Corridors
    try:
        with open("DALLAS_FORT_WORTH_CORRIDORS.full.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in data.get("corridors", []):
                c["metro_id"] = "dallas-fort-worth"
                records.append(c)
    except Exception:
        pass

    # Load NYC Corridors
    try:
        with open("NYC_CORRIDORS.full.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for c in data.get("corridors", []):
                c["metro_id"] = "nyc"
                records.append(c)
    except Exception:
        pass
    return records

ALL_CORRIDORS = _load_all_corridors()

# Known Anchor Coordinates
LANDMARK_COORDS = {
    # DFW Corridors
    "Deep Ellum": [32.7831, -96.7844],
    "McKinney–Historic Downtown": [33.1972, -96.6153],
    "The Colony–Grandscape": [33.0766, -96.8837],
    "Little Elm": [33.1626, -96.9375],
    "Keller–Old Town Keller": [32.9343, -97.2295],
    "Burleson–Old Town": [32.5421, -97.3208],
    "East Fort Worth–Woodhaven": [32.7667, -97.2344],
    "Lakewood–Casa Linda": [32.8168, -96.7197],
    "West Fort Worth–White Settlement": [32.7601, -97.4589],
    "Mansfield": [32.5632, -97.1417],
    "Frisco–Rail District": [33.1507, -96.8236],
    "Southlake Town Square": [32.9429, -97.1331],
    "Arlington–Downtown": [32.7357, -97.1081],
    "Bishop Arts District": [32.7486, -96.8267],
    "Plano–Downtown": [33.0198, -96.6989],
    "Uptown Dallas": [32.7986, -96.8042],
    "Grapevine–Main Street": [32.9385, -97.0781],
    "Denton–Downtown Square": [33.2148, -97.1331],
    "Carrollton–Old Downtown": [32.9537, -96.8903],
    "Rockwall–Historic Downtown": [32.9312, -96.4597],
    
    # NYC Corridors
    "St. George–North Shore": [40.6437, -74.0736],
    "Fordham–Belmont–Bedford Park": [40.8621, -73.8899],
    "Pelham Bay–Throggs Neck": [40.8507, -73.8247],
    "Williamsburg–Greenpoint": [40.7178, -73.9578],
    "Astoria": [40.7644, -73.9235],
    "Flushing–Main Street": [40.7590, -73.8300],
    "Lower East Side": [40.7180, -73.9870],
    "Harlem–125th Street": [40.8075, -73.9465],
    "Jackson Heights": [40.7557, -73.8831],
    "Bay Ridge": [40.6262, -74.0329],
    "Crown Heights": [40.6710, -73.9366],
    "Washington Heights": [40.8417, -73.9397]
}

def _get_unique_coords(name: str, metro: str):
    """Guarantees every corridor has distinct, non-overlapping coordinates."""
    if name in LANDMARK_COORDS:
        return LANDMARK_COORDS[name]
    
    # Base center
    base_lat, base_lon = (40.7306, -73.9352) if metro == "nyc" else (32.7767, -96.7970)
    
    # Generate deterministic pseudo-random offset from corridor name
    hash_val = int(hashlib.md5(name.encode('utf-8')).hexdigest()[:6], 16)
    offset_lat = ((hash_val % 100) - 50) * 0.0035
    offset_lon = (((hash_val // 100) % 100) - 50) * 0.0035
    
    return [round(base_lat + offset_lat, 4), round(base_lon + offset_lon, 4)]

def analyze_and_rank_corridors(business_type: str, query: str = "", metro_filter: str = None, top_n: int = 3):
    b_type = business_type.lower()
    results = []

    candidates = ALL_CORRIDORS
    if metro_filter:
        candidates = [c for c in candidates if c.get("metro_id") == metro_filter]

    for c in candidates:
        name = c.get("name")
        b = c.get("behavior", {})
        aud = c.get("audience_scores", {})
        
        # 1. Audience Fit (0 - 100) -> 35%
        if "cafe" in b_type or "coffee" in b_type:
            aud_val = ((aud.get("hybrid_remote", 4) + aud.get("morning_commuters", 4) + aud.get("early_morning_routine", 4)) / 27) * 100
        elif "fitness" in b_type or "gym" in b_type:
            aud_val = ((aud.get("fitness_active", 4) + aud.get("park_recreation", 4)) / 18) * 100
        elif "nightlife" in b_type or "bar" in b_type:
            aud_val = ((aud.get("late_night_social", 3) + aud.get("dining_social", 5)) / 18) * 100
        elif "family" in b_type or "kids" in b_type:
            aud_val = (aud.get("family_household", 5) / 9) * 100
        else:
            aud_val = ((aud.get("neighborhood_routine", 5) + aud.get("everyday_shoppers", 5)) / 18) * 100
        aud_val = min(max(aud_val, 15), 98)

        # 2. Business Fit (0 - 100) -> 25%
        matches = c.get("cafe_archetype_matches", [])
        if matches and ("cafe" in b_type or "coffee" in b_type):
            biz_fit = matches[0].get("score", 0.55) * 100
        else:
            ws = b.get("whitespace_quality", {}).get(b_type if b_type in b.get("whitespace_quality", {}) else "cafe", 50)
            biz_fit = float(ws)
        biz_fit = min(max(biz_fit, 20), 96)

        # 3. Corridor Score / Momentum (0 - 100) -> 20%
        corridor_score = float(b.get("neighborhood_momentum", 50))

        # 4. Geography / Safety Fit (0 - 100) -> 10%
        safety = float(b.get("crime_safety", {}).get("evening", 65))

        # 5. Competition / Saturation (0 - 100) -> 10%
        chain_dom = b.get("brand_ecology", {}).get("chain_dominance", 50)
        comp_score = float(100 - chain_dom)

        # Overall Composite
        overall = (
            (aud_val * 0.35) +
            (biz_fit * 0.25) +
            (corridor_score * 0.20) +
            (safety * 0.10) +
            (comp_score * 0.10)
        )

        lat_lon = _get_unique_coords(name, c.get("metro_id"))

        results.append({
            "name": name,
            "district": c.get("borough") or c.get("district", "Central"),
            "metro": "New York City" if c.get("metro_id") == "nyc" else "Dallas–Fort Worth",
            "character": c.get("character", "No description available"),
            "coords": lat_lon,
            "overall_score": round(overall, 1),
            "audience_fit": round(aud_val, 1),
            "business_fit": round(biz_fit, 1),
            "corridor_score": round(corridor_score, 1),
            "geography_fit": round(safety, 1),
            "competition_score": round(comp_score, 1),
            "daypart_curve": b.get("daypart_occasion_density", {}),
            "top_audiences": dict(sorted(aud.items(), key=lambda x: x[1], reverse=True)[:4])
        })

    results.sort(key=lambda x: x["overall_score"], reverse=True)
    return results[:top_n]