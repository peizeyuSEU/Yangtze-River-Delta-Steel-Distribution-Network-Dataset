"""Recover public-source metadata from the calibration workbook.

This script only updates provenance metadata. It never writes processed inputs.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import openpyxl

FIELDS = [
    "source_record_id", "entity_id", "city", "variable_name", "recovered_value",
    "recovered_unit", "source_url", "source_title", "publisher_or_platform",
    "observation_date", "source_quality", "observation_type", "proxy_flag",
    "original_workbook", "original_sheet", "original_row", "workbook_sha256",
    "recovery_status", "verification_status", "notes",
]

def rows(ws, header_row):
    vals = list(ws.iter_rows(values_only=True))
    headers = [str(x).strip() if x is not None else "" for x in vals[header_row - 1]]
    for no, values in enumerate(vals[header_row:], header_row + 1):
        if not values or values[0] in (None, ""):
            continue
        yield no, dict(zip(headers, values))

def s(value):
    return "" if value is None else str(value)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workbook", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    wb_path = args.workbook.resolve()
    digest = hashlib.sha256(wb_path.read_bytes()).hexdigest().upper()
    wb_name = wb_path.name
    wb = openpyxl.load_workbook(wb_path, data_only=True, read_only=True)
    out = []

    for rowno, r in rows(wb["Nodes"], 1):
        nid, city = s(r.get("Node ID")), s(r.get("City"))
        out.append({"source_record_id": f"NODE_{nid}", "entity_id": nid, "city": city,
            "variable_name": "coordinates", "recovered_value": f"{r.get('Latitude')};{r.get('Longitude')}",
            "recovered_unit": "lat;lon", "source_url": s(r.get("Coordinate source")),
            "source_title": "GeoNames gazetteer", "publisher_or_platform": "GeoNames",
            "observation_date": "2024/2026", "source_quality": s(r.get("Coordinate status")),
            "observation_type": "city-centre coordinate", "proxy_flag": "true",
            "original_workbook": wb_name, "original_sheet": "Nodes", "original_row": rowno,
            "workbook_sha256": digest, "recovery_status": "recovered",
            "verification_status": "verified_metadata_only",
            "notes": "City-centre coordinate; not an enterprise or warehouse address."})

    for rowno, r in rows(wb["Market_Proxy"], 1):
        mid, city = s(r.get("Market ID")), s(r.get("City"))
        out.append({"source_record_id": f"STAT_{mid}", "entity_id": mid, "city": city,
            "variable_name": "second_industry_va_2024_100m_cny", "recovered_value": s(r.get("2024 second-industry value added\n(100m CNY)")),
            "recovered_unit": "100m CNY", "source_url": s(r.get("Source URL")),
            "source_title": "Municipal/provincial statistical bulletin", "publisher_or_platform": s(r.get("Source quality")),
            "observation_date": "2024", "source_quality": s(r.get("Source quality")),
            "observation_type": "statistical proxy", "proxy_flag": "true",
            "original_workbook": wb_name, "original_sheet": "Market_Proxy", "original_row": rowno,
            "workbook_sha256": digest, "recovery_status": "recovered",
            "verification_status": "pending_manual_review", "notes": "Demand weights and demand fields are derived in the pipeline."})

    for rowno, r in rows(wb["Steel_Prices_Observed"], 4):
        mid, city = s(r.get("Market ID")), s(r.get("City"))
        proxy = "true" if "proxy" in s(r.get("Observation type")).lower() or mid == "M15" else "false"
        note = s(r.get("Notes"))
        if mid == "M15":
            note += " Parent observations: PRICE_C05, PRICE_C08, PRICE_M12."
        out.append({"source_record_id": f"PRICE_{mid}", "entity_id": mid, "city": city,
            "variable_name": "observed_price_cny_per_tonne", "recovered_value": s(r.get("Selected screening price\n(CNY/t)")),
            "recovered_unit": "CNY/t", "source_url": s(r.get("Source URL")),
            "source_title": "Steel market quotation", "publisher_or_platform": "Mysteel / ChinaGold / SteelX2",
            "observation_date": s(r.get("Observation date")), "source_quality": s(r.get("Data quality")),
            "observation_type": s(r.get("Observation type")), "proxy_flag": proxy,
            "original_workbook": wb_name, "original_sheet": "Steel_Prices_Observed", "original_row": rowno,
            "workbook_sha256": digest, "recovery_status": "recovered",
            "verification_status": "verified_page_but_value_unavailable" if mid == "M15" else "pending_manual_review",
            "notes": note})

    for rowno, r in rows(wb["Warehouse_Rents_Observed"], 4):
        did, city = s(r.get("DC ID")), s(r.get("City"))
        out.append({"source_record_id": f"RENT_{did}", "entity_id": did, "city": city,
            "variable_name": "warehouse_rent_cny_per_sqm_month", "recovered_value": s(r.get("Monthly rent\n(CNY/m²/month)")),
            "recovered_unit": "CNY/m²/month", "source_url": s(r.get("Source URL")),
            "source_title": "Warehouse market rent observation", "publisher_or_platform": "CBRE / 58.com",
            "observation_date": s(r.get("Observation period")), "source_quality": s(r.get("Data quality")),
            "observation_type": s(r.get("Observation type")), "proxy_flag": "true",
            "original_workbook": wb_name, "original_sheet": "Warehouse_Rents_Observed", "original_row": rowno,
            "workbook_sha256": digest, "recovery_status": "recovered",
            "verification_status": "pending_manual_review",
            "notes": s(r.get("Notes"))})

    out_dir = args.repo_root / "metadata"
    out_dir.mkdir(exist_ok=True)
    with (out_dir / "source_recovery_register.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)
    # Enrich existing source records without changing IDs or normalized values.
    sr_path = args.repo_root / "data" / "source_records" / "source_records.csv"
    if sr_path.exists():
        with sr_path.open(encoding="utf-8-sig", newline="") as f: sr = list(csv.DictReader(f))
        by_id = {x["source_record_id"]: x for x in out}
        for r in sr:
            x = by_id.get(r["source_record_id"])
            if not x: continue
            r["source_url"] = x["source_url"]
            r["observation_date"] = x["observation_date"]
            r["proxy_flag"] = x["proxy_flag"]
            r["notes"] = (r.get("notes", "").strip().strip('"') + " " + x["notes"]).strip()
        with sr_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=sr[0].keys()); w.writeheader(); w.writerows(sr)
    # Keep source_catalog category-level and add an explicit register pointer.
    cat_path = out_dir / "source_catalog.csv"
    with cat_path.open(encoding="utf-8-sig", newline="") as f: cat = list(csv.DictReader(f))
    for r in cat:
        if r["source_id"] == "SRC_NODE_RECORDS":
            r["source_url"] = "https://www.geonames.org/"
            r["notes"] = "Record-level URLs and workbook provenance: metadata/source_recovery_register.csv; city-centre coordinates."
        elif r["source_id"] == "SRC_STAT_RECORDS":
            r["notes"] = "Record-level municipal/provincial URLs recovered in metadata/source_recovery_register.csv."
        elif r["source_id"] == "SRC_PRICE_RECORDS":
            r["notes"] = "Record-level quotation URLs recovered in metadata/source_recovery_register.csv; M15 is an explicit geographic proxy."
        elif r["source_id"] == "SRC_RENT_RECORDS":
            r["notes"] = "Record-level rent URLs recovered in metadata/source_recovery_register.csv; listing-based values remain provisional."
    with cat_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cat[0].keys()); w.writeheader(); w.writerows(cat)
    print(json.dumps({"records": len(out), "workbook": wb_name, "sha256": digest}, ensure_ascii=False))

if __name__ == "__main__":
    main()
