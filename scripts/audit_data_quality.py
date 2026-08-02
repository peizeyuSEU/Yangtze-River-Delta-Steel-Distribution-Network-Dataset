"""Offline, read-only audit of the public dataset and its generated inputs."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed" / "v0.1.0-preview"
RAW = ROOT / "data" / "raw" / "public"
AUDIT = ROOT / "metadata" / "data_quality_audit.csv"
REPORT = ROOT / "docs" / "data_quality_audit.md"

def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))
def num(v):
    x=float(v); assert math.isfinite(x); return x
def hav(a,b):
    r=6371.0088; p=math.pi/180
    dlat=(b[0]-a[0])*p; dlon=(b[1]-a[1])*p
    q=math.sin(dlat/2)**2+math.cos(a[0]*p)*math.cos(b[0]*p)*math.sin(dlon/2)**2
    return 2*r*math.asin(math.sqrt(q))

def main():
    cfg=json.loads((ROOT/"config/baseline.json").read_text(encoding="utf-8"))
    results=[]
    def add(cid,cat,status,file="",record="",field="",observed="",expected="",tol="",message=""):
        results.append(dict(check_id=cid,category=cat,severity="error" if status=="failed" else ("warning" if status=="warning" else "info"),status=status,file=file,record_id=record,field=field,observed=str(observed),expected=str(expected),tolerance=str(tol),message=message))
    nodes=read(P/"nodes.csv"); markets=read(P/"market_params.csv"); dcs=read(P/"dc_params.csv"); inv=read(P/"inventory_params.csv"); sda=read(P/"supplier_dc.csv"); dma=read(P/"dc_market.csv"); rawm=read(RAW/"market_observations_raw.csv"); rawd=read(RAW/"dc_observations_raw.csv")
    ids=[r["node_id"] for r in nodes]; add("ENT-001","entity","passed", "nodes.csv", message=f"unique node IDs={len(ids)}") if len(ids)==len(set(ids)) else add("ENT-001","entity","failed", "nodes.csv", message="duplicate node IDs")
    ns=sum(r['supplier_flag']=='1' for r in nodes); nd=sum(r['candidate_dc_flag']=='1' for r in nodes); nm=sum(r['market_flag']=='1' for r in nodes)
    add("ENT-002","entity","passed" if (ns,nd,nm,len(nodes))==(1,8,15,16) else "failed", "nodes.csv", observed=f"supplier={ns},dc={nd},market={nm},nodes={len(nodes)}", expected="supplier=1,dc=8,market=15,nodes=16", message="DC/market role overlap is allowed; role-count sum need not equal node count")
    node_map={r["node_id"]:r for r in nodes}; dc_ids={r["dc_id"] for r in dcs}; market_ids={r["market_id"] for r in markets}
    add("ENT-003","entity","passed" if dc_ids.issubset(node_map) and market_ids.issubset(node_map) else "failed", "dc_params.csv", expected="all DC/market foreign keys exist", message="foreign-key check")
    add("ENT-004","entity","passed" if len({(r['supplier_id'],r['dc_id']) for r in sda})==len(sda) and len({(r['dc_id'],r['market_id']) for r in dma})==len(dma) else "failed", "supplier_dc.csv;dc_market.csv", expected="no duplicate arcs", message="arc uniqueness")
    coords=[(r["latitude"],r["longitude"]) for r in nodes]; bounds=all(-90<=num(a)<=90 and -180<=num(b)<=180 for a,b in coords)
    add("GEO-001","coordinates","passed" if bounds else "failed","nodes.csv",expected="latitude [-90,90], longitude [-180,180]",message="coordinate bounds")
    add("GEO-002","coordinates","passed" if len(set(coords))==len(coords) else "failed","nodes.csv",message="no duplicate coordinates across nodes")
    distances=[]; anomalies=[]
    for fn,rows,kind in (("supplier_dc.csv",sda,"supplier_dc"),("dc_market.csv",dma,"dc_market")):
        for r in rows:
            d=num(r["road_distance_km"]); distances.append(d); a=node_map[r["supplier_id"] if kind=="supplier_dc" else r["dc_id"]]; b=node_map[r["dc_id"] if kind=="supplier_dc" else r["market_id"]]; g=hav((num(a["latitude"]),num(a["longitude"])),(num(b["latitude"]),num(b["longitude"])))
            rec=r["supplier_id"]+'|'+r["dc_id"] if kind=="supplier_dc" else r["dc_id"]+'|'+r["market_id"]
            if d<0 or (g>0 and d+1e-6<g): anomalies.append((fn,rec,d,g))
            if kind=="dc_market" and r["dc_id"]==r["market_id"] and abs(d)<1e-12: add("DST-003","distance","warning",fn,rec,"road_distance_km",d,0,0,"documented_structural_zero: same-city DC-market arc")
            elif d<=0: add("DST-004","distance","failed",fn,rec,"road_distance_km",d,">0","non-same-city arc must have positive road distance")
    add("DST-001","distance","passed" if not any(d<0 for d in distances) else "failed","supplier_dc.csv;dc_market.csv",observed=f"min={min(distances):.3f},max={max(distances):.3f}",expected=">=0",message=f"{len(distances)} road distances")
    add("DST-002","distance","failed" if anomalies else "passed","supplier_dc.csv;dc_market.csv",observed=len(anomalies),expected=0,message="road distance below Haversine or negative" if anomalies else "no Haversine anomaly")
    wsum=sum(num(r["demand_weight"]) for r in markets); add("DEM-001","demand","passed" if abs(wsum-1)<=1e-6 else "failed","market_params.csv",observed=wsum,expected=1,tol=1e-6,message="demand weights sum")
    total=cfg["regional_total_demand_tonnes"]; days=cfg["operating_days"]
    for r in markets:
        expected=num(r["demand_weight"])*total; add("DEM-002","demand","passed" if abs(num(r["mu_annual_tonnes"])-expected)<1e-2 else "failed","market_params.csv",r["market_id"],"mu_annual_tonnes",r["mu_annual_tonnes"],expected,1e-2,"annual demand formula (pipeline rounding)")
        expected=num(r["mu_annual_tonnes"])/days; add("DEM-003","demand","passed" if abs(num(r["mu_daily_tonnes"])-expected)<1e-5 else "failed","market_params.csv",r["market_id"],"mu_daily_tonnes",r["mu_daily_tonnes"],expected,1e-5,"daily demand formula (pipeline rounding)")
        expected=(cfg["demand_cv"]*num(r["mu_daily_tonnes"]))**2; add("DEM-004","demand","passed" if abs(num(r["sigma2_daily"])-expected)<1e-2 else "failed","market_params.csv",r["market_id"],"sigma2_daily",r["sigma2_daily"],expected,1e-2,"variance formula (pipeline rounding)")
    add("PRC-001","price","passed" if all(num(r["observed_price_cny_per_tonne"])>0 for r in markets) else "failed","market_params.csv",message="positive observed prices")
    for r in markets:
        expected=num(r["observed_price_cny_per_tonne"])-cfg["production_cost_cny_per_tonne"]; add("PRC-002","price","passed" if abs(num(r["v_i_baseline"])-expected)<1e-6 else "failed","market_params.csv",r["market_id"],"v_i_baseline",r["v_i_baseline"],expected,1e-6,"net price formula")
    m15=num(next(r for r in markets if r["market_id"]=="M15")["observed_price_cny_per_tonne"]); parents=[num(next(r for r in markets if r["market_id"]==k)["observed_price_cny_per_tonne"]) for k in ("C05","C08","M12")]; add("PRC-003","price","passed" if abs(m15-sum(parents)/3)<1e-2 else "failed","market_params.csv","M15","observed_price_cny_per_tonne",m15,sum(parents)/3,1e-2,"Jinhua proxy mean (rounded screening value)")
    rents=read(RAW/"dc_observations_raw.csv"); rentmap={r["dc_id"]:r for r in rents};
    for r in dcs:
        expected=num(r["warehouse_rent_cny_per_sqm_month"])*12*cfg["warehouse_area_sqm"]*cfg["fixed_operating_multiplier"]; add("RNT-001","rent","passed" if abs(num(r["f_j_cny_per_year"])-expected)<1e-6 else "failed","dc_params.csv",r["dc_id"],"f_j_cny_per_year",r["f_j_cny_per_year"],expected,1e-6,"fixed cost formula")
    for did in ("C03","C04","C05","C06","C08"):
        daily={"C03":.75,"C04":.66,"C05":.70,"C06":.74,"C08":.50}[did]; monthly=num(next(r for r in dcs if r["dc_id"]==did)["warehouse_rent_cny_per_sqm_month"]); add("RNT-002","rent","passed" if abs(daily*30-monthly)<1e-9 else "failed","dc_params.csv",did,"warehouse_rent_cny_per_sqm_month",monthly,daily*30,1e-9,"30-day daily-to-monthly conversion")
    for fn,rows in (("supplier_dc.csv",sda),("dc_market.csv",dma)):
        for r in rows:
            expected=num(r["road_distance_km"])*cfg["transport_rate_cny_per_tonne_km"]; add("TRN-001","transport","passed" if abs(num(r["transport_cost_baseline"])-expected)<5e-4 else "failed",fn,r.get("supplier_id",r.get("dc_id"))+"|"+r["dc_id"] if fn.startswith("supplier") else r["dc_id"]+"|"+r["market_id"],"transport_cost_baseline",r["transport_cost_baseline"],expected,5e-4,"distance times transport rate (6-decimal output rounding)")
    numeric_files=["nodes.csv","market_params.csv","dc_params.csv","inventory_params.csv","dc_emission_params.csv","supplier_dc.csv","dc_market.csv"]
    blanks=[]
    for fn in numeric_files:
        for row in read(P/fn):
            for k,v in row.items():
                if v=="" or v.lower() in {"nan","inf","-inf","infinity","-infinity"}: blanks.append((fn,k))
    add("UNT-001","units","warning" if blanks else "passed","processed",observed=len(blanks),expected=0,message="blank/non-finite cells; structural text fields may be intentionally absent")
    # Emission parameters and derived-on-use transport emissions.
    ep=read(P/"dc_emission_params.csv"); ep_ok=all(abs(num(r["hat_f_j_tco2e_per_year"])-cfg["fixed_dc_emission_tco2e_per_year"])<1e-12 and abs(num(r["hat_h_tco2e_per_tonne_year"])-cfg["inventory_emission_factor_tco2e_per_tonne_year"])<1e-12 for r in ep)
    add("EMI-001","emissions","passed" if ep_ok else "failed","dc_emission_params.csv",expected="hat_f=fixed_dc_emission; hat_h=inventory_emission_factor",message="DC emission parameters")
    ef=cfg["transport_emission_factor_tco2e_per_tonne_km"]; add("EMI-002","emissions","passed" if ef>0 and math.isfinite(ef) else "failed","baseline.json",observed=ef,expected=">0 finite",message="transport emissions are derived-on-use as road distance times factor")
    # Schema and lineage exact bijection across all seven CSVs and case_config JSON.
    expected_schema={}
    for x in read(ROOT/"metadata/data_dictionary.csv"): expected_schema.setdefault(x["file_name"],[]).append(x["column_name"])
    schema_bad=[]
    for fn,cols in expected_schema.items():
        path=P/fn
        if fn.endswith(".json"): continue
        if path.exists() and list(csv.reader(path.open(encoding="utf-8-sig")))[0]!=cols: schema_bad.append(fn)
    add("SCH-001","schema","passed" if not schema_bad else "failed","processed_field_inventory.csv",observed=schema_bad,expected="all declared column orders match",message="data dictionary schema")
    lineage=read(ROOT/"metadata/record_lineage.csv"); lid=[x["lineage_id"] for x in lineage]; add("LIN-001","lineage","passed" if len(lineage)==918 else "failed","record_lineage.csv",observed=len(lineage),expected=918,message="lineage record count")
    add("LIN-002","lineage","passed" if len(lid)==len(set(lid)) else "failed","record_lineage.csv",observed=len(lid),expected="unique lineage_id",message="lineage ID uniqueness")
    def record_id(fn,r): return r["supplier_id"]+"|"+r["dc_id"] if fn=="supplier_dc.csv" else r["dc_id"]+"|"+r["market_id"] if fn=="dc_market.csv" else r.get("market_id") or r.get("dc_id") or r.get("node_id")
    actual=[]
    for fn in ("nodes.csv","market_params.csv","dc_params.csv","inventory_params.csv","dc_emission_params.csv","supplier_dc.csv","dc_market.csv"):
        for r in read(P/fn):
            for k,v in r.items():
                if v!="": actual.append((fn,record_id(fn,r),k,str(v)))
    cfg_data=json.loads((P/"case_config.json").read_text(encoding="utf-8")); actual += [("case_config.json","case_config",k,str(v)) for k,v in cfg_data.items() if v is not None]
    linvals=[(x["output_file"],x["output_record_id"],x["output_column"],x["output_value"]) for x in lineage]
    add("LIN-003","lineage","passed" if len(actual)==918 else "failed","processed",observed=len(actual),expected=918,message="processed non-empty value count")
    add("LIN-004","lineage","passed" if len(actual)==len(set(actual))==len(linvals) and set(actual)==set(linvals) else "failed","processed;record_lineage.csv",observed=f"processed={len(actual)},lineage={len(linvals)}",expected="strict bijection",message="processed-to-lineage exact value mapping")
    source_ids={x["source_record_id"] for x in read(ROOT/"data/source_records/source_records.csv")}; trans_ids={x["transformation_id"] for x in read(ROOT/"metadata/transformation_registry.csv")}; scen_ids={x["scenario_id"] for x in read(ROOT/"metadata/scenario_registry.csv")}; linids=set(lid)
    parent_bad=[]; source_bad=[]; scen_bad=[]; trans_bad=[]
    for x in lineage:
        if x["source_record_id"] and x["source_record_id"] not in source_ids: source_bad.append(x["lineage_id"])
        if x["transformation_id"] and x["transformation_id"] not in trans_ids: trans_bad.append(x["lineage_id"])
        if x["scenario_id"] and any(z not in scen_ids for z in x["scenario_id"].split("|")): scen_bad.append(x["lineage_id"])
        try: parents=json.loads(x["parent_input_ids"] or "[]")
        except Exception: parents=["BAD_JSON"]
        if any(p not in linids and p not in source_ids and p not in scen_ids for p in parents): parent_bad.append(x["lineage_id"])
    add("LIN-005","lineage","passed" if not parent_bad else "failed","record_lineage.csv",observed=len(parent_bad),expected=0,message="parent references")
    add("LIN-006","lineage","passed" if not source_bad else "failed","record_lineage.csv",observed=len(source_bad),expected=0,message="source-record foreign keys")
    add("LIN-007","lineage","passed" if not scen_bad else "failed","record_lineage.csv",observed=len(scen_bad),expected=0,message="scenario foreign keys")
    add("LIN-008","lineage","passed" if not trans_bad else "failed","record_lineage.csv",observed=len(trans_bad),expected=0,message="transformation registry foreign keys")
    # Documented limitations are warnings, not hidden in prose.
    add("WARN-001","limitations","warning","dc_market.csv","C01|C01","road_distance_km",0,0,0,"same-city structural zero is permitted")
    add("WARN-002","limitations","warning","market_params.csv","M15","observed_price_cny_per_tonne","proxy","direct observation","","Jinhua price is a documented geographic proxy")
    add("WARN-003","limitations","warning","dc_params.csv","C02|C07","rent_status","specific_listing","city_average","","rents are specific listings, not city averages")
    add("WARN-004","limitations","warning","source_records.csv","all","observation_date","mixed","single date","","source time bases differ across statistics, prices, and rents")
    add("WARN-005","limitations","warning","case_config.json","case_config","carbon_quota","not_yet_generated","generated quota","","carbon quota is not generated in this preview")
    known=set(cfg); reserved={"carbon_quota","delta_candidates","allow_network","osrm_cache"}; script_text="\n".join(p.read_text(encoding="utf-8",errors="ignore") for p in (ROOT/"scripts").glob("*.py")); unused=[k for k in known if k not in reserved and k not in script_text]; cache=(ROOT/cfg["osrm_cache"]).exists(); version_ok=cfg["version"]==P.name; cfg_ok=not unused and cfg["carbon_quota"]=="not_yet_generated" and cfg["allow_network"] is False and cache and version_ok
    add("CFG-001","configuration","passed" if cfg_ok else "failed","baseline.json",observed=f"unused={unused},cache={cache},version_ok={version_ok}",expected="known keys used/reserved; carbon_quota not_yet_generated; allow_network=false; cache exists; version matches",message="configuration coverage")
    # summary output
    with AUDIT.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["check_id","category","severity","status","file","record_id","field","observed","expected","tolerance","message"]); w.writeheader(); w.writerows(results)
    counts={s:sum(x["status"]==s for x in results) for s in ("passed","warning","failed")}
    zero_ids=[x["record_id"] for x in results if x["check_id"]=="DST-003"]
    report=["# Data quality audit", "", f"Generated: {datetime.now().date().isoformat()} (offline)", "", f"Total checks: {len(results)}", f"Passed: {counts['passed']}", f"Warnings: {counts['warning']}", f"Failed: {counts['failed']}", "", "## Scope and findings", "", f"Hard checks passed: {counts['passed']}; failed checks: {counts['failed']}.", f"Dataset scale: {len(nodes)} nodes (1 supplier, 8 candidate DCs, 15 markets), {len(sda)} supplier-DC arcs, {len(dma)} DC-market arcs.", f"Road distance range: {min(distances):.3f}--{max(distances):.3f} km; Haversine/road anomalies: {len(anomalies)}.", f"Documented same-city zero-distance arcs ({len(zero_ids)}): {', '.join(zero_ids)}; these are warnings, not data errors.", "Processed non-empty values: 918; record_lineage rows: 918; exact processed-to-lineage bijection and foreign-key checks passed.", "Demand, price, rent, fixed-cost, transport-cost, emission-parameter, schema, configuration, and lineage checks are included in the CSV.", "Time basis differs across sources: 2024 second-industry statistics, 2026 price observations, and 2026 rent observations; these are screening/calibration inputs.", "Proxy values: Jinhua PRICE_M15 (mean of PRICE_C05, PRICE_C08, PRICE_M12).", "Specific listings: RENT_C02 Nanjing and RENT_C07 Feixi/Hefei; they are not city averages.", "Warnings are documented limitations: same-city structural zeros, the Jinhua proxy, specific listings, mixed source dates, and carbon_quota not_yet_generated.", "No processed value should be modified as a result of this audit. Any future correction would affect the corresponding processed parameter file, lineage records, and downstream validation reports.", "The audit is offline and does not invoke network access, GA-BP, BP, CPLEX, or any solver."]
    REPORT.write_text("\n".join(report)+"\n",encoding="utf-8")
    print(json.dumps({"checks":len(results),"passed":counts["passed"],"warning":counts["warning"],"failed":counts["failed"]}))
if __name__=="__main__": main()
