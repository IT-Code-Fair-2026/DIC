"""
Build small_cells.csv (25 rows) from the NT mobile coverage guide.

Source: data/raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx
("Remote Sites with Mobile Phone Small Cell Coverage"). The companion file
mobile-coverage-all-sites.xlsx explains the ranges the app draws around a tower:

    "macro cell (up to 40 km coverage), small cell (up to 5 km coverage) ...
     Coverage varies according to local conditions especially topography and
     vegetation and this list is a GUIDE only."

Uses only the standard library + pandas (an .xlsx is a zip of XML), so it needs
no extra dependency. Run from the repo root:

    python Saugat/services/build_small_cells.py
"""
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pandas as pd

SRC = Path("data/raw/nt_mobile_coverage/remote-small-cell-coverage-nt.xlsx")
OUT = Path("Saugat/app/small_cells.csv")
NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_rows(path: Path) -> list[list[str]]:
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = ["".join(si.itertext()) for si in root.findall("a:si", NS)]
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.findall(".//a:row", NS):
        vals = []
        for c in row.findall("a:c", NS):
            v = c.find("a:v", NS)
            vals.append("" if v is None else shared[int(v.text)] if c.get("t") == "s" else v.text)
        rows.append(vals)
    return rows


def main() -> None:
    rows = read_rows(SRC)
    header_at = next(i for i, r in enumerate(rows) if r and r[0].startswith("Location of Small Cell"))
    body = [r for r in rows[header_at + 1:] if len(r) >= 4 and r[1]]
    df = pd.DataFrame(body, columns=["name", "latitude", "longitude", "provider"]).astype(
        {"latitude": float, "longitude": float}
    )
    df.to_csv(OUT, index=False)
    print(f"wrote {OUT} ({len(df)} rows)")


if __name__ == "__main__":
    main()
