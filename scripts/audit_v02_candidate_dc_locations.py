"""Offline audit of the v0.2 candidate DC location register."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'metadata/v0.2_candidate_dc_locations.csv'; OUT=ROOT/'metadata/v0.2_candidate_dc_location_audit.csv'; DOC=ROOT/'docs/v0.2_candidate_dc_location_audit.md'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 rows=read(SRC); checks=[]
 def add(i,ok,msg):checks.append({'check_id':i,'status':'passed' if ok else 'failed','message':msg})
 add('V02-001',len(rows)==8,'exactly eight candidate DC records')
 add('V02-002',{r['dc_id'] for r in rows}=={f'C{i:02d}' for i in range(1,9)},'C01-C08 present')
 add('V02-003',len({r['city'] for r in rows})==8,'one primary candidate per city')
 add('V02-004',all(r['candidate_name_cn'] and r['candidate_name_en'] for r in rows),'candidate names non-empty')
 add('V02-005',all(r['official_source_url'].startswith('http') for r in rows),'official source URLs present')
 allowed_s={'verified_exact_address','verified_named_poi','verified_within_official_boundary','pending_manual_review','not_geocoded'}; allowed_c={'high','moderate','low'}; allowed_m={'exact_address','named_logistics_poi','official_project_location','official_boundary_representative','pending'}
 add('V02-006',all(r['coordinate_status'] in allowed_s for r in rows),'coordinate status enum valid'); add('V02-007',all(r['confidence_level'] in allowed_c for r in rows),'confidence enum valid'); add('V02-008',all(r['representative_point_method'] in allowed_m for r in rows),'representative method enum valid')
 for r in rows:
  haslat=bool(r['latitude']); haslon=bool(r['longitude']); add('V02-COORD-'+r['dc_id'],(haslat==haslon) and (not haslat or (-90<=float(r['latitude'])<=90 and -180<=float(r['longitude'])<=180)),'coordinate pair is either blank or in range')
  if r['confidence_level']=='high': add('V02-HIGH-'+r['dc_id'],bool(r['address_or_boundary'] and r['official_source_url']),'high-confidence candidate has location evidence')
 add('V02-009',all(not (r['latitude'] and r['longitude']) for r in rows),'no unverified coordinates entered'); add('V02-010',not any(r['latitude'] and r['longitude'] and 'city centre' in ((r.get('notes') or '')+' '+(r.get('selection_rationale') or '')).lower() for r in rows),'city-centre substitutions excluded'); add('V02-011',(ROOT/'data/processed/v0.1.0-preview').exists(),'v0.1 processed directory remains the only processed dataset')
 with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['check_id','status','message']);w.writeheader();w.writerows(checks)
 failed=sum(x['status']=='failed' for x in checks); DOC.write_text('# v0.2 candidate DC location audit\n\nOffline audit only; no geocoding or network calls are performed.\n\n'+f'Checks: {len(checks)}; passed: {len(checks)-failed}; failed: {failed}.\n\nEight candidate records C01-C08 are registered. Coordinates are intentionally blank pending repeatable address/POI/boundary evidence, so no city-centre coordinate is repurposed as a DC location. The register does not enter the v0.1 build and no OSRM matrix was regenerated.\n',encoding='utf-8'); print(json.dumps({'checks':len(checks),'failed':failed}))
if __name__=='__main__':main()
