"""Offline validator for externally generated carbon-quota artifacts."""
import json,math,re,sys
from pathlib import Path
REQ=json.loads((Path(__file__).resolve().parents[1]/'metadata/carbon_quota_artifact_schema.json').read_text())['required']
ALLOWED={'optimal','feasible','complete','validated'}
def validate(path):
    d=json.loads(Path(path).read_text(encoding='utf-8'))
    if d.get('_example_only') or any(v=='REPLACE_WITH_MODEL_OUTPUT' for v in d.values() if isinstance(v,str)): raise ValueError('example or placeholder is not a formal artifact')
    missing=[k for k in REQ if k not in d or d[k] in ('',None)]
    if missing: raise ValueError('missing fields: '+','.join(missing))
    for k in ('e0_value','quota_multiplier','carbon_quota_value'):
        if not isinstance(d[k],(int,float)) or isinstance(d[k],bool) or not math.isfinite(d[k]) or d[k]<0: raise ValueError(k+' must be finite nonnegative')
    if d['solver_status'] not in ALLOWED: raise ValueError('invalid solver_status')
    for k in ('e0_unit','quota_rule','carbon_quota_unit','dataset_commit','model_commit'):
        if not str(d[k]).strip(): raise ValueError(k+' is empty')
    for k in ('processed_manifest_sha256',):
        if not re.fullmatch(r'[0-9a-fA-F]{64}',str(d[k])): raise ValueError(k+' is not a sha256')
    return True
if __name__=='__main__':
    if len(sys.argv)!=2: print('usage: python scripts/validate_carbon_quota_artifact.py artifact.json'); sys.exit(2)
    try: validate(sys.argv[1]); print('valid formal carbon-quota artifact')
    except Exception as e: print('invalid:',e); sys.exit(1)
