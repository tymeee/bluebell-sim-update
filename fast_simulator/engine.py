"""Daily native simulation; only monthly paths survive each trial.

Request-local state and per-trial seeds allow concurrent calls without shared
random streams. No Streamlit imports, network access, or report generation.
"""
from functools import lru_cache
from pathlib import Path
import secrets
import time
import numpy as np
import pandas as pd
from numba import njit
from .kernels import index_path, fund_path, index_cached_path, fund_cached_path
from .schema import SimulationRequest, INDEX_NAMES, FUND_NAMES

DATA_DIR = Path(__file__).resolve().parents[1]
INDEX_COLUMNS = ['^GSPC', '^SET.BK', 'China', 'AGG', 'FDSVX', 'VWENX', 'VWIAX',
                 '^990100-USD-STRD', 'IXJ', 'IXN', 'IYR', 'EEM', '^DJGSP']
FUND_COLUMNS = ['ktp', 'gqg', 'eae', 'gtech', 'gnph', 'gcore', 'plus', 'cash',
                'kfa', 'ugi', 'healthcare', 'prop', 'sp500']
FEE_DRAG = (1 - np.array([.001, .002, .005, .001, .003, .003, .003,
                           .002, .002, .002, .002, .002, .002])) ** (1/252)
ROSTRUM_DAILY = (1 + (.126 + .13 + .139)/3) ** (1/252)

@lru_cache(maxsize=1)
def market_stats():
    data = pd.read_parquet(DATA_DIR / 'market_index.parquet')[INDEX_COLUMNS]
    data.index = pd.to_datetime(data.index)
    data = data.sort_index()
    result = []
    for start, end in [('2015-06-01', '2025-12-30'), ('2005-12-01', '2015-06-01')]:
        period = data.loc[start:end]
        cov = period.cov().to_numpy(dtype=np.float64)
        mean = period.mean().to_numpy(dtype=np.float64) - np.diag(cov)/2
        result.extend([mean, cov])
    return tuple(result)

@lru_cache(maxsize=1)
def fund_stats():
    # Match upstream: drop a row if any fund NAV is zero/missing, then log differences.
    nav = pd.read_csv(DATA_DIR / 'mutualfunds_data.csv')[FUND_COLUMNS]
    nav = nav.replace(0, np.nan).dropna()
    returns = np.log(nav / nav.shift(1)).dropna()
    mean = returns.mean().to_numpy(dtype=np.float64)
    cov = returns.cov().to_numpy(dtype=np.float64)
    fof_vol = float(pd.read_parquet(DATA_DIR / 'market_proxies.parquet')['fof'].std())
    return mean, cov, fof_vol

def covariance_factor(cov):
    if not np.isfinite(cov).all():
        raise ValueError('Market covariance contains non-finite values.')
    cov = (cov + cov.T) * .5
    if not len(cov):
        return np.empty((0, 0), dtype=np.float64)
    try:
        return np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        # Permit numerical zero eigenvalues; do not silently fix invalid model data.
        eig, vectors = np.linalg.eigh(cov)
        tolerance = max(float(np.max(np.abs(eig))) * 1e-10, 1e-14)
        if eig.min() < -tolerance:
            raise ValueError('Market covariance is not positive semidefinite.')
        return vectors * np.sqrt(np.maximum(eig, 0))[None, :]

@njit(cache=True, nogil=True)
def path_summary(path, retirement_day, initial, contribution):
    peak = 0.0
    drawdown = 0.0
    log_growth = 0.0
    valid = initial > 0 and retirement_day > 0
    previous = initial
    for day in range(len(path)):
        value = float(path[day])
        if value > peak:
            peak = value
        if peak > 0:
            drawdown = min(drawdown, value / peak - 1)
        if day < retirement_day:
            before_contribution = value - (contribution if day % 21 == 0 else 0.0)
            if previous <= 0 or before_contribution <= 0 or not np.isfinite(value):
                valid = False
            elif valid:
                log_growth += np.log(before_contribution / previous)
            previous = value
    annualized = np.expm1(log_growth * 252 / retirement_day) if valid else np.nan
    return drawdown, annualized, np.float64(path[min(retirement_day, len(path)-1)]), np.float64(path[-1])

@njit(cache=True, nogil=True)
def index_batch(n, duration, retirement_years, initial, contribution, withdrawal,
                target, weights, savings_weight, cash_weight, bull_mean, bear_mean,
                bull_factor, bear_factor, active, sample_days, seed, *extra):
    sampled = np.empty((len(sample_days), n), dtype=np.float32)
    summaries = np.empty((n, 4))
    failures = np.zeros(n, dtype=np.uint8)
    successes = np.zeros(n, dtype=np.uint8)
    stock_weights = weights[np.array([0, 1, 2, 7, 8, 9, 10, 11, 12])]
    for sim in range(n):
        np.random.seed((seed + sim * 2654435761) % 4294967296)
        maturity = np.random.randint(504, 2520)
        path, failed, success = index_path(
            retirement_years, duration, maturity, initial * weights,
            initial * savings_weight, initial * cash_weight, weights,
            contribution, savings_weight, (1.0175)**(1/252), withdrawal,
            .00011, cash_weight,
            0., 0., 0., 0., 0., 0.,
            (1.04)**(1/252), (1.05)**(1/252), (1.08)**(1/252),
            (1.045)**(1/252), (1.05)**(1/252), (1.08)**(1/252),
            stock_weights, weights[3], weights[4], weights[5], weights[6],
            target, bull_mean, bear_mean, bull_factor, bear_factor, active, FEE_DRAG)
        for j in range(len(sample_days)):
            sampled[j, sim] = path[sample_days[j]]
        summary = path_summary(path, retirement_years*252, initial, contribution)
        for k in range(4):
            summaries[sim, k] = summary[k]
        failures[sim] = failed
        successes[sim] = success
    return sampled, summaries, failures, successes

@njit(cache=True, nogil=True)
def fund_batch(n, duration, retirement_years, initial, contribution, withdrawal,
               target, weights, savings_weight, rostrum_weight, mean, factor,
               active, fof_vol, sample_days, seed, *extra):
    sampled = np.empty((len(sample_days), n), dtype=np.float32)
    summaries = np.empty((n, 4))
    failures = np.zeros(n, dtype=np.uint8)
    successes = np.zeros(n, dtype=np.uint8)
    for sim in range(n):
        np.random.seed((seed + sim * 2654435761) % 4294967296)
        amounts = initial * weights
        path, failed, success = fund_path(
            retirement_years, duration, contribution, withdrawal,
            amounts[1], amounts[6], amounts[7], amounts[8], amounts[9], amounts[3],
            amounts[2], amounts[0], initial*savings_weight, initial*rostrum_weight,
            amounts[4], amounts[10], amounts[11], amounts[12], amounts[5],
            weights[6], weights[7], weights[8], weights[9], weights[1], weights[3],
            weights[2], weights[0], savings_weight, rostrum_weight, weights[4],
            weights[10], weights[11], weights[12], weights[5], target,
            mean, factor, active, ROSTRUM_DAILY, fof_vol)
        for j in range(len(sample_days)):
            sampled[j, sim] = path[sample_days[j]]
        summary = path_summary(path, retirement_years*252, initial, contribution)
        for k in range(4):
            summaries[sim, k] = summary[k]
        failures[sim] = failed
        successes[sim] = success
    return sampled, summaries, failures, successes

def finite_number(value):
    return float(value) if np.isfinite(value) else None

def simulate(request: SimulationRequest | dict, scenario_banks=None):
    start = time.perf_counter()
    req = request if isinstance(request, SimulationRequest) else SimulationRequest.model_validate(request)
    cached = scenario_banks is not None and req.seed is None
    seed = scenario_banks.seed if cached else (req.seed if req.seed is not None else secrets.randbits(32))
    duration = (85 - req.age) * 252
    if cached:
        bank = scenario_banks.index if req.model == 'index' else scenario_banks.funds
        if req.simulations > bank.shape[0] or duration > bank.shape[1]:
            raise ValueError('Requested workload exceeds the prepared scenario bank.')
    retirement_day = req.years_until_retirement * 252
    # Include retirement exactly and the final day; chart storage does not alter daily rules.
    sample_days = np.unique(np.concatenate([np.arange(0, duration, 21),
                                            [retirement_day, duration-1]])).astype(np.int64)
    names = INDEX_NAMES if req.model == 'index' else FUND_NAMES
    weights = np.array([req.weights.get(name, 0) for name in names], dtype=np.float64)
    active = np.flatnonzero(weights > 0).astype(np.int64)
    common = (req.simulations, duration, req.years_until_retirement, req.initial_amount,
              req.monthly_contribution, req.annual_withdrawal, req.target, weights)
    if req.model == 'index':
        savings = float(req.weights.get('Savings', 0))
        cash = float(max(0., 1 - sum(req.weights.values())))
        bm, bc, em, ec = market_stats()
        batch = index_cached_batch if cached else index_batch
        extra = (scenario_banks.index,) if cached else ()
        outputs = batch(*common, savings, cash, bm[active], em[active],
                              covariance_factor(bc[np.ix_(active, active)]),
                              covariance_factor(ec[np.ix_(active, active)]),
                              active, sample_days, seed, *extra)
    else:
        savings = float(max(0., 1 - sum(req.weights.values())))
        rostrum = float(req.weights.get('Rostrum', 0))
        mean, cov, fof_vol = fund_stats()
        batch = fund_cached_batch if cached else fund_batch
        extra = (scenario_banks.funds,) if cached else ()
        outputs = batch(*common, savings, rostrum, mean[active],
                             covariance_factor(cov[np.ix_(active, active)]),
                             active, fof_vol, sample_days, seed, *extra)
    sampled, summaries, failures, successes = outputs
    if not np.isfinite(sampled).all() or not np.isfinite(summaries[:, [0, 2, 3]]).all():
        raise ValueError('Simulation produced non-finite wealth; review inputs and model data.')
    lines = np.percentile(sampled, [10, 25, 50, 75, 90], axis=1)
    ending = summaries[:, 3]
    annualized = summaries[:, 1]
    annualized = annualized[np.isfinite(annualized)]
    return {
        'model': req.model, 'seed': seed, 'sampling_mode': 'shared_scenarios' if cached else 'fresh', 'request': req.model_dump(),
        'chart_ages': (req.age + sample_days / 252).tolist(),
        'percentiles': {str(p): lines[i].tolist() for i, p in enumerate([10,25,50,75,90])},
        'ending_values': ending.tolist(),
        'statistics': {
            'success_probability': float(successes.mean()),
            'survival_probability': float(1 - failures.mean()),
            'median_retirement_wealth': float(np.median(summaries[:, 2])),
            'median_ending_wealth': float(np.median(ending)),
            'median_real_ending_wealth': float(np.median(ending)/(1+req.inflation)**(85-req.age)),
            'median_max_drawdown': float(np.median(summaries[:, 0])),
            'median_accumulation_annualized_return': finite_number(np.median(annualized)) if len(annualized) else None,
            'valid_annualized_trials': int(len(annualized)),
        },
        'simulation_seconds': time.perf_counter() - start,
    }

def warmup():
    """Compile both engines and load datasets before readiness; no user pays JIT cost."""
    # Compile using empty allocations and a one-year horizon to keep startup work small.
    for model in ('index', 'funds'):
        simulate(SimulationRequest(model=model, age=84, years_until_retirement=0,
                                   simulations=100, initial_amount=1_000_000,
                                   annual_withdrawal=0, seed=123))

@njit(cache=True, nogil=True)
def index_cached_batch(n, duration, retirement_years, initial, contribution, withdrawal, target, weights, savings_weight, cash_weight, bull_mean, bear_mean, bull_factor, bear_factor, active, sample_days, seed, scenarios):
    sampled = np.empty((len(sample_days), n), dtype=np.float32)
    summaries = np.empty((n, 4))
    failures = np.zeros(n, dtype=np.uint8)
    successes = np.zeros(n, dtype=np.uint8)
    stock_weights = weights[np.array([0, 1, 2, 7, 8, 9, 10, 11, 12])]
    for sim in range(n):
        np.random.seed((seed + sim * 2654435761) % 4294967296)
        maturity = np.random.randint(504, 2520)
        path, failed, success = index_cached_path(retirement_years, duration, maturity, initial * weights, initial * savings_weight, initial * cash_weight, weights, contribution, savings_weight, 1.0175 ** (1 / 252), withdrawal, 0.00011, cash_weight, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.04 ** (1 / 252), 1.05 ** (1 / 252), 1.08 ** (1 / 252), 1.045 ** (1 / 252), 1.05 ** (1 / 252), 1.08 ** (1 / 252), stock_weights, weights[3], weights[4], weights[5], weights[6], target, bull_mean, bear_mean, bull_factor, bear_factor, active, FEE_DRAG, scenarios[sim])
        for j in range(len(sample_days)):
            sampled[j, sim] = path[sample_days[j]]
        summary = path_summary(path, retirement_years * 252, initial, contribution)
        for k in range(4):
            summaries[sim, k] = summary[k]
        failures[sim] = failed
        successes[sim] = success
    return (sampled, summaries, failures, successes)

@njit(cache=True, nogil=True)
def fund_cached_batch(n, duration, retirement_years, initial, contribution, withdrawal, target, weights, savings_weight, rostrum_weight, mean, factor, active, fof_vol, sample_days, seed, scenarios):
    sampled = np.empty((len(sample_days), n), dtype=np.float32)
    summaries = np.empty((n, 4))
    failures = np.zeros(n, dtype=np.uint8)
    successes = np.zeros(n, dtype=np.uint8)
    for sim in range(n):
        np.random.seed((seed + sim * 2654435761) % 4294967296)
        amounts = initial * weights
        path, failed, success = fund_cached_path(retirement_years, duration, contribution, withdrawal, amounts[1], amounts[6], amounts[7], amounts[8], amounts[9], amounts[3], amounts[2], amounts[0], initial * savings_weight, initial * rostrum_weight, amounts[4], amounts[10], amounts[11], amounts[12], amounts[5], weights[6], weights[7], weights[8], weights[9], weights[1], weights[3], weights[2], weights[0], savings_weight, rostrum_weight, weights[4], weights[10], weights[11], weights[12], weights[5], target, mean, factor, active, ROSTRUM_DAILY, fof_vol, scenarios[sim])
        for j in range(len(sample_days)):
            sampled[j, sim] = path[sample_days[j]]
        summary = path_summary(path, retirement_years * 252, initial, contribution)
        for k in range(4):
            summaries[sim, k] = summary[k]
        failures[sim] = failed
        successes[sim] = success
    return (sampled, summaries, failures, successes)

# Engine revision 2: skip direct-bond hazard draws when no direct bonds exist.

# Engine revision 3: cached index path uses scalar array updates without daily row views.
