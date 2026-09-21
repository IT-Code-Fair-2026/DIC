"""
Trim the three data-main datasets to the columns actually needed to plug into
DIC-main's pipeline, following the exact pattern notebooks/05_program_sites.ipynb
already uses for mbsp/guide/rict: common identity+location columns, plus a
small set of source-prefixed columns, everything else (constant columns, dead
GNAF-match scaffolding, contact details not used downstream) dropped per the
issues already logged in each *_findings.md.
"""
import csv

BASE = "/tmp/claude-0/-home-claude/46f3b0b2-161d-5267-a238-2dfa4cc408b8/scratchpad/work"
OUT = f"{BASE}/out"

def zero_pad_postcode(v):
    v = (v or "").strip()
    if not v:
        return None
    try:
        return f"{int(float(v)):04d}"
    except ValueError:
        return v

# ---------- medical_facilities_NT.csv -> medical_services.csv ----------
med_rows = []
with open(f"{BASE}/data-main/data-main/medical_facilities_NT.csv", encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        med_rows.append({
            "source": "medical",
            "name": row["ORGANISATION_NAME"].strip(),
            "latitude": row["LATITUDE"],
            "longitude": row["LONGITUDE"],
            "medical_class": row["GA_CLASS"],
            "medical_service_type": row["NHSD_SERVICE_TYPE"],
            "medical_suburb": row["SUBURB"],
            "medical_postcode": zero_pad_postcode(row["POSTCODE"]),
        })
with open(f"{OUT}/medical_services.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(med_rows[0].keys()))
    w.writeheader(); w.writerows(med_rows)
print(f"medical_services.csv: {len(med_rows)} rows")

# ---------- emergency_facilities_NORTHERN_TERRITORY.csv -> emergency_services.csv ----------
AGENCY_MAP = {
    "NT FIRE AND RESCUE": "NT Fire and Rescue",
    "NORTHERN TERRITORY POLICE, FIR": "NT Police, Fire and Emergency Services",
    "AUSTRALIAN FEDERAL POLICE": "Australian Federal Police",
}
em_rows = []
with open(f"{BASE}/data-main/data-main/emergency_facilities_NORTHERN_TERRITORY.csv", encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        if not row["FACILITY_LAT"] or not row["FACILITY_LONG"]:
            continue
        src = row["FACILITY_SOURCE"].strip()
        em_rows.append({
            "source": "emergency",
            "name": row["FACILITY_NAME"].strip(),
            "latitude": row["FACILITY_LAT"],
            "longitude": row["FACILITY_LONG"],
            "emergency_class": row["CLASS"].strip().title(),
            "emergency_agency": AGENCY_MAP.get(src, src),
            "emergency_suburb": row["ABS_SUBURB"].strip().title(),
            "emergency_postcode": zero_pad_postcode(row["ABS_POSTCODE"]),
        })
with open(f"{OUT}/emergency_services.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(em_rows[0].keys()))
    w.writeheader(); w.writerows(em_rows)
print(f"emergency_services.csv: {len(em_rows)} rows")

# ---------- combine schools (already geocoded) + medical + emergency into one
#     DIC-main-shaped "services_sites.csv", mirroring program_sites.csv exactly ----------
import csv as _csv
with open(f"{OUT}/schools_services.csv", encoding="utf-8") as fh:
    school_rows = list(_csv.DictReader(fh))

def slugify(text):
    import re
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")

combined = []
for i, r in enumerate(school_rows):
    combined.append({
        "service_site_id": f"school-{slugify(r['name'])}-{i}",
        "source": "school", "name": r["name"],
        "latitude": r["latitude"] or None, "longitude": r["longitude"] or None,
        "geocode_method": r["school_geocode_method"],
        "type": "; ".join(t for t, flag in [
            ("Pre School", r["school_is_preschool"]), ("Primary", r["school_is_primary"]),
            ("Middle", r["school_is_middle"]), ("Senior", r["school_is_senior"]),
        ] if flag == "True") or None,
        "sector_or_agency": r["school_sector"] or None,
        "region_or_class": r["school_region"] or None,
    })
for i, r in enumerate(med_rows):
    combined.append({
        "service_site_id": f"medical-{i}",
        "source": "medical", "name": r["name"],
        "latitude": r["latitude"], "longitude": r["longitude"],
        "geocode_method": "source_supplied",
        "type": r["medical_service_type"],
        "sector_or_agency": None,
        "region_or_class": r["medical_class"],
    })
for i, r in enumerate(em_rows):
    combined.append({
        "service_site_id": f"emergency-{i}",
        "source": "emergency", "name": r["name"],
        "latitude": r["latitude"], "longitude": r["longitude"],
        "geocode_method": "source_supplied",
        "type": r["emergency_class"],
        "sector_or_agency": r["emergency_agency"],
        "region_or_class": r["emergency_class"],
    })

with open(f"{OUT}/services_sites.csv", "w", newline="", encoding="utf-8") as fh:
    w = _csv.DictWriter(fh, fieldnames=list(combined[0].keys()))
    w.writeheader(); w.writerows(combined)
print(f"services_sites.csv (combined): {len(combined)} rows "
      f"({sum(1 for r in combined if r['source']=='school')} school, "
      f"{sum(1 for r in combined if r['source']=='medical')} medical, "
      f"{sum(1 for r in combined if r['source']=='emergency')} emergency)")
n_geo = sum(1 for r in combined if r["latitude"])
print(f"rows with coordinates: {n_geo}/{len(combined)}")
