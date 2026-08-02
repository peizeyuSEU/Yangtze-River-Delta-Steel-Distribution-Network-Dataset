"""Explicit one-time Nominatim geocoder for v0.2 candidate DCs.

This script is intentionally not imported by build, tests, CI, or audit scripts.
It performs only a small, cached, single-threaded query set. Reviewers may pass
--accept DC:INDEX after inspecting cached results; without --accept it never
writes coordinates into the candidate register.
"""
import argparse,csv,json,time,urllib.parse,urllib.request
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REG=ROOT/'metadata/v0.2_candidate_dc_locations.csv'; CACHE=ROOT/'data/cache/v0.2-candidate/geocoding'; LOG=ROOT/'metadata/v0.2_candidate_geocoding_log.csv'
UA='Yangtze-River-Delta-Steel-Distribution-Network-Dataset/0.2-candidate (https://github.com/peizeyuSEU/Yangtze-River-Delta-Steel-Distribution-Network-Dataset)'
QUERIES={
 'C01':['外高桥物流园区二期 上海','外高桥物流园区二期 港建路 上海','外高桥物流园区 上海 高东镇'],
 'C02':['南京龙潭综合物流园','龙潭综合物流园 疏港大道 南京','南京龙潭港 综合物流园'],
 'C03':['普洛斯苏州望亭物流园 海盛路75号','苏州市相城区海盛路75号','苏州市相城区海盛路68号'],
 'C04':['无锡西站物流园','无锡国家物流枢纽供应链基地','锡西大道 新长铁路 无锡 惠山区'],
 'C05':['杭州传化公路港','传化公路港 萧山区 宁围街道','传化物流公路港 杭州 萧山'],
 'C06':['宁波栎社保税物流中心 聚才路99号','宁波市海曙区聚才路99号','宁波空港物流园区 聚才路99号'],
 'C07':['派河国际综合物流园公共物流中心','合肥派河物流园 莲花路 疏港大道','合肥经济技术开发区 莲花路 疏港大道 物流中心'],
 'C08':['嘉兴现代物流园 王店','嘉兴现代物流园 吉蚂西路','嘉兴市秀洲区王店镇 现代物流园'],}
FIELDS=['dc_id','query_order','query_text','request_url_without_sensitive_data','request_timestamp','response_cache_path','result_count','selected_result_index','selected_display_name','selected_latitude','selected_longitude','selected_osm_type','selected_osm_id','selected_category','selected_type','acceptance_status','acceptance_reason','reviewer_note']
ALLOWED={'accepted_exact_address','accepted_named_poi','accepted_within_official_boundary','rejected_city_level_result','rejected_road_only_result','rejected_wrong_facility','rejected_outside_boundary','ambiguous','no_result'}
def readreg():
 with REG.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def get_json(q,dc,order):
 CACHE.mkdir(parents=True,exist_ok=True); p=CACHE/f'{dc}_query_{order:02d}.json'
 if p.exists(): return json.loads(p.read_text(encoding='utf-8')),'cached',p
 params=urllib.parse.urlencode({'q':q,'format':'jsonv2','addressdetails':'1','limit':'5','accept-language':'en'})
 url='https://nominatim.openstreetmap.org/search?'+params
 req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
 with urllib.request.urlopen(req,timeout=5) as resp: data=json.load(resp)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); time.sleep(1.1); return data,url,p
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--accept',action='append',default=[],help='DC:result_index (1-based), only after manual review'); args=ap.parse_args(); accepts={x.split(':',1)[0]:int(x.split(':',1)[1]) for x in args.accept}
 rows=[]
 for dc,qs in QUERIES.items():
  for i,q in enumerate(qs,1):
   try: data,source,p=get_json(q,dc,i); err=''
   except Exception as e: data=[];source='error';p=CACHE/f'{dc}_query_{i:02d}.json';err=str(e); p.write_text(json.dumps({'error':err,'query':q},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   selected=accepts.get(dc); item=data[selected-1] if selected and 0<selected<=len(data) else None
   status='ambiguous' if data else 'no_result'; reason='Manual selection required; inspect cached result.' if data else 'No Nominatim result.'
   if item: status='accepted_named_poi'; reason='Accepted only by explicit --accept after manual review.'
   rows.append({'dc_id':dc,'query_order':i,'query_text':q,'request_url_without_sensitive_data':'https://nominatim.openstreetmap.org/search','request_timestamp':datetime.now(timezone.utc).isoformat(),'response_cache_path':str(p.relative_to(ROOT)).replace('\\','/'),'result_count':len(data),'selected_result_index':selected or '','selected_display_name':item.get('display_name','') if item else '','selected_latitude':item.get('lat','') if item else '','selected_longitude':item.get('lon','') if item else '','selected_osm_type':item.get('osm_type','') if item else '','selected_osm_id':item.get('osm_id','') if item else '','selected_category':item.get('category','') if item else '','selected_type':item.get('type','') if item else '','acceptance_status':status,'acceptance_reason':reason,'reviewer_note':err or ('Cached response' if source=='cached' else 'Fresh response; manual review required.')})
 with LOG.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
 print(json.dumps({'queries':len(rows),'cache_files':len(list(CACHE.glob('*.json'))),'accepted':sum(bool(x['selected_result_index']) for x in rows)}))
if __name__=='__main__':main()
