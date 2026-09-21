"""
Offline locality-level geocoder for the NT school list.

Why offline: this sandbox's network egress policy blocks every public geocoding
API (Nominatim, Photon, Geoapify, etc. all rejected the CONNECT at the proxy).
So instead of street-address precision, this matches each school's suburb/locality
name against three gazetteers already sitting in this project (all real lat/long,
no network calls):

  1. medical_facilities_NT.csv   SUBURB -> mean(LATITUDE, LONGITUDE)   (your own data)
  2. emergency_facilities_...csv ABS_SUBURB -> mean(FACILITY_LAT/LONG) (your own data)
  3. BushTel Com_BushTel_Profile_CMC_2024.json community_name/aliases -> lat/long
     (792 NT communities incl. Darwin/Alice Springs/Katherine/Nhulunbuy/Palmerston/
     Tennant Creek/Alyangula/Yulara as single "Town"/"City" points)

This gives locality/suburb-centre precision, not street precision -- consistent
with the project's own rule that distance work here is triage, not a coverage
claim (see PROJECT_CONTEXT.md rule 5). Every row is tagged with how it was
matched so nothing is silently guessed.
"""
import csv
import json
import re
import difflib
from collections import defaultdict

BASE = "/tmp/claude-0/-home-claude/46f3b0b2-161d-5267-a238-2dfa4cc408b8/scratchpad/work"
SCHOOLS_CSV = f"{BASE}/data-main/data-main/School_List_Public_2026_09_12_11_12_43.csv"
MEDICAL_CSV = f"{BASE}/data-main/data-main/medical_facilities_NT.csv"
EMERGENCY_CSV = f"{BASE}/data-main/data-main/emergency_facilities_NORTHERN_TERRITORY.csv"
BUSHTEL_JSON = f"{BASE}/DIC-main/DIC-main/data/raw/bushtel/Com_BushTel_Profile_CMC_2024.json"
OUT_CSV = f"{BASE}/out/schools_services.csv"

def norm(name):
    """Normalise a locality name for matching: upper, strip, collapse whitespace,
    drop a trailing state/'City' qualifier some sources add."""
    if not name:
        return ""
    n = re.sub(r"\s+", " ", str(name).strip().upper())
    n = re.sub(r"\s*\(NT\)$", "", n)
    return n

# --- 1. Build the gazetteer: normalized locality name -> (lat, lon, source) ---
gaz = {}          # exact-name lookup, first-source-wins priority order below
gaz_names = []     # for fuzzy matching

def add_gaz(name, lat, lon, source, overwrite=False):
    key = norm(name)
    if not key or lat is None or lon is None:
        return
    if key not in gaz or overwrite:
        gaz[key] = (float(lat), float(lon), source)

# 1a. medical_facilities_NT.csv -> suburb centroid (mean of its facility points)
med_sub = defaultdict(list)
with open(MEDICAL_CSV, encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        med_sub[norm(row["SUBURB"])].append((float(row["LATITUDE"]), float(row["LONGITUDE"])))
for name, pts in med_sub.items():
    lat = sum(p[0] for p in pts) / len(pts)
    lon = sum(p[1] for p in pts) / len(pts)
    add_gaz(name, lat, lon, "medical_suburb")

# 1b. emergency_facilities -> suburb centroid
em_sub = defaultdict(list)
with open(EMERGENCY_CSV, encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        try:
            em_sub[norm(row["ABS_SUBURB"])].append((float(row["FACILITY_LAT"]), float(row["FACILITY_LONG"])))
        except (ValueError, KeyError):
            continue
for name, pts in em_sub.items():
    lat = sum(p[0] for p in pts) / len(pts)
    lon = sum(p[1] for p in pts) / len(pts)
    add_gaz(name, lat, lon, "emergency_suburb")

# 1c. BushTel communities + aliases (only fill gaps left by the two local sources,
#     since BushTel is a single point per community, not a suburb centroid)
with open(BUSHTEL_JSON, encoding="utf-8") as fh:
    bt = json.load(fh)
for feat in bt["features"]:
    p = feat["properties"]
    add_gaz(p["community_name"], p["latitude"], p["longitude"], "bushtel")
    aliases = p.get("community_aliases") or ""
    if aliases and "no aliases" not in aliases.lower():
        for alias in re.split(r"[;,]", aliases):
            add_gaz(alias, p["latitude"], p["longitude"], "bushtel_alias")

gaz_names = list(gaz.keys())
print(f"gazetteer size: {len(gaz)} distinct localities "
      f"(medical {sum(v[2]=='medical_suburb' for v in gaz.values())}, "
      f"emergency {sum(v[2]=='emergency_suburb' for v in gaz.values())}, "
      f"bushtel {sum(v[2] in ('bushtel','bushtel_alias') for v in gaz.values())})")

# --- 2. Extract a locality name (and an alt-name candidate) from each school's
#     Physical Address. Handles three messy patterns seen in this file:
#       "80 Spearwood Rd, Alice Springs, 0870, NT"   (clean, comma-separated)
#       "N/A, Amoonguna, NT"                          (no street, no postcode)
#       "Wurrumiyanga NT 0822"                        (no commas at all)
#       "Santa Teresa (Ltyenty Apurte)"                (official name + alt name)
POSTCODE_RE = re.compile(r"^\d{3,4}$")
TRAILING_STATE_POSTCODE_RE = re.compile(r"\s+NT\s*\d{0,4}\s*$", re.IGNORECASE)
PAREN_RE = re.compile(r"^(.*?)\s*\(([^)]+)\)\s*$")

def extract_locality(address):
    """Returns (primary_locality, alt_locality_or_None)."""
    if not address or address.strip().upper() in ("", "N/A", "TBA"):
        return None, None
    addr = TRAILING_STATE_POSTCODE_RE.sub("", address.strip())
    parts = [p.strip() for p in addr.split(",") if p.strip()]
    if not parts:
        return None, None
    if parts and parts[-1].upper() in ("NT", "N.T.", "NORTHERN TERRITORY"):
        parts = parts[:-1]
    if parts and POSTCODE_RE.match(parts[-1]):
        parts = parts[:-1]
    if not parts:
        return None, None
    locality = TRAILING_STATE_POSTCODE_RE.sub("", parts[-1]).strip()
    m = PAREN_RE.match(locality)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return locality, None

# --- 2b. Manual overrides: suburbs with no facility in the medical/emergency
#     files and no BushTel entry (these are Darwin-rural/Palmerston suburbs,
#     not remote communities). Looked up one at a time via WebSearch/WebFetch
#     against Wikipedia infoboxes and findlatitudeandlongitude.com -- each is a
#     real, checkable public source, not a guess. Cross-checked against the NT
#     bounding box before being trusted.
MANUAL_OVERRIDES = {
    # suburb           lat          lon         source
    "DRIVER":        (-12.485085, 130.973005, "wikipedia:Driver,_Northern_Territory"),
    "GIRRAWEEN":     (-12.524085, 131.092505, "wikipedia:Girraween,_Northern_Territory"),
    "GRAY":          (-12.492205, 130.978915, "wikipedia:Gray,_Northern_Territory"),
    "MOULDEN":       (-12.510000, 130.976000, "wikipedia:Moulden,_Northern_Territory"),
    "JOHNSTON":      (-12.486400, 131.009600, "wikipedia:Johnston,_Northern_Territory"),
    "DUNDEE BEACH":  (-12.733400, 130.383100, "wikipedia:Dundee_Beach,_Northern_Territory"),
    "MIDDLE POINT":  (-12.599000, 131.326100, "wikipedia:Middle_Point,_Northern_Territory"),
    "BELLAMACK":     (-12.521100, 130.980200, "latitude.to:Bellamack"),
    "TIPPERARY":     (-13.729839, 131.040459, "findlatitudeandlongitude.com:Tipperary_Station"),
    # Still unresolved after a web check -- left unmatched rather than guessed:
    # Freds Pass, Marlow Lagoon, Pickertaramoor Melville Island, Litchfield Park.
}

# --- 3. Match each school to a coordinate ---
# Tier 3 fallback: NT DoE region -> that region's own town/regional-centre point
# (from the BushTel Town/City list). This is deliberately coarse -- flagged as
# "region_fallback" and never presented as suburb-level precision.
REGION_FALLBACK = {
    "DARWIN": "DARWIN", "PALMERSTON": "PALMERSTON",
    "CENTRAL": "ALICE SPRINGS", "BIG RIVERS": "KATHERINE",
    "EAST ARNHEM": "NHULUNBUY", "BARKLY": "TENNANT CREEK",
    "WEST ARNHEM": "JABIRU",
    # "TOP END" has no single town of its own in the region list; left unmapped
    # on purpose rather than guessing one.
}

def match(locality, alt_locality, region):
    for candidate, tag in ((locality, "primary"), (alt_locality, "alt")):
        if not candidate:
            continue
        key = norm(candidate)
        if key in gaz:
            lat, lon, src = gaz[key]
            return lat, lon, f"exact:{src}:{tag}"
        if key in MANUAL_OVERRIDES:
            lat, lon, src = MANUAL_OVERRIDES[key]
            return lat, lon, f"manual:{src}"
    # Fuzzy matching against the full gazetteer was tried and DROPPED: short NT
    # place names (e.g. "Alawa", "Anula", "Nakara" -- real Darwin suburbs) kept
    # matching remote BushTel community aliases that merely share letters
    # ("NALAWAN", "YANULA", "NTAKARRA") but sit hundreds of km away. A wrong
    # coordinate is worse than an honest "unmatched", so this tier only trusts
    # exact locality-name matches and the coarse region fallback below.
    region_town = REGION_FALLBACK.get(norm(region))
    if region_town and region_town in gaz:
        lat, lon, src = gaz[region_town]
        return lat, lon, f"region_fallback:{region}->{region_town}"
    return None, None, "unmatched"

rows_out = []
stats = defaultdict(int)
with open(SCHOOLS_CSV, encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        locality, alt_locality = extract_locality(row["Physical Address"])
        lat, lon, how = match(locality, alt_locality, row["Region"])
        stats[how.split(":")[0]] += 1
        rows_out.append({
            "source": "school",
            "name": row["Name"].strip(),
            "latitude": lat,
            "longitude": lon,
            "school_locality": locality,
            "school_geocode_method": how,
            "school_region": row["Region"].strip(),
            "school_sector": row["Sector"].strip() or None,
            "school_remoteness": row["NTG Remote Definition"].strip() or None,
            "school_is_preschool": row["Is Pre School"].strip() == "Yes",
            "school_is_primary": row["Is Primary School"].strip() == "Yes",
            "school_is_middle": row["Is Middle School"].strip() == "Yes",
            "school_is_senior": row["Is Senior School"].strip() == "Yes",
            "school_is_faft": row["Is FAFT School"].strip() == "Yes",
        })

print("\nmatch method breakdown:", dict(stats))
n = len(rows_out)
n_matched = sum(1 for r in rows_out if r["latitude"] is not None)
print(f"geocoded {n_matched}/{n} schools ({n_matched/n:.1%})")

fieldnames = list(rows_out[0].keys())
with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows_out)
print(f"wrote {OUT_CSV}")

print("\nunmatched schools (need a manual check / real geocoder later):")
for r in rows_out:
    if r["latitude"] is None:
        print(" -", r["name"], "|", r["school_locality"])
