"""Create v0.2 lineage by updating only changed arc values."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'metadata/record_lineage.csv'; OUT=ROOT/'metadata/v0.2_record_lineage.csv'; ARC={f'C{i:02d}|C{i:02d}' for i in range(1,9)}
def main():
 rows=[]
 with SRC.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 for r in rows:
  if r['output_file']=='dc_market.csv' and r['output_record_id'] in ARC and r['output_column']=='road_distance_km':
   r['output_value']='10.000'; r['notes']='v0.2 representative intracity delivery distance; researcher-defined scenario parameter; not OSRM'
  if r['output_file']=='dc_market.csv' and r['output_record_id'] in ARC and r['output_column']=='transport_cost_baseline':
   r['output_value']='3.900000'; r['notes']='v0.2 cost recomputed from representative intracity distance and configured transport rate'
 with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 print(json.dumps({'rows':len(rows),'changed_arc_lineage':16}))
if __name__=='__main__':main()
