"""Offline sensitivity analysis for the eight same-city zero-distance arcs."""
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/processed/v0.1.0-preview'; OUT=ROOT/'metadata/intracity_zero_distance_sensitivity.csv'; DOC=ROOT/'docs/intracity_zero_distance_sensitivity.md'
def read(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def main():
    cfg=json.loads((ROOT/'config/baseline.json').read_text(encoding='utf-8')); markets={r['market_id']:r for r in read(P/'market_params.csv')}; arcs=[r for r in read(P/'dc_market.csv') if r['dc_id']==r['market_id']]; assert len(arcs)==8
    distances=[0,5,10,15,20,30]; fields=['dc_id','market_id','city','current_distance_km','candidate_distance_km','annual_demand_tonnes','transport_rate_cny_per_tonne_km','transport_emission_factor_tco2e_per_tonne_km','cost_cny_per_tonne','emission_tco2e_per_tonne','delta_cost_cny_per_tonne','delta_emission_tco2e_per_tonne','annual_cost_if_all_local_demand_served','annual_emission_if_all_local_demand_served','delta_annual_cost','delta_annual_emission']; rows=[]
    for a in arcs:
        demand=float(markets[a['market_id']]['mu_annual_tonnes']); city=markets[a['market_id']]['city']
        for d in distances:
            cost=d*cfg['transport_rate_cny_per_tonne_km']; em=d*cfg['transport_emission_factor_tco2e_per_tonne_km']; rows.append({'dc_id':a['dc_id'],'market_id':a['market_id'],'city':city,'current_distance_km':float(a['road_distance_km']),'candidate_distance_km':d,'annual_demand_tonnes':demand,'transport_rate_cny_per_tonne_km':cfg['transport_rate_cny_per_tonne_km'],'transport_emission_factor_tco2e_per_tonne_km':cfg['transport_emission_factor_tco2e_per_tonne_km'],'cost_cny_per_tonne':cost,'emission_tco2e_per_tonne':em,'delta_cost_cny_per_tonne':cost,'delta_emission_tco2e_per_tonne':em,'annual_cost_if_all_local_demand_served':demand*cost,'annual_emission_if_all_local_demand_served':demand*em,'delta_annual_cost':demand*cost,'delta_annual_emission':demand*em})
    with OUT.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    lines=['# Intracity zero-distance sensitivity analysis','','Offline, non-destructive analysis only. Candidate distances are not written to processed data or model inputs.','',f"Arcs analysed: {', '.join(a['dc_id']+'|'+a['market_id'] for a in arcs)}",'','| Candidate distance (km) | Aggregate annual cost increment (CNY) | Aggregate annual emission increment (tCO2e) |','|---:|---:|---:|']
    for d in distances:
        sub=[r for r in rows if r['candidate_distance_km']==d]; lines.append(f"| {d} | {sum(r['delta_annual_cost'] for r in sub):,.2f} | {sum(r['delta_annual_emission'] for r in sub):,.6f} |")
    lines += ['', '## Interpretation','', 'The values are scale calculations assuming all local annual demand is served by the corresponding same-city DC. They are not an optimization assignment.','', 'The largest annual impacts are associated with the markets having the largest annual demand, especially Suzhou, Shanghai, and Ningbo under the same candidate distance.','', '## Treatment options','', '**A. Retain 0 km:** valid only if the model explicitly excludes intra-city last-mile delivery.','', '**B. Apply a common lower bound:** requires public evidence or a robustness study; this analysis does not recommend a particular distance.','', '**C. Use representative DC and market coordinates:** more realistic, but requires collecting logistics-park/warehouse coordinates and recomputing the road network distances.','', 'No option is recommended here; the sensitivity table is provided to make the assumption transparent.']
    DOC.write_text('\n'.join(lines)+'\n',encoding='utf-8'); print(json.dumps({'records':len(rows),'arcs':len(arcs),'distances':distances}))
if __name__=='__main__':main()
