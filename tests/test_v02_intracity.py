import csv,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def test_v02_only_eight_arcs_change_and_cross_city_equal():
 a=read(ROOT/'data/processed/v0.1.0-preview/dc_market.csv'); b=read(ROOT/'data/processed/v0.2.0-candidate/dc_market.csv'); A={f'C{i:02d}|C{i:02d}' for i in range(1,9)}; x={r['dc_id']+'|'+r['market_id']:r for r in a}; y={r['dc_id']+'|'+r['market_id']:r for r in b}; assert len(y)==120 and all(float(r['road_distance_km'])>0 for r in b); assert all(float(y[k]['road_distance_km'])==10 for k in A); assert all(y[k]==x[k] for k in y if k not in A)
def test_v02_policy_lineage_manifest_and_scenarios():
 p=json.loads((ROOT/'metadata/v0.2_intracity_policy.json').read_text()); assert p['intracity_distance_policy']=='representative_intracity_delivery_distance' and p['source_type']=='researcher_defined_scenario_parameter' and p['osrm_recomputed'] is False; assert len(read(ROOT/'metadata/v0.2_record_lineage.csv'))==918; m=json.loads((ROOT/'metadata/v0.2_release_manifest.json').read_text()); assert m['carbon_quota_status']=='not_yet_generated' and m['model_execution_ready'] is False; rows=read(ROOT/'metadata/intracity_distance_sensitivity_summary.csv'); assert len(rows)==40 and {int(x['scenario_km']) for x in rows}=={0,5,10,15,20}
def test_v01_hashes_and_v02_audit():
 expected={'case_config.json':'bec13b33d8b03c1cf3afbfd6a0c3a41b56389beece99eba489bfc985fbcf37a9','dc_market.csv':'00190d18bbeacd733e055134bb9b5d8f59739fe41996f6b2527b89fb0a8a85db'}
 for fn,h in expected.items():assert hashlib.sha256((ROOT/'data/processed/v0.1.0-preview'/fn).read_bytes()).hexdigest()==h
 q=subprocess.run([sys.executable,str(ROOT/'scripts/audit_v02_intracity_candidate.py')],capture_output=True,text=True); assert q.returncode==0 and '"failed": 0' in q.stdout
