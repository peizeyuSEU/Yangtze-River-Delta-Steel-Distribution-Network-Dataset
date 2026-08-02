import csv,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def test_price_c04_m13_original_values_urls_and_statuses():
 r={x['source_record_id']:x for x in read(ROOT/'metadata/source_recovery_register.csv')}
 assert r['PRICE_C04']['recovered_value']=='3340'; assert r['PRICE_C04']['source_url']=='https://jiancai.m.mysteel.com/m/26060810/142E6539F044F562_abc.html'; assert r['PRICE_C04']['verification_status']=='verified_page_but_value_unavailable'; assert r['PRICE_C04']['verification_evidence_url']=='https://gc.m.mysteel.com/a/26060817/C38A23088455AAB4_abc.html'
 assert r['PRICE_M13']['recovered_value']=='3260'; assert r['PRICE_M13']['source_url']=='https://jiancai.m.mysteel.com/m/26061810/4CF8D81827E51286_abc.html'; assert r['PRICE_M13']['verification_status']=='verified_page_but_value_unavailable'; assert r['PRICE_M13']['verification_evidence_url']=='https://list1.mysteel.com/zhishi/hzjzgcjg97898.html'; assert 'Phi18-22' in r['PRICE_M13']['verification_note']
def test_price_counts_are_dynamic_and_values_unchanged():
 r=[x for x in read(ROOT/'metadata/source_recovery_register.csv') if x['source_record_id'].startswith('PRICE_')]; c={}
 for x in r:c[x['verification_status']]=c.get(x['verification_status'],0)+1
 assert c.get('verified_exact',0)==11 and c.get('verified_page_but_value_unavailable',0)==3 and c.get('pending_manual_review',0)==1 and c.get('content_changed',0)==0
 assert next(x for x in r if x['source_record_id']=='PRICE_C04')['recovered_value']=='3340'
def test_candidate_register_has_eight_cities_and_no_coordinates():
 rows=read(ROOT/'metadata/v0.2_candidate_dc_locations.csv'); assert len(rows)==8; assert {x['dc_id'] for x in rows}=={f'C{i:02d}' for i in range(1,9)}; assert all(x['official_source_url'].startswith('http') for x in rows); assert all(not x['latitude'] and not x['longitude'] for x in rows)
 assert all(x['coordinate_status']=='pending_manual_review' for x in rows)
def test_candidate_audit_offline_and_passes():
 q=subprocess.run([sys.executable,str(ROOT/'scripts/audit_v02_candidate_dc_locations.py')],capture_output=True,text=True); assert q.returncode==0; assert '"failed": 0' in q.stdout
 text=(ROOT/'scripts/audit_v02_candidate_dc_locations.py').read_text(); assert 'requests' not in text and 'urllib' not in text
def test_geocoding_run_is_explicit_cached_and_no_accepted_coordinates():
 rows=read(ROOT/'metadata/v0.2_candidate_geocoding_log.csv'); assert len(rows)==24; assert all(int(x['query_order'])<=3 for x in rows); assert all(x['acceptance_status'] in {'ambiguous','no_result'} for x in rows); assert all(not x['selected_latitude'] and not x['selected_longitude'] for x in rows)
 script=(ROOT/'scripts/geocode_v02_candidate_dc_locations.py').read_text(encoding='utf-8'); assert 'build_all' not in script and 'pytest' not in script and 'audit_v02' not in script
def test_candidate_metadata_c03_c07_corrections():
 r={x['dc_id']:x for x in read(ROOT/'metadata/v0.2_candidate_dc_locations.csv')}; assert '海盛路68号' in r['C03']['address_or_boundary'] and '75号' in r['C03']['address_or_boundary']; assert r['C03']['representative_point_method']=='exact_address'; assert '莲花路以西' in r['C07']['address_or_boundary'] and '疏港大道以北' in r['C07']['address_or_boundary']; assert r['C07']['representative_point_method']=='official_project_location'
def test_v01_manifest_and_processed_hashes_unchanged():
 m=json.loads((ROOT/'metadata/release_manifest.json').read_text()); assert m['processed_non_empty_values']==918 and m['lineage_rows']==918 and m['carbon_quota_status']=='not_yet_generated' and m['preview_release_ready'] is True and m['formal_release_ready'] is False and m['model_execution_ready'] is False
 assert len(read(ROOT/'metadata/record_lineage.csv'))==918
 expected={'case_config.json':'bec13b33d8b03c1cf3afbfd6a0c3a41b56389beece99eba489bfc985fbcf37a9','dc_emission_params.csv':'6e79e08b47a60e73b3b74a9ad70627d3300010b96df51bd00438c19c5b2cdcb8','dc_market.csv':'00190d18bbeacd733e055134bb9b5d8f59739fe41996f6b2527b89fb0a8a85db','dc_params.csv':'22655b8f599908f7c385357ce37d4436b7cef36c1015b378b07cf563dda0a6e0','inventory_params.csv':'2828559aa34824293ace2897fb9c026ca6fa984cb25648a24f0594a2df485944','market_params.csv':'dd5758fa17329afd91cc0fa1d40c8c0746ae80c23436ea795c98c8edf0f34710','nodes.csv':'959f7bc9ffac9cc98f97af13481f08c511baed3786b36b6dcf60e3fe340f63a4','supplier_dc.csv':'ec3e0f29d2ee934fc23b1480933b5e36cca4d008987b169b832df72772e49e61'}
 for fn,h in expected.items(): assert hashlib.sha256((ROOT/'data/processed/v0.1.0-preview'/fn).read_bytes()).hexdigest()==h
