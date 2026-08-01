import csv,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def test_all_processed_fields_have_lineage():
 inv=read(ROOT/'metadata/processed_field_inventory.csv'); cov=read(ROOT/'metadata/lineage_coverage_report.csv'); assert len(inv)==len(cov); assert all(float(x['lineage_coverage_rate'])==1 for x in cov)
def test_lineage_foreign_keys():
 l=read(ROOT/'metadata/record_lineage.csv'); s={x['source_record_id'] for x in read(ROOT/'data/source_records/source_records.csv')}; t={x['transformation_id'] for x in read(ROOT/'metadata/transformation_registry.csv')}; assert all(x['source_record_id'] in s for x in l if x['source_record_id']); assert all(x['transformation_id'] in t for x in l if x['transformation_id'])
def test_no_forbidden_content():
 text='\n'.join(p.read_text(errors='ignore') for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '.venv' not in p.parts and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts and p.name!='test_lineage.py'); assert not re.search(r'BEGIN (RSA|OPENSSH) PRIVATE KEY|ghp_[A-Za-z0-9]+|password=',text,re.I); assert not any(x in text for x in ('no_investment_results.csv','delta_screening_results.csv','adapter_screening_only'))
