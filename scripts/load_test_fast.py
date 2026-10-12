"""Load-test the deployed API with distinct maximum-horizon portfolios.

Exit 1 if any request fails or exceeds the selected server-response threshold.
HTTP timing includes queueing and transfers, but does not measure browser rendering.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import sys
import time
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fast_simulator.schema import INDEX_NAMES,FUND_NAMES

parser=argparse.ArgumentParser()
parser.add_argument('url')
parser.add_argument('--users',type=int,default=30)
parser.add_argument('--rounds',type=int,default=3)
parser.add_argument('--model',choices=['index','funds'],default='index')
parser.add_argument('--max-seconds',type=float,default=6)
parser.add_argument('--no-proxy',action='store_true',help='Ignore proxy environment variables, e.g. for localhost tests.')
parser.add_argument('--fresh',action='store_true',help='Explicit seeds bypass shared scenarios.')
parser.add_argument('--output',default='load-test-results.json')
args=parser.parse_args()

async def main():
    headers={'X-API-Key':os.environ['SIMULATOR_API_KEY']} if os.getenv('SIMULATOR_API_KEY') else {}
    records=[]
    async with httpx.AsyncClient(timeout=180,headers=headers,trust_env=not args.no_proxy,
        limits=httpx.Limits(max_connections=args.users,max_keepalive_connections=args.users)) as client:
        health=await client.get(args.url.rstrip('/')+'/health')
        health.raise_for_status()
        for round_number in range(args.rounds):
            event=asyncio.Event()
            async def run(i):
                names=INDEX_NAMES if args.model=='index' else FUND_NAMES
                weights={name:1/len(names) for name in names}
                payload=dict(model=args.model,age=0,years_until_retirement=20,
                    initial_amount=1_000_000+i*1000,monthly_contribution=10_000,
                    annual_withdrawal=0,simulations=1000,weights=weights,
                    seed=(round_number*args.users+i+1) if args.fresh else None)
                await event.wait()
                start=time.perf_counter()
                try:
                    response=await client.post(args.url.rstrip('/')+'/api/simulate',json=payload)
                    elapsed=time.perf_counter()-start
                    if response.status_code!=200:
                        return dict(round=round_number+1,user=i,status=response.status_code,seconds=elapsed,error=response.text[:300])
                    data=response.json()
                    return dict(round=round_number+1,user=i,status=200,seconds=elapsed,
                                engine_seconds=data['simulation_seconds'],server_seconds=data['server_seconds'])
                except Exception as exc:
                    return dict(round=round_number+1,user=i,status=0,seconds=time.perf_counter()-start,error=str(exc))
            tasks=[asyncio.create_task(run(i)) for i in range(args.users)]
            event.set()
            batch=await asyncio.gather(*tasks)
            records.extend(batch)
            print(f"Round {round_number+1}: maximum {max(r['seconds'] for r in batch):.3f}s; failures {sum(r['status']!=200 for r in batch)}",flush=True)
    passed=all(r['status']==200 and r['seconds']<=args.max_seconds for r in records)
    report=dict(passed=passed,threshold=args.max_seconds,users=args.users,rounds=args.rounds,
                model=args.model,measurement='HTTP response; browser rendering excluded',records=records)
    Path(args.output).write_text(json.dumps(report,indent=2))
    return 0 if passed else 1

if args.users<1 or args.rounds<1: parser.error('users and rounds must be positive')
raise SystemExit(asyncio.run(main()))
