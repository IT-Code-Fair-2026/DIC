# data/external/services/ — essential-services point layers

Schools, health clinics, hospitals and police stations for the Northern Territory, used by
`src/05_load_services.py` to answer "how far is the nearest school / clinic / hospital /
police station from each community?".

The pulls below were downloaded on **2026-09-04**. Raw responses are kept in `_raw/` exactly
as returned. `src/05_load_services.py` reads `_raw/` and writes the tidy combined table to
`data/processed/05_services.csv` — it does not write here.

To re-fetch, re-run the four commands below (each is a plain HTTP GET, no key needed).

---

## 1. Police stations — Geoscience Australia

`_raw/ga_police_nt.geojson` — 66 features.

Layer: **Emergency Management Facilities → `POLICING_FACILITY` (layer 2)**, National Location
Information / Geoscience Australia. Point per police station / shopfront.
Licence: © Commonwealth of Australia (Geoscience Australia) 2024 — CC BY 4.0.
Fields used: `facility_name`, `facility_operationalstatus`, `facility_address`, `abs_suburb`;
coordinates from the GeoJSON geometry.

```
curl -s "https://services.ga.gov.au/gis/rest/services/Emergency_Management_Facilities/MapServer/2/query?where=facility_state%3D%27NORTHERN%20TERRITORY%27&outFields=*&returnGeometry=true&outSR=4326&f=geojson" -o data/external/services/_raw/ga_police_nt.geojson
```

## 2. Hospitals — Geoscience Australia / National Health Services Directory

`_raw/ga_hospitals_nt.geojson` — 11 features → **8** after cleaning in `05_load_services.py`.

Layer: **National HealthDirect Health Facilities → `HOSPITAL` (layer 1)**, sourced from the
National Health Services Directory (NHSD).
Licence: © Commonwealth of Australia (Geoscience Australia) 2024 — CC BY 4.0.
Fields used: `organisation_name`, `address`, `suburb`, `operationalstatus`; coordinates from geometry.
Cleaning in `05_load_services.py`:
- NHSD lists Alice Springs and Katherine hospitals twice (an "Emergency Department" row and a
  "General Medical Clinic" row at the same site) → keep one per site, preferring the ED row.
- one row, "Tkc Production" (Darwin City), is a placeholder org name at a building-under-
  construction address → dropped.
- `is_public` = `False` only where the name contains "Private" (Darwin Private Hospital).
Result: 8 hospitals — Royal Darwin, Alice Springs, Katherine, Tennant Creek, Palmerston
Regional, Gove District, Imanpa Community Health Centre, Darwin Private.

```
curl -s "https://services.ga.gov.au/gis/rest/services/National_HealthDirect_Health_Facilities/MapServer/1/query?where=state%3D%27NT%27&outFields=*&returnGeometry=true&outSR=4326&f=geojson" -o data/external/services/_raw/ga_hospitals_nt.geojson
```

## 3. Health clinics / general practices — Geoscience Australia / NHSD

`_raw/ga_gp_nt.geojson` — 128 features.

Layer: **National HealthDirect Health Facilities → `GENERAL_PRACTICE` (layer 0)**.
Licence: © Commonwealth of Australia (Geoscience Australia) 2024 — CC BY 4.0.
This layer includes the remote Aboriginal Community Controlled and NT Health community health
centres as well as urban GP practices. A spot-check (2026-09-04) found a health centre within
5 km of Maningrida (0.3 km), Wadeye (0.2), Galiwin'ku (0.4), Yuendumu (3.6), Ngukurr (0.2)
and Borroloola (1.4), so no OpenStreetMap merge was needed. Urban GPs are **not** filtered
out (per instruction) — the `service_type` is `health_clinic` for all of them.

```
curl -s "https://services.ga.gov.au/gis/rest/services/National_HealthDirect_Health_Facilities/MapServer/0/query?where=state%3D%27NT%27&outFields=*&returnGeometry=true&outSR=4326&f=geojson" -o data/external/services/_raw/ga_gp_nt.geojson
```

## 4. Schools — ACARA Australian Schools List (official)

`../../raw/school_data.xlsx` — 217 rows (one sheet, `ASL Search Results`).

From **`https://asl.acara.edu.au/`** (ACARA's Australian Schools List): run a search filtered to
State = NT, then "Download search results as" Excel. The export has a title banner on row 1 and
the real header on row 2. Columns: `ACARA ID, School Name, Suburb, State, Postcode, Type,
Sector, Status, Geolocation, Parent School ID, AGE ID, Latitude, Longitude, StateProvinceID`.
All 217 rows are Status = Open, all have Latitude/Longitude. Sector = Gov (150) / Non-Gov (67)
→ `is_public`. 22 rows are named campuses of a multi-campus college, each with its own point;
all kept.

Downloaded **2026-09-04**. Licence: © ACARA — the ASL is published under Creative Commons
Attribution (CC BY 4.0).

`05_load_services.py` reads it straight through (`header=1`), no cleaning needed.

> An earlier OpenStreetMap Overpass pull (`amenity=school`, NT → 208 schools after dedupe) was
> used only as a cross-check and then discarded once the ACARA file was available; the two
> agree closely (OSM 208 vs ACARA 217) and every remote community has its school within ~1 km
> in the ACARA data.
