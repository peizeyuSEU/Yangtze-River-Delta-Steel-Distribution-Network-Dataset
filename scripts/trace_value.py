import argparse,csv,json,sys
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--file',required=True);ap.add_argument('--record',required=True);ap.add_argument('--column',required=True);ap.add_argument('--format',choices=['text','json'],default='text');a=ap.parse_args();root=Path(__file__).resolve().parents[1];p=root/'data/processed/v0.1.0-preview'/a.file
 if not p.exists(): print('ERROR: file not found',file=sys.stderr); return 2
 if p.suffix=='.json': value=json.loads(p.read_text()); result={'file':a.file,'record_id':a.record,'column':a.column,'value':value.get(a.column),'unit':'configuration','lineage_role':'scenario','caveats':'carbon quota not generated'}
 else:
  with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
  if not rows or a.column not in rows[0]: print('ERROR: field not found',file=sys.stderr);return 2
  key=next((x for x in ('market_id','dc_id','supplier_id','node_id') if x in rows[0]),None);r=next((x for x in rows if x.get(key)==a.record),None)
  if r is None and '-' in a.record:
   d,m=a.record.split('-',1);r=next((x for x in rows if x.get('dc_id')==d and x.get('market_id')==m),None)
  if r is None: print('ERROR: record not found',file=sys.stderr);return 2
  with (root/'metadata/record_lineage.csv').open(encoding='utf-8-sig',newline='') as f: ls=[x for x in csv.DictReader(f) if x['output_file']==a.file and x['output_record_id']==r.get(key) and x['output_column']==a.column]
  if not ls: print('ERROR: no lineage found',file=sys.stderr);return 3
  result={'file':a.file,'record_id':a.record,'column':a.column,'value':r[a.column],'unit':ls[0]['output_unit'],'lineage_role':ls[0]['lineage_role'],'lineage':ls,'caveats':'External source verification may remain pending.'}
 if a.format=='json':print(json.dumps(result,ensure_ascii=False,indent=2))
 else: print(f"File: {result['file']}\nRecord: {result['record_id']}\nColumn: {result['column']}\nValue: {result['value']}\nUnit: {result['unit']}\nLineage role: {result['lineage_role']}\nCaveats: {result['caveats']}")
 return 0
if __name__=='__main__':sys.exit(main())
