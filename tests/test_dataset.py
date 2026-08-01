import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; P=ROOT/'data/processed/v0.1.0-preview'
def rows(n):
 with (P/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def test_counts(): assert len(rows('supplier_dc.csv'))==8 and len(rows('dc_market.csv'))==120
def test_demand(): assert abs(sum(float(x['demand_weight']) for x in rows('market_params.csv'))-1)<1e-5
def test_nonnegative():
 for n in ('supplier_dc.csv','dc_market.csv'):
  for r in rows(n): assert float(r['road_distance_km'])>=0 and float(r['transport_cost_baseline'])>=0
