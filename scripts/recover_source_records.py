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
    "recovery_status", "verification_status", "verification_checked_at",
    "verification_evidence_url", "verification_evidence_type", "verification_note", "notes",
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
    stat_status = {
        "C01": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "C02": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "C03": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "C04": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "C05": ("verified_exact", "", "local media reproduces the statistical bulletin; exact value match, not necessarily the official origin page"),
        "C06": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "C07": ("verified_exact", "https://www.tjnj.net/newsview.aspx?newsid=20250427155536", "statistical-bulletin mirror confirms exact value; not necessarily the official origin page"),
        "C08": ("pending_manual_review", "https://tjj.jiaxing.gov.cn/module/download/downfile.jsp?classid=0&filename=78c3082538704b178ee0a1f21d20f0d1.pdf", "public bulletin mirror cross-checks 3751.81; original Jiaxing Statistics Bureau PDF still requires manual browser confirmation"),
        "M09": ("verified_exact", "https://www.changzhou.gov.cn/gi_news/618174366821577", "The original Changzhou government statistical bulletin directly displays the 2024 secondary-industry value added of 5139.4 billion CNY."),
        "M10": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "M11": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "M12": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "M13": ("verified_exact", "https://www.tjnj.net/newsview.aspx?newsid=20250401092827", "statistical-bulletin mirror confirms exact value; not necessarily the official origin page"),
        "M14": ("verified_exact", "", "direct page confirms city, 2024, second-industry value, unit, and value"),
        "M15": ("verified_exact", "https://tjgb.hongheiku.com/djs/64880.html", "statistical-bulletin mirror confirms exact value; not necessarily the official origin page"),
    }

    price_status = {
        "C01": ("pending_manual_review", "", "The multi-city quotation page is retained; automated review did not reliably expose the historical Shanghai row, so city/date/spec/brand/value need manual confirmation."),
        "C02": ("pending_manual_review", "", "The multi-city quotation page is retained; automated review did not reliably expose the historical Nanjing row, so city/date/spec/brand/value need manual confirmation."),
        "C03": ("verified_exact", "https://m.steelx2.com/region-quotation.aspx?city=suzhou&typeid=1", "Historical indexed quotation confirms Suzhou, 2026-07-14, HRB400E Phi20, and 3470 CNY/t. The regional quotation URL is dynamic and may display another date when opened later."),
        "C04": ("verified_page_but_value_unavailable", "", "Mysteel page is a dynamic historical quotation; the original range and midpoint require manual page access."),
        "C05": ("pending_manual_review", "", "The multi-city quotation page is retained; automated review did not reliably expose the historical Hangzhou row, so city/date/spec/brand/value need manual confirmation."),
        "C06": ("verified_exact", "https://www.mysteel.com/", "Mysteel Ningbo same-day market flash confirms Zhongtian HRB400E Phi20 at 3140 CNY/t; the original historical URL is retained."),
        "C07": ("pending_manual_review", "", "The multi-city quotation page is retained; automated review did not reliably expose the historical Hefei row, so city/date/spec/brand/value need manual confirmation."),
        "C08": ("verified_exact", "https://m.steelx2.com/region-quotation.aspx?city=jiaxing&typeid=1", "Current quotation page confirms Jiaxing, 2026-06-30, HRB400E Phi20, and 3440 CNY/t; the page is supplementary evidence and the original URL is retained."),
        "M09": ("verified_exact", "https://jiancai.m.mysteel.com/m/26060810/142E6539F044F562_abc.html", "Historical Changzhou quotation confirms HRB400E Phi20 at 3240-3290 CNY/t; the recorded 3265 CNY/t is the two-market-quotation midpoint (3240 + 3290) / 2."),
        "M10": ("verified_exact", "https://www.cngold.org/c/2026-07-10/c10006608.html", "Historical multi-city quotation confirms Nantong, 2026-07-10, Zhongtian HRB400E Phi20, and 3320 CNY/t."),
        "M11": ("verified_exact", "https://jiancai.m.mysteel.com/m/26070610/7DB53E9E3046D2F6_abc.html", "Historical Taizhou quotation confirms HRB400E Phi20 at 3190-3290 CNY/t; the recorded 3240 CNY/t is the two-market-quotation midpoint (3190 + 3290) / 2."),
        "M12": ("pending_manual_review", "", "SteelX2 page is retained, but automated review did not reliably expose the historical Shaoxing row and exact specification."),
        "M13": ("verified_page_but_value_unavailable", "", "Mysteel page is a dynamic historical quotation; the Huzhou Phi18-22 specification-band row requires manual page access."),
        "M14": ("pending_manual_review", "", "The city quotation page is retained; automated review did not reliably expose the historical Wuhu row, so city/date/spec/brand/value need manual confirmation."),
        "M15": ("verified_page_but_value_unavailable", "", "Jinhua value is a geographic proxy constructed from Hangzhou, Jiaxing and Shaoxing screening observations; the linked page is supporting context, not a direct Jinhua quotation."),
    }
    rent_status = {
        "C01": ("verified_exact", "https://www.cbre.com.cn/insights/figures/shanghai-real-estate-marketview-q1-2026", "official_market_report_exact_match", "CBRE Shanghai Figures Q1 2026 directly reports citywide average logistics rent of 35.8 RMB per sq. m. per month."),
        "C02": ("pending_manual_review", "", "original_listing_not_independently_retrievable", "The original Nanjing 58.com listing URL is retained, but the listing ID was not independently retrievable through current search or indexed snapshots. The recorded 0.7 CNY/m2/day and 21 CNY/m2/month remain provisional listing-based screening values."),
        "C03": ("verified_exact", "https://su.58.com/fangjia/cangkuzujin/", "platform_city_average_exact_match", "The 58.com Suzhou warehouse-rent trend page reports 0.75 CNY/m2/day for April 2026; the recorded monthly value is the stated 30-day conversion, 0.75 x 30 = 22.5 CNY/m2/month."),
        "C04": ("verified_exact", "https://wx.58.com/fangjia/cangkuzujin/", "platform_city_average_exact_match", "The 58.com Wuxi warehouse-rent trend page reports 0.66 CNY/m2/day for April 2026; 0.66 x 30 = 19.8 CNY/m2/month."),
        "C05": ("verified_exact", "https://hz.58.com/fangjia/cangkuzujin/", "platform_city_average_exact_match", "The 58.com Hangzhou warehouse-rent trend page reports 0.70 CNY/m2/day for July 2026; 0.70 x 30 = 21 CNY/m2/month."),
        "C06": ("verified_exact", "https://nb.58.com/fangjia/cangkuzujin/", "platform_city_average_exact_match", "The 58.com Ningbo warehouse-rent trend page reports 0.74 CNY/m2/day for July 2026; 0.74 x 30 = 22.2 CNY/m2/month."),
        "C07": ("pending_manual_review", "", "original_listing_not_independently_retrievable", "The original Feixi high-standard warehouse listing remains unavailable for independent page-level confirmation. The recorded 17 CNY/m2/month remains a provisional listing-based screening value and must not be described as a Hefei city average."),
        "C08": ("verified_exact", "https://jx.58.com/fangjia/cangkuzujin/", "platform_city_average_exact_match", "The 58.com Jiaxing warehouse-rent trend page reports 0.50 CNY/m2/day for July 2026; 0.50 x 30 = 15 CNY/m2/month."),
    }

    def verification(entity, default="pending_manual_review"):
        status, evidence, note = stat_status.get(entity, (default, "", ""))
        return {"verification_status": status, "verification_checked_at": "2026-08-02",
                "verification_evidence_url": evidence,
                "verification_evidence_type": "original_official_page_exact_match" if entity == "M09" else ("direct_page" if status == "verified_exact" and evidence == "" else ("mirror_cross_check" if evidence else "original_page")),
                "verification_note": note}

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
            **{"verification_status": "verified_metadata_only", "verification_checked_at": "", "verification_evidence_url": "", "verification_evidence_type": "", "verification_note": ""},
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
            **verification(mid), "notes": "Demand weights and demand fields are derived in the pipeline."})

    for rowno, r in rows(wb["Steel_Prices_Observed"], 4):
        mid, city = s(r.get("Market ID")), s(r.get("City"))
        proxy = "true" if "proxy" in s(r.get("Observation type")).lower() or mid == "M15" else "false"
        note = s(r.get("Notes"))
        if mid == "M15":
            note += " Parent observations: PRICE_C05, PRICE_C08, PRICE_M12."
        pstatus, pevidence, pnote = price_status[mid]
        if mid == "C04": note += " Range midpoint recomputes as (3310 + 3370) / 2 = 3340 CNY/t."
        if mid == "M09": note += " Range midpoint recomputes as (3240 + 3290) / 2 = 3265 CNY/t."
        if mid == "M11": note += " Range midpoint recomputes as (3190 + 3290) / 2 = 3240 CNY/t."
        out.append({"source_record_id": f"PRICE_{mid}", "entity_id": mid, "city": city,
            "variable_name": "observed_price_cny_per_tonne", "recovered_value": s(r.get("Selected screening price\n(CNY/t)")),
            "recovered_unit": "CNY/t", "source_url": s(r.get("Source URL")),
            "source_title": "Steel market quotation", "publisher_or_platform": "Mysteel / ChinaGold / SteelX2",
            "observation_date": s(r.get("Observation date")), "source_quality": s(r.get("Data quality")),
            "observation_type": s(r.get("Observation type")), "proxy_flag": proxy,
            "original_workbook": wb_name, "original_sheet": "Steel_Prices_Observed", "original_row": rowno,
            "workbook_sha256": digest, "recovery_status": "recovered",
            "verification_status": pstatus,
            "verification_checked_at": "2026-08-02", "verification_evidence_url": pevidence,
            "verification_evidence_type": {"C03": "search_indexed_historical_snapshot", "C06": "supplementary_mysteel_market_flash", "C08": "original_page_exact_match", "M09": "historical_range_midpoint", "M10": "supplementary_mysteel_market_flash", "M11": "historical_range_midpoint"}.get(mid, "supporting_context_only" if mid == "M15" else "dynamic_or_restricted_page"),
            "verification_note": pnote,
            "notes": note})

    for rowno, r in rows(wb["Warehouse_Rents_Observed"], 4):
        did, city = s(r.get("DC ID")), s(r.get("City"))
        rstatus, revidence, rtype, rnote = rent_status[did]
        out.append({"source_record_id": f"RENT_{did}", "entity_id": did, "city": city,
            "variable_name": "warehouse_rent_cny_per_sqm_month", "recovered_value": s(r.get("Monthly rent\n(CNY/m²/month)")),
            "recovered_unit": "CNY/m²/month", "source_url": s(r.get("Source URL")),
            "source_title": "Warehouse market rent observation", "publisher_or_platform": "CBRE / 58.com",
            "observation_date": s(r.get("Observation period")), "source_quality": s(r.get("Data quality")),
            "observation_type": s(r.get("Observation type")), "proxy_flag": "true",
            "original_workbook": wb_name, "original_sheet": "Warehouse_Rents_Observed", "original_row": rowno,
            "workbook_sha256": digest, "recovery_status": "recovered",
            "verification_status": rstatus, "verification_checked_at": "2026-08-02", "verification_evidence_url": revidence, "verification_evidence_type": rtype, "verification_note": rnote,
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
            # Keep source-record notes stable; detailed verification notes live
            # in the recovery register and must not alter the raw record text.
            if r.get("variable_name") not in {"steel_price"}:
                existing = r.get("notes", "").strip().strip('"')
                detail = x["notes"].strip()
                if detail and detail not in existing:
                    r["notes"] = (existing + " " + detail).strip()
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
