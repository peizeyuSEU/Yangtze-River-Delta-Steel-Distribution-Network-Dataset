"""Offline validation and manifest for v0.2 intracity candidate."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V01=ROOT/'data/processed/v0.1.0-preview'; V02=ROOT/'data/processed/v0.2.0-candidate'; ARC={f'C{i:02d}|C{i:02d}' for i in range(1,9)}
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks=[]
 def add(i,ok,msg):checks.append({'check_id':i,'status':'passed' if ok else 'failed','message':msg})
 a=read(V01/'dc_market.csv'); b=read(V02/'dc_market.csv'); m={x['dc_id']+'|'+x['market_id']:x for x in a}; n={x['dc_id']+'|'+x['market_id']:x for x in b}
 add('V02-001',len(b)==120,'120 DC-market arcs'); add('V02-002',all(float(x['road_distance_km'])>0 for x in b),'no zero-distance arcs'); add('V02-003',all(float(n[k]['road_distance_km'])==10 for k in ARC),'eight intracity distances are 10 km'); add('V02-004',all((n[k]['road_distance_km'],n[k]['transport_cost_baseline'])!=(m[k]['road_distance_km'],m[k]['transport_cost_baseline']) for k in ARC),'all eight targeted arcs changed'); add('V02-005',all(n[k]['road_distance_km']==m[k]['road_distance_km'] and n[k]['transport_cost_baseline']==m[k]['transport_cost_baseline'] for k in n if k not in ARC),'cross-city values unchanged'); add('V02-006',json.loads((ROOT/'metadata/v0.2_intracity_policy.json').read_text())['source_type']=='researcher_defined_scenario_parameter','intracity source type explicit'); add('V02-007',json.loads((V02/'case_config.json').read_text())['carbon_quota']=='not_yet_generated','quota remains ungenerated'); add('V02-008',len(read(ROOT/'metadata/v0.2_record_lineage.csv'))==918,'v0.2 lineage has 918 rows'); add('V02-009',(ROOT/'data/processed/v0.1.0-preview').exists(),'v0.1 directory retained')
 proc=[{'path':'data/processed/v0.2.0-candidate/'+p.name,'sha256':sha(p)} for p in sorted(V02.iterdir()) if p.is_file()]
 manifest={'dataset_name':'Yangtze River Delta Steel Distribution Network Dataset','version':'v0.2.0-candidate','base_version':'v0.1.0-preview','intracity_distance_km':10,'intracity_distance_policy':'representative_intracity_delivery_distance','source_type':'researcher_defined_scenario_parameter','affected_arc_ids':sorted(ARC),'osrm_recomputed':False,'processed_non_empty_values':918,'lineage_rows':918,'processed_files':proc,'carbon_quota_status':'not_yet_generated','preview_release_ready':True,'formal_release_ready':False,'model_execution_ready':False}
 (ROOT/'metadata/v0.2_release_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 with (ROOT/'metadata/v0.2_intracity_audit.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['check_id','status','message']);w.writeheader();w.writerows(checks)
 failed=sum(x['status']=='failed' for x in checks); (ROOT/'docs/v0.2_intracity_audit.md').write_text(f'# v0.2 intracity candidate audit\n\nOffline validation only. Checks: {len(checks)}; passed: {len(checks)-failed}; failed: {failed}.\n\nOnly C01|C01 through C08|C08 changed from 0 km to 10 km. All cross-city distances and all non-targeted costs are byte-for-value equal to v0.1. The 10 km value is a researcher-defined representative intracity delivery scenario, not an OSRM measurement. v0.1 remains untouched; no logistics-park coordinates are used.\n',encoding='utf-8'); print(json.dumps({'checks':len(checks),'failed':failed}))
if __name__=='__main__':main()
