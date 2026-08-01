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
 for x in l: assert isinstance(json.loads(x['parent_input_ids']),list)
def test_no_forbidden_content():
 text='\n'.join(p.read_text(errors='ignore') for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '.venv' not in p.parts and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts and p.name!='test_lineage.py'); assert not re.search(r'BEGIN (RSA|OPENSSH) PRIVATE KEY|ghp_[A-Za-z0-9]+|password=',text,re.I); assert not any(x in text for x in ('no_investment_results.csv','delta_screening_results.csv','adapter_screening_only'))
