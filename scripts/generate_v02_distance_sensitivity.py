"""Generate five offline intracity distance scenario summaries."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; V01=ROOT/'data/processed/v0.1.0-preview'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
 cfg=json.loads((V01/'case_config.json').read_text()); rates=cfg['transport_rate_cny_per_tonne_km']; ef=cfg['transport_emission_factor_tco2e_per_tonne_km']; demand={r['market_id']:float(r['mu_annual_tonnes']) for r in read(V01/'market_params.csv')}; rows=[]
 for km in (0,5,10,15,20):
  for i in range(1,9):
   aid=f'C{i:02d}|C{i:02d}'; annual=demand[f'C{i:02d}']; rows.append({'scenario_km':km,'arc_id':aid,'old_distance_km':0,'new_distance_km':km,'annual_demand_tonnes':annual,'unit_transport_cost_change':km*rates,'annual_transport_cost_upper_bound':annual*km*rates,'annual_transport_emission_upper_bound':annual*km*ef,'source_type':'researcher_defined_scenario_parameter'})
 with (ROOT/'metadata/intracity_distance_sensitivity_summary.csv').open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
 (ROOT/'docs/intracity_distance_sensitivity_report.md').write_text('# Intracity distance sensitivity\n\nFive offline scenarios (0, 5, 10, 15, 20 km) are evaluated as arithmetic upper bounds for the eight same-city arcs. They do not run the optimization model or claim that all local demand is assigned to the same-city DC. The 10 km scenario is the v0.2 candidate baseline.\n',encoding='utf-8'); print(json.dumps({'rows':len(rows),'scenarios':[0,5,10,15,20]}))
if __name__=='__main__':main()
