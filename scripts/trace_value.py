import argparse,csv,json
from pathlib import Path
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--file',required=True);ap.add_argument('--record',required=True);ap.add_argument('--column',required=True);a=ap.parse_args();root=Path(__file__).resolve().parents[1];p=root/'data/processed/v0.1.0-preview'/a.file
 with p.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
 key='market_id' if 'market' in a.file else ('dc_id' if 'dc' in a.file else 'node_id');r=next(x for x in rows if x.get(key)==a.record);print(json.dumps({'file':a.file,'record':a.record,'column':a.column,'value':r.get(a.column),'lineage':str(root/'metadata/record_lineage.csv')},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
