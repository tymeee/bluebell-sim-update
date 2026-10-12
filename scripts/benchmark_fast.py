"""Warmed full-engine benchmark; reports actual observed timings, not projections."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fast_simulator.engine import simulate, warmup
from fast_simulator.schema import SimulationRequest, INDEX_NAMES, FUND_NAMES, PRESETS

parser=argparse.ArgumentParser()
parser.add_argument('--simulations',type=int,default=1000)
parser.add_argument('--age',type=int,default=0)
parser.add_argument('--users',type=int,default=1)
parser.add_argument('--workers',type=int,default=1)
parser.add_argument('--model',choices=['index','funds'],default='index')
parser.add_argument('--portfolio',choices=['all','balanced','cash'],default='all')
args=parser.parse_args()
warmup()
names=INDEX_NAMES if args.model=='index' else FUND_NAMES
weights={name:1/len(names) for name in names} if args.portfolio=='all' else (
    {'US Equity':.7,'Bond/Fixed Income Fund':.3} if args.model=='index' else PRESETS['Bluebell Balance'])
if args.portfolio=='cash': weights={}
base=dict(model=args.model,age=args.age,years_until_retirement=min(20,84-args.age),
          weights=weights,simulations=args.simulations,annual_withdrawal=0)
requests=[SimulationRequest(**base,seed=1000+i,initial_amount=1_000_000+i*1000) for i in range(args.users)]
start=time.perf_counter()
def run(req):
    result=simulate(req)
    return {'engine_seconds':result['simulation_seconds'],'completion_seconds':time.perf_counter()-start}
with ThreadPoolExecutor(max_workers=args.workers) as pool:
    results=list(pool.map(run,requests))
print(json.dumps({'settings':vars(args),'wall_seconds':time.perf_counter()-start,
                  'max_completion_seconds':max(r['completion_seconds'] for r in results),
                  'max_engine_seconds':max(r['engine_seconds'] for r in results),
                  'results':results},indent=2))
