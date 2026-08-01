import csv,re,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def test_all_processed_fields_have_lineage():
 inv=read(ROOT/'metadata/processed_field_inventory.csv'); cov=read(ROOT/'metadata/lineage_coverage_report.csv'); assert len(inv)==len(cov); assert all(float(x['lineage_coverage_rate'])==1 for x in cov)
def test_lineage_foreign_keys():
 l=read(ROOT/'metadata/record_lineage.csv'); s={x['source_record_id'] for x in read(ROOT/'data/source_records/source_records.csv')}; t={x['transformation_id'] for x in read(ROOT/'metadata/transformation_registry.csv')}; sc={x['scenario_id'] for x in read(ROOT/'metadata/scenario_registry.csv')}; cats={x['source_id'] for x in read(ROOT/'metadata/source_catalog.csv')}; sr=read(ROOT/'data/source_records/source_records.csv'); assert all(x['source_record_id'] in s for x in l if x['source_record_id']); assert all(x['transformation_id'] in t for x in l if x['transformation_id']); assert all(z in sc for x in l for z in x['scenario_id'].split('|') if z); assert all(x['source_id'] in cats for x in sr)
def test_lineage_unique_and_value_matches():
 l=read(ROOT/'metadata/record_lineage.csv'); assert len(l)==len({x['lineage_id'] for x in l});
 for x in l:
  if x['output_file'].endswith('.csv'):
   rows=read(ROOT/'data/processed/v0.1.0-preview'/x['output_file']); r=next(y for y in rows if (y.get('supplier_id')+'|'+y.get('dc_id') if x['output_file']=='supplier_dc.csv' else y.get('dc_id')+'|'+y.get('market_id') if x['output_file']=='dc_market.csv' else y.get('market_id') or y.get('dc_id') or y.get('node_id'))==x['output_record_id']); assert str(r[x['output_column']])==x['output_value']
def test_exact_price_rent_mapping():
 l=read(ROOT/'metadata/record_lineage.csv'); assert all(x['source_record_id']==f"PRICE_{x['output_record_id']}" for x in l if x['output_file']=='market_params.csv' and x['output_column']=='observed_price_cny_per_tonne'); assert all(x['source_record_id']==f"RENT_{x['output_record_id']}" for x in l if x['output_file']=='dc_params.csv' and x['output_column']=='warehouse_rent_cny_per_sqm_month')
def test_composite_arc_keys_and_parent_arrays():
 l=read(ROOT/'metadata/record_lineage.csv'); arcs=[x for x in l if x['output_file']=='dc_market.csv']; assert len({x['output_record_id'] for x in arcs})==120
 ids={x['lineage_id'] for x in l}; src={x['source_record_id'] for x in l if x['source_record_id']}; scen={z['scenario_id'] for z in read(ROOT/'metadata/scenario_registry.csv')};
 for x in l:
  for p in json.loads(x['parent_input_ids']): assert p in ids or p in src or p in scen
 for x in arcs:
  if x['output_column']=='road_distance_km':
   d,m=x['output_record_id'].split('|'); parents=json.loads(x['parent_input_ids']); assert f'NODE_{d}' in parents and f'NODE_{m}' in parents and 'OSRM_CACHE_001' in parents
def test_osrm_source_and_arc_endpoints():
 s=next(x for x in read(ROOT/'data/source_records/source_records.csv') if x['source_record_id']=='OSRM_CACHE_001'); assert s['source_id']=='SRC_OSRM_CACHE'
 l=read(ROOT/'metadata/record_lineage.csv');
 for x in l:
  if x['output_file'] in ('supplier_dc.csv','dc_market.csv') and x['output_column']=='road_distance_km':
   rec=x['output_record_id']; start,end=rec.split('|'); p=json.loads(x['parent_input_ids']); assert f'NODE_{start}' in p and f'NODE_{end}' in p
def test_trace_commands():
 import subprocess,sys
 cases=[('market_params.csv','C01','mu_annual_tonnes'),('market_params.csv','M15','observed_price_cny_per_tonne'),('dc_params.csv','C02','f_j_cny_per_year'),('supplier_dc.csv','S1|C01','road_distance_km'),('dc_market.csv','C01|M09','road_distance_km'),('dc_market.csv','C01|M09','transport_cost_baseline'),('inventory_params.csv','C01','F_j_cny_per_order'),('case_config.json','case_config','transport_rate_cny_per_tonne_km')]
 for fn,rec,col in cases:
  q=subprocess.run([sys.executable,str(ROOT/'scripts/trace_value.py'),'--file',fn,'--record',rec,'--column',col,'--format','json'],capture_output=True,text=True); assert q.returncode==0,q.stderr; assert 'output' in q.stdout
def test_representative_formulas():
 import json,math
 cfg=json.loads((ROOT/'config/baseline.json').read_text()); m=read(ROOT/'data/processed/v0.1.0-preview/market_params.csv'); d=read(ROOT/'data/processed/v0.1.0-preview/dc_params.csv'); sd=read(ROOT/'data/processed/v0.1.0-preview/supplier_dc.csv'); dm=read(ROOT/'data/processed/v0.1.0-preview/dc_market.csv'); r=next(x for x in m if x['market_id']=='C01'); assert abs(sum(float(x['demand_weight']) for x in m)-1)<1e-5
 weights=[11637.57,5831.06,12516.7,7716.02,6615.95,7882.7,4000,5000,5000,6000,5000,4000,3000,2500,3500]; assert abs(sum(float(x['demand_weight']) for x in m)-1)<1e-5; assert abs(float(r['mu_daily_tonnes'])-float(r['mu_annual_tonnes'])/cfg['operating_days'])<1e-5; assert abs(float(r['sigma2_daily'])-(cfg['demand_cv']*float(r['mu_daily_tonnes']))**2)<1e-3; assert abs(float(r['v_i_baseline'])-(float(r['observed_price_cny_per_tonne'])-cfg['production_cost_cny_per_tonne']))<1e-8
 j=next(x for x in d if x['dc_id']=='C02'); raw=next(x for x in read(ROOT/'data/raw/public/dc_observations_raw.csv') if x['dc_id']=='C02'); assert abs(float(j['f_j_cny_per_year'])-float(raw['warehouse_rent_cny_per_sqm_month'])*12*cfg['warehouse_area_sqm']*cfg['fixed_operating_multiplier'])<1e-8
 a=next(x for x in sd if x['dc_id']=='C01'); assert abs(float(a['transport_cost_baseline'])-float(a['road_distance_km'])*cfg['transport_rate_cny_per_tonne_km'])<5e-4; b=next(x for x in dm if x['dc_id']=='C01' and x['market_id']=='M09'); assert abs(float(b['transport_cost_baseline'])-float(b['road_distance_km'])*cfg['transport_rate_cny_per_tonne_km'])<5e-4
def test_no_forbidden_content():
 text='\n'.join(p.read_text(errors='ignore') for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '.venv' not in p.parts and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts and p.name!='test_lineage.py'); assert not re.search(r'BEGIN (RSA|OPENSSH) PRIVATE KEY|ghp_[A-Za-z0-9]+|password=',text,re.I); assert not any(x in text for x in ('no_investment_results.csv','delta_screening_results.csv','adapter_screening_only'))
