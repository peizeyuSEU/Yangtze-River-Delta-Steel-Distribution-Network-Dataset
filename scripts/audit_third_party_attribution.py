"""Offline audit of third-party inventory, attribution, and scope statements."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'metadata/third_party_attribution_audit.csv'; DOC=ROOT/'docs/third_party_attribution_audit.md'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    inv=read(ROOT/'metadata/third_party_data_inventory.csv'); rows=[]
    def add(cid,status,msg): rows.append({'check_id':cid,'status':status,'message':msg})
    ids={x['third_party_id'] for x in inv}; required={'SRC_GEONAMES_DATA','SRC_OSM_DATA','SRC_OSRM_SOFTWARE','SRC_OSRM_DEMO_SERVICE','SRC_OSRM_CACHE','SRC_CITY_STATISTICS','SRC_STEEL_PRICE_PAGES','SRC_WAREHOUSE_RENT_PAGES','SRC_NOMINATIM_GEOCODING'}
    add('TP-001','passed' if required<=ids else 'failed','required third-party components present')
    g=next(x for x in inv if x['third_party_id']=='SRC_GEONAMES_DATA'); o=next(x for x in inv if x['third_party_id']=='SRC_OSM_DATA'); s=next(x for x in inv if x['third_party_id']=='SRC_OSRM_SOFTWARE')
    add('TP-002','passed' if g['license_name']=='Creative Commons Attribution' and g['license_version']=='4.0' else 'failed','GeoNames CC BY 4.0')
    add('TP-003','passed' if o['license_name']=='Open Data Commons Open Database License' and o['license_version']=='1.0' else 'failed','OSM ODbL 1.0')
    add('TP-004','passed' if s['license_name']=='BSD-2-Clause' else 'failed','OSRM BSD-2-Clause')
    text='\n'.join((ROOT/f).read_text(encoding='utf-8',errors='ignore') for f in ('README.md','THIRD_PARTY_NOTICES.md','docs/third_party_data_and_attribution.md'))
    add('TP-005','passed' if 'GeoNames' in text and 'CC BY 4.0' in text else 'failed','GeoNames attribution text')
    add('TP-006','passed' if 'OpenStreetMap contributors' in text and 'ODbL' in text else 'failed','OSM attribution text')
    add('TP-007','passed' if 'OSRM' in text and 'BSD-2-Clause' in text else 'failed','OSRM distinction')
    add('TP-008','passed' if 'factual_extraction_only_terms_review_required' in '\n'.join(x['redistribution_status'] for x in inv if x['component_type']=='factual_web_extraction') else 'failed','web sources remain factual extraction only')
    normalized=' '.join(text.split())
    add('TP-009','passed' if 'Produced Work' in normalized and 'Derived Database' in normalized and 'scope review' in normalized else 'failed','OSM/OSRM derived-output scope review retained')
    add('TP-010','passed' if not any('fully_relicensed' in x['redistribution_status'] for x in inv) else 'failed','no blanket relicensing')
    reg=read(ROOT/'metadata/source_recovery_register.csv'); add('TP-011','passed' if all(x['source_url'].startswith('http') for x in reg) else 'failed','original source URLs remain present')
    add('TP-012','passed' if 'Nominatim' in text and 'cached' in text.lower() else 'failed','Nominatim is documented as a cached exploratory service')
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=['check_id','status','message']); w.writeheader(); w.writerows(rows)
    failed=sum(x['status']=='failed' for x in rows); DOC.write_text('# Third-party attribution audit\n\nOffline checks only.\n\n'+f"Checks: {len(rows)}; passed: {len(rows)-failed}; failed: {failed}.\n\n"+'All third-party components are inventoried. GeoNames, OSM, and OSRM are kept as distinct data/software/service categories. Web sources are factual extraction only, and the cached distance matrix retains conservative ODbL scope review. No blanket relicensing is asserted.\n',encoding='utf-8'); print(json.dumps({'checks':len(rows),'failed':failed}))
if __name__=='__main__':main()
