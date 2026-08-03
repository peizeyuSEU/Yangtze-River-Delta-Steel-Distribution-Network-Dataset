"""Build an isolated v0.2 candidate with representative 10 km intracity arcs."""
import argparse,csv,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V01=ROOT/'data/processed/v0.1.0-preview'; V02=ROOT/'data/processed/v0.2.0-candidate'; ARC_IDS={f'C{i:02d}|C{i:02d}' for i in range(1,9)}
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--distance-km',type=float,default=10.0); args=ap.parse_args(); assert args.distance_km>0
 if V02.exists(): shutil.rmtree(V02)
 V02.mkdir(parents=True)
 for p in V01.iterdir():
  if p.is_file(): shutil.copy2(p,V02/p.name)
 rows=read(V01/'dc_market.csv'); changed=[]
 for r in rows:
  aid=r['dc_id']+'|'+r['market_id']
  if aid in ARC_IDS:
   r['road_distance_km']=f'{args.distance_km:.3f}'; r['transport_cost_baseline']=f'{args.distance_km*0.39:.6f}'; changed.append(aid)
 with (V02/'dc_market.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['dc_id','market_id','road_distance_km','transport_cost_baseline']);w.writeheader();w.writerows(rows)
 cfg=json.loads((V02/'case_config.json').read_text(encoding='utf-8')); cfg['version']='v0.2.0-candidate'; (V02/'case_config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 meta={'dataset_version':'v0.2.0-candidate','intracity_distance_policy':'representative_intracity_delivery_distance','intracity_distance_km':args.distance_km,'affected_arc_ids':sorted(ARC_IDS),'source_type':'researcher_defined_scenario_parameter','osrm_recomputed':False,'carbon_quota':'not_yet_generated'}; (ROOT/'metadata/v0.2_intracity_policy.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'version':'v0.2.0-candidate','changed_arcs':changed,'distance_km':args.distance_km}))
if __name__=='__main__':main()
