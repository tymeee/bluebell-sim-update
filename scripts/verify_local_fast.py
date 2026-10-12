"""Start a warmed local backend, run real HTTP burst tests, then shut it down.

Needs >= 8 GB available memory for the shared banks; 16 GB is recommended in
production. Runs one API process with the requested compute thread count.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
import httpx

parser=argparse.ArgumentParser()
parser.add_argument('--workers',type=int,default=8)
parser.add_argument('--users',type=int,default=30)
parser.add_argument('--rounds',type=int,default=3)
parser.add_argument('--port',type=int,default=8765)
parser.add_argument('--output-dir',default='verification-results')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
outdir=Path(args.output_dir).resolve(); outdir.mkdir(parents=True,exist_ok=True)
env=os.environ.copy()
env.update(SIMULATOR_SHARED_SCENARIOS='1',SIMULATOR_WORKERS=str(args.workers),
           OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
url=f'http://127.0.0.1:{args.port}'
passed=True
with (outdir/'backend.log').open('w') as log:
    server=subprocess.Popen([sys.executable,'-m','uvicorn','simulator_api:app',
        '--host','127.0.0.1','--port',str(args.port),'--workers','1'],cwd=root,
        stdout=log,stderr=log,env=env)
    try:
        started=time.perf_counter()
        with httpx.Client(trust_env=False,timeout=2) as client:
            while time.perf_counter()-started<240:
                if server.poll() is not None:
                    raise RuntimeError('Backend exited; inspect backend.log')
                try:
                    response=client.get(url+'/health')
                    if response.status_code==200:
                        print(f'Ready after {time.perf_counter()-started:.2f}s: {response.json()}',flush=True)
                        break
                except httpx.HTTPError:
                    pass
                time.sleep(.5)
            else:
                raise RuntimeError('Backend did not become ready within 240 seconds.')
        for model in ('index','funds'):
            check=subprocess.run([sys.executable,str(root/'scripts/load_test_fast.py'),url,
                '--no-proxy','--users',str(args.users),'--rounds',str(args.rounds),
                '--model',model,'--output',str(outdir/f'load-{model}-{args.users}.json')],cwd=root,env=env)
            passed=passed and check.returncode==0
    finally:
        server.terminate()
        try: server.wait(timeout=20)
        except subprocess.TimeoutExpired:
            server.kill(); server.wait()
raise SystemExit(0 if passed else 1)
