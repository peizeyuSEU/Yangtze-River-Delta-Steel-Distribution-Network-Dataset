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
def test_arc_identifier_source_mapping():
 l={(x['output_file'],x['output_record_id'],x['output_column']):x['source_record_id'] for x in read(ROOT/'metadata/record_lineage.csv')}
 for x in read(ROOT/'data/processed/v0.1.0-preview/supplier_dc.csv'):
  rec=x['supplier_id']+'|'+x['dc_id']; assert l['supplier_dc.csv',rec,'supplier_id']=='NODE_'+x['supplier_id']; assert l['supplier_dc.csv',rec,'dc_id']=='NODE_'+x['dc_id']
 for x in read(ROOT/'data/processed/v0.1.0-preview/dc_market.csv'):
  rec=x['dc_id']+'|'+x['market_id']; assert l['dc_market.csv',rec,'dc_id']=='NODE_'+x['dc_id']; assert l['dc_market.csv',rec,'market_id']=='NODE_'+x['market_id']
def test_processed_values_and_lineage_are_exact_bijection():
 actual=[];p=ROOT/'data/processed/v0.1.0-preview'
 for fn in ('nodes.csv','market_params.csv','dc_params.csv','inventory_params.csv','dc_emission_params.csv','supplier_dc.csv','dc_market.csv'):
  for r in read(p/fn):
   rec=r.get('supplier_id')+'|'+r.get('dc_id') if fn=='supplier_dc.csv' else r.get('dc_id')+'|'+r.get('market_id') if fn=='dc_market.csv' else r.get('market_id') or r.get('dc_id') or r.get('node_id')
   actual += [(fn,rec,k,v) for k,v in r.items() if v!='']
 cfg=json.loads((p/'case_config.json').read_text()); actual += [('case_config.json','case_config',k,str(v)) for k,v in cfg.items() if v is not None]
 lineage=[(x['output_file'],x['output_record_id'],x['output_column'],x['output_value']) for x in read(ROOT/'metadata/record_lineage.csv')]; assert len(actual)==len(set(actual))==len(lineage); assert set(actual)==set(lineage)
def test_case_config_values_and_roles():
 cfg=json.loads((ROOT/'data/processed/v0.1.0-preview/case_config.json').read_text()); ls=[x for x in read(ROOT/'metadata/record_lineage.csv') if x['output_file']=='case_config.json']; assert len(ls)==len(cfg)==7
 for x in ls:
  assert x['output_value']==str(cfg[x['output_column']]); assert x['transformation_id']=='T_CONFIG_MAPPING_001'; assert x['lineage_role']==('structural' if x['output_column']=='version' else 'scenario')
 assert cfg['carbon_quota']=='not_yet_generated'
def test_trace_commands():
 import subprocess,sys
 cases=[('market_params.csv','C01','mu_annual_tonnes'),('market_params.csv','M15','observed_price_cny_per_tonne'),('dc_params.csv','C02','f_j_cny_per_year'),('supplier_dc.csv','S1|C01','road_distance_km'),('dc_market.csv','C01|M09','road_distance_km'),('dc_market.csv','C01|M09','transport_cost_baseline'),('inventory_params.csv','C01','F_j_cny_per_order'),('case_config.json','case_config','transport_rate_cny_per_tonne_km')]
 for fn,rec,col in cases:
  q=subprocess.run([sys.executable,str(ROOT/'scripts/trace_value.py'),'--file',fn,'--record',rec,'--column',col,'--format','json'],capture_output=True,text=True); assert q.returncode==0,q.stderr; assert 'output' in q.stdout
def test_representative_formulas():
 import json,math
 cfg=json.loads((ROOT/'config/baseline.json').read_text()); m=read(ROOT/'data/processed/v0.1.0-preview/market_params.csv'); d=read(ROOT/'data/processed/v0.1.0-preview/dc_params.csv'); sd=read(ROOT/'data/processed/v0.1.0-preview/supplier_dc.csv'); dm=read(ROOT/'data/processed/v0.1.0-preview/dc_market.csv'); r=next(x for x in m if x['market_id']=='C01'); assert abs(sum(float(x['demand_weight']) for x in m)-1)<1e-5
 raw_stats=read(ROOT/'data/raw/public/market_observations_raw.csv'); weights={x['market_id']:float(x['second_industry_va_2024_100m_cny']) for x in raw_stats}; assert abs(float(r['demand_weight'])-round(weights['C01']/sum(weights.values()),8))<1e-8; assert abs(float(r['mu_annual_tonnes'])-round(weights['C01']/sum(weights.values())*cfg['regional_total_demand_tonnes'],6))<1e-4; assert abs(float(r['mu_daily_tonnes'])-float(r['mu_annual_tonnes'])/cfg['operating_days'])<1e-5; assert abs(float(r['sigma2_daily'])-(cfg['demand_cv']*float(r['mu_daily_tonnes']))**2)<1e-3; assert abs(float(r['v_i_baseline'])-(float(r['observed_price_cny_per_tonne'])-cfg['production_cost_cny_per_tonne']))<1e-8
 j=next(x for x in d if x['dc_id']=='C02'); raw=next(x for x in read(ROOT/'data/raw/public/dc_observations_raw.csv') if x['dc_id']=='C02'); assert abs(float(j['f_j_cny_per_year'])-float(raw['warehouse_rent_cny_per_sqm_month'])*12*cfg['warehouse_area_sqm']*cfg['fixed_operating_multiplier'])<1e-8
 a=next(x for x in sd if x['dc_id']=='C01'); assert abs(float(a['transport_cost_baseline'])-float(a['road_distance_km'])*cfg['transport_rate_cny_per_tonne_km'])<5e-4; b=next(x for x in dm if x['dc_id']=='C01' and x['market_id']=='M09'); assert abs(float(b['transport_cost_baseline'])-float(b['road_distance_km'])*cfg['transport_rate_cny_per_tonne_km'])<5e-4
def test_no_forbidden_content():
 text='\n'.join(p.read_text(errors='ignore') for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '.venv' not in p.parts and '.pytest_cache' not in p.parts and '__pycache__' not in p.parts and p.name!='test_lineage.py'); assert not re.search(r'BEGIN (RSA|OPENSSH) PRIVATE KEY|ghp_[A-Za-z0-9]+|password=',text,re.I); assert not any(x in text for x in ('no_investment_results.csv','delta_screening_results.csv','adapter_screening_only'))

def test_recovered_public_source_register_is_complete():
 reg=read(ROOT/'metadata/source_recovery_register.csv'); assert len(reg)==54
 assert len({x['source_record_id'] for x in reg})==54
 assert all(x['original_workbook']=='长三角钢材配送案例_公开数据校准包_v2.xlsx' for x in reg)
 assert all(x['workbook_sha256']=='DA93615FF0A440843378A1763600FC5EEEE0C570585A2811B7188782D234F91B' for x in reg)
 assert all(x['original_sheet'] in {'Nodes','Market_Proxy','Steel_Prices_Observed','Warehouse_Rents_Observed'} for x in reg)
 assert all(x['source_url'].startswith('http') for x in reg)

def test_recovered_source_foreign_keys_and_proxy_disclosure():
 reg={x['source_record_id']:x for x in read(ROOT/'metadata/source_recovery_register.csv')}
 src={x['source_record_id']:x for x in read(ROOT/'data/source_records/source_records.csv')}
 assert set(reg).issubset(src)
 assert reg['PRICE_M15']['proxy_flag']=='true'
 assert 'PRICE_C05' in reg['PRICE_M15']['notes'] and 'PRICE_C08' in reg['PRICE_M15']['notes'] and 'PRICE_M12' in reg['PRICE_M15']['notes']
 assert reg['NODE_S1']['source_url']=='https://www.geonames.org/'
 assert all(reg[k]['source_url'] for k in reg if k.startswith(('STAT_','PRICE_','RENT_')))

def test_source_verification_status_enum_and_no_workbook_copy():
 allowed={'verified_exact','verified_metadata_only','verified_page_but_value_unavailable','blocked','dead_link','content_changed','pending_manual_review'}
 reg=read(ROOT/'metadata/source_recovery_register.csv'); assert all(x['verification_status'] in allowed for x in reg)
 assert not list(ROOT.rglob('长三角钢材配送案例_公开数据校准包_v2.xlsx'))

def test_statistical_source_verification_counts_and_urls():
 reg={x['source_record_id']:x for x in read(ROOT/'metadata/source_recovery_register.csv') if x['source_record_id'].startswith('STAT_')}
 assert len(reg)==15 and all(x['verification_status'] for x in reg.values())
 from collections import Counter
 assert Counter(x['verification_status'] for x in reg.values())==Counter({'verified_exact':14,'verified_metadata_only':0,'pending_manual_review':1})
 assert reg['STAT_M09']['source_url']=='https://www.changzhou.gov.cn/gi_news/618174366821577'
 assert reg['STAT_M09']['verification_status']=='verified_exact'
 assert reg['STAT_M09']['verification_evidence_type']=='original_official_page_exact_match'
 assert reg['STAT_C08']['source_url']=='https://tjj.jiaxing.gov.cn/module/download/downfile.jsp?classid=0&filename=78c3082538704b178ee0a1f21d20f0d1.pdf'
 assert all(x['verification_checked_at']=='2026-08-02' for x in reg.values())
 assert all(x['recovered_value'] for x in reg.values())

def test_price_source_verification_and_midpoint_disclosure():
 reg={x['source_record_id']:x for x in read(ROOT/'metadata/source_recovery_register.csv') if x['source_record_id'].startswith('PRICE_')}
 assert len(reg)==15 and all(x['verification_status'] for x in reg.values())
 assert reg['PRICE_M15']['proxy_flag']=='true'
 assert all(k in reg['PRICE_M15']['notes'] for k in ('PRICE_C05','PRICE_C08','PRICE_M12'))
 assert 'Jinhua value is a geographic proxy constructed from Hangzhou, Jiaxing and Shaoxing screening observations' in reg['PRICE_M15']['verification_note']
 assert reg['PRICE_C08']['source_url']=='https://m.steelx2.com/news-content.aspx?id=643704'
 from collections import Counter
 assert Counter(x['verification_status'] for x in reg.values())==Counter({'verified_exact':6,'verified_page_but_value_unavailable':3,'content_changed':0,'pending_manual_review':6})
 for k in ('PRICE_C03','PRICE_C06','PRICE_C08','PRICE_M09','PRICE_M10','PRICE_M11'):
  assert reg[k]['verification_status']=='verified_exact'
 assert reg['PRICE_C03']['verification_evidence_type']=='search_indexed_historical_snapshot'
 assert reg['PRICE_M09']['verification_evidence_type']=='historical_range_midpoint'
 assert reg['PRICE_M11']['verification_evidence_type']=='historical_range_midpoint'
 assert '(3310 + 3370) / 2 = 3340' in reg['PRICE_C04']['notes']
 assert '(3240 + 3290) / 2 = 3265' in reg['PRICE_M09']['notes']
 assert '(3190 + 3290) / 2 = 3240' in reg['PRICE_M11']['notes']
 assert all(x['verification_checked_at']=='2026-08-02' for x in reg.values())

def test_rent_source_verification_and_unit_conversions():
 reg={x['source_record_id']:x for x in read(ROOT/'metadata/source_recovery_register.csv') if x['source_record_id'].startswith('RENT_')}
 from collections import Counter
 assert len(reg)==8
 assert Counter(x['verification_status'] for x in reg.values())==Counter({'verified_exact':6,'pending_manual_review':2})
 for k in ('RENT_C01','RENT_C03','RENT_C04','RENT_C05','RENT_C06','RENT_C08'):
  assert reg[k]['verification_status']=='verified_exact'
 for k in ('RENT_C02','RENT_C07'):
  assert reg[k]['verification_status']=='pending_manual_review'
 assert 'specific listing' in reg['RENT_C02']['observation_type'].lower()
 assert 'specific high-standard listing' in reg['RENT_C07']['observation_type'].lower()
 assert reg['RENT_C03']['source_url']=='https://su.58.com/cangku/'
 assert reg['RENT_C03']['verification_evidence_url']=='https://su.58.com/fangjia/cangkuzujin/'
 assert reg['RENT_C01']['verification_evidence_type']=='official_market_report_exact_match'
 assert all(x['verification_checked_at']=='2026-08-02' for x in reg.values())
 assert all(x['recovered_value'] for x in reg.values())
 daily={'C03':0.75,'C04':0.66,'C05':0.70,'C06':0.74,'C08':0.50}
 for did, value in daily.items(): assert abs(float(reg['RENT_'+did]['recovered_value'])-value*30)<1e-9

def test_offline_data_quality_audit_is_reproducible_and_non_mutating():
 import hashlib,subprocess,sys
 files=('case_config.json','dc_emission_params.csv','dc_market.csv','dc_params.csv','inventory_params.csv','market_params.csv','nodes.csv','supplier_dc.csv')
 def hashes(): return {f:hashlib.sha256((ROOT/'data/processed/v0.1.0-preview'/f).read_bytes()).hexdigest() for f in files}
 before=hashes(); q=subprocess.run([sys.executable,str(ROOT/'scripts/audit_data_quality.py')],capture_output=True,text=True); assert q.returncode==0,q.stderr
 audit=read(ROOT/'metadata/data_quality_audit.csv'); assert audit and all(x['status'] in {'passed','warning','failed'} for x in audit); assert not any(x['status']=='failed' for x in audit)
 assert all((x['severity']=='warning')==(x['status']=='warning') for x in audit)
 allowed={'DST-003','WARN-001','WARN-002','WARN-003','WARN-004','WARN-005'}
 assert all(x['check_id'] in allowed for x in audit if x['status']=='warning')
 assert {x['record_id'] for x in audit if x['check_id']=='DST-003'}=={f'C0{i}|C0{i}' for i in range(1,9)}
 assert any(x['check_id']=='LIN-002' and x['status']=='passed' for x in audit)
 assert all(any(x['check_id']==k and x['status']=='passed' for x in audit) for k in ('LIN-002','LIN-003','LIN-004','LIN-005','LIN-006','LIN-007','LIN-008','CFG-001','EMI-001','EMI-002','SCH-001'))
 first=(ROOT/'metadata/data_quality_audit.csv').read_bytes(); q=subprocess.run([sys.executable,str(ROOT/'scripts/audit_data_quality.py')],capture_output=True,text=True); assert q.returncode==0,q.stderr; assert first==(ROOT/'metadata/data_quality_audit.csv').read_bytes()
 assert before==hashes(); assert len(read(ROOT/'metadata/record_lineage.csv'))==918
