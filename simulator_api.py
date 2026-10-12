"""Run: uvicorn simulator_api:app --host 0.0.0.0 --port 8000 --workers 1.

One API process owns one bounded native-compute thread pool. Do not multiply
Uvicorn workers and compute pools without accounting for CPU and memory.
"""
import os
# Set before NumPy imports to prevent each request spawning a BLAS thread team.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import logging
import secrets
from threading import BoundedSemaphore
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fast_simulator.engine import simulate, warmup
from fast_simulator.runtime import available_cpus
from fast_simulator.schema import SimulationRequest

logger = logging.getLogger(__name__)
WORKERS = int(os.getenv('SIMULATOR_WORKERS', str(available_cpus())))
MAX_INFLIGHT = int(os.getenv('SIMULATOR_MAX_INFLIGHT', '64'))
if WORKERS < 1 or MAX_INFLIGHT < WORKERS:
    raise ValueError('SIMULATOR_WORKERS must be positive; MAX_INFLIGHT must be >= workers.')
API_KEY = os.getenv('SIMULATOR_API_KEY', '')
slots = BoundedSemaphore(MAX_INFLIGHT)

@asynccontextmanager
async def lifespan(app):
    warmup()
    app.state.banks = None
    if os.getenv('SIMULATOR_SHARED_SCENARIOS', '0') == '1':
        from fast_simulator.scenarios import build_banks, warm_cached
        logger.info('Preparing shared scenarios; readiness remains false until complete.')
        app.state.banks = build_banks(int(os.getenv('SIMULATOR_SCENARIO_SEED', '20261012')))
        warm_cached(app.state.banks)
    app.state.pool = ThreadPoolExecutor(max_workers=WORKERS, thread_name_prefix='simulation')
    app.state.ready = True
    logger.info('Simulation service ready: %s compute workers, %s admitted requests.', WORKERS, MAX_INFLIGHT)
    try:
        yield
    finally:
        app.state.ready = False
        app.state.pool.shutdown(wait=True, cancel_futures=True)

app = FastAPI(title='BlueBridge Simulation API', version='1.0.0', lifespan=lifespan)
origins = [v.strip() for v in os.getenv('SIMULATOR_CORS_ORIGINS', '').split(',') if v.strip()]
if origins:
    app.add_middleware(CORSMiddleware, allow_origins=origins,
                       allow_methods=['POST', 'GET'], allow_headers=['Content-Type', 'X-API-Key'])

@app.get('/health')
async def health():
    if not getattr(app.state, 'ready', False):
        raise HTTPException(503, 'Service is warming up.')
    return {'status': 'ready', 'compute_workers': WORKERS, 'max_inflight': MAX_INFLIGHT,
            'sampling_mode': 'shared_scenarios' if app.state.banks is not None else 'fresh'}

@app.post('/api/simulate')
async def run(request: SimulationRequest, x_api_key: str | None = Header(default=None)):
    if API_KEY and not secrets.compare_digest(x_api_key or '', API_KEY):
        raise HTTPException(401, 'Invalid API key.')
    if not getattr(app.state, 'ready', False):
        raise HTTPException(503, 'Service is warming up.')
    if app.state.banks is not None and request.seed is not None and os.getenv('SIMULATOR_ALLOW_FRESH', '0') != '1':
        raise HTTPException(422, 'This service uses shared scenarios. Omit seed, or enable fresh runs on a separate service.')
    if not slots.acquire(blocking=False):
        raise HTTPException(429, 'Simulation capacity is full. Please retry shortly.', headers={'Retry-After':'2'})
    import time
    submitted = time.perf_counter()
    try:
        future = app.state.pool.submit(simulate, request, app.state.banks)
    except Exception:
        slots.release()
        raise
    # Hold admission even if the HTTP client disconnects; native work cannot be killed safely.
    future.add_done_callback(lambda _: slots.release())
    try:
        result = await asyncio.shield(asyncio.wrap_future(future))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:
        logger.exception('Simulation failed')
        raise HTTPException(500, 'Simulation failed; consult server logs.') from exc
    result['server_seconds'] = time.perf_counter() - submitted
    return result
