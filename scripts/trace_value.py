import argparse,csv,json,sys
from pathlib import Path
def rd(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--file',required=True);ap.add_argument('--record',required=True);ap.add_argument('--column',required=True);ap.add_argument('--format',choices=['text','json'],default='text');a=ap.parse_args();root=Path(__file__).resolve().parents[1];p=root/'data/processed/v0.1.0-preview'/a.file
 if not p.exists():print('ERROR: file not found',file=sys.stderr);return 2
 if p.suffix=='.json':
  obj=json.loads(p.read_text());
  if a.column not in obj:print('ERROR: field not found',file=sys.stderr);return 2
  result={'output':{'file':a.file,'record_id':'case_config','column':a.column,'value':obj[a.column],'unit':'configuration'},'lineage_role':'scenario','source_records':[],'source_catalog':[],'transformations':[{'transformation_id':'T_CONFIG_MAPPING_001'}],'scenarios':[{'scenario_id':'SCENARIO_ASSUMPTION'}],'parent_inputs':[],'verification_status':'documented','unresolved_provenance':['carbon quota not generated'] if a.column=='carbon_quota' else []}
 else:
  rows=rd(p);key=next((x for x in ('market_id','dc_id','supplier_id','node_id') if x in rows[0]),None);r=next((x for x in rows if x.get(key)==a.record),None)
  if r is None and '|' in a.record:
   d,m=a.record.split('|',1);r=next((x for x in rows if x.get('dc_id')==d and x.get('market_id')==m),None)
  if r is None or a.column not in r:print('ERROR: record or field not found',file=sys.stderr);return 2
  rec=(r.get('supplier_id')+'|'+r.get('dc_id') if a.file=='supplier_dc.csv' else r.get('dc_id')+'|'+r.get('market_id') if a.file=='dc_market.csv' else r.get(key)); ls=[x for x in rd(root/'metadata/record_lineage.csv') if x['output_file']==a.file and x['output_record_id']==rec and x['output_column']==a.column]
  if not ls:print('ERROR: lineage not found',file=sys.stderr);return 3
  sources={x['source_record_id']:x for x in rd(root/'data/source_records/source_records.csv')};catalog={x['source_id']:x for x in rd(root/'metadata/source_catalog.csv')};trans={x['transformation_id']:x for x in rd(root/'metadata/transformation_registry.csv')};sc={x['scenario_id']:x for x in rd(root/'metadata/scenario_registry.csv')};result={'output':{'file':a.file,'record_id':rec,'column':a.column,'value':r[a.column],'unit':ls[0]['output_unit']},'lineage_role':ls[0]['lineage_role'],'source_records':[sources[x['source_record_id']] for x in ls if x['source_record_id'] in sources],'source_catalog':[catalog[sources[x['source_record_id']]['source_id']] for x in ls if x['source_record_id'] in sources and sources[x['source_record_id']]['source_id'] in catalog],'transformations':[trans[x['transformation_id']] for x in ls if x['transformation_id'] in trans],'scenarios':[sc[z] for x in ls for z in x['scenario_id'].split('|') if z in sc],'parent_inputs':[json.loads(x['parent_input_ids']) for x in ls],'verification_status':ls[0]['verification_status'],'unresolved_provenance':['external source verification pending'] if ls[0]['verification_status']!='documented' else []}
 if a.format=='json':print(json.dumps(result,ensure_ascii=False,indent=2))
 else:
  print(f"File: {result['output']['file']}\nRecord: {result['output']['record_id']}\nColumn: {result['output']['column']}\nValue: {result['output']['value']}\nUnit: {result['output']['unit']}\nRole: {result['lineage_role']}\nSources: {len(result['source_records'])}\nTransformations: {len(result['transformations'])}\nScenarios: {len(result['scenarios'])}\nParents: {result['parent_inputs']}")
 return 0
if __name__=='__main__':sys.exit(main())
