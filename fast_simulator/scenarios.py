"""Optional shared Monte Carlo scenario banks, generated once at startup.

Each trial is independent within the bank. Requests intentionally share scenarios
(common random numbers), so portfolio comparisons are stable. Explicit request
seeds bypass this cache. Daily shocks and full cross-asset dependence are retained.
Bank dimensions are 1,000 trials x 85*252 days x all model assets, in float64.
"""
from dataclasses import dataclass
import numpy as np
from numba import njit
from .engine import market_stats, fund_stats, covariance_factor, FEE_DRAG, ROSTRUM_DAILY
from .kernels import index_multipliers, fund_returns

@dataclass(frozen=True)
class ScenarioBanks:
    seed: int
    index: np.ndarray
    funds: np.ndarray

@njit(cache=True, nogil=True)
def generate_index(bank, seed, bull_mean, bear_mean, bull_factor, bear_factor):
    active=np.arange(13,dtype=np.int64)
    for sim in range(len(bank)):
        np.random.seed((seed+sim*2654435761)%4294967296)
        market=np.random.randint(0,2)
        for day in range(bank.shape[1]):
            if market==1:
                bank[sim,day]=index_multipliers(bear_mean,bear_factor,active,FEE_DRAG)
                if np.random.random()<.05: market=0
            else:
                bank[sim,day]=index_multipliers(bull_mean,bull_factor,active,FEE_DRAG)
                if np.random.random()<.02: market=1

@njit(cache=True, nogil=True)
def generate_funds(bank, seed, mean, factor, fof_vol):
    active=np.arange(13,dtype=np.int64)
    offsets=np.array([.00185,.0002,.001,.001875,.0002,.00034,0.,0.,0.,0.,.0001,0.,.0002])
    for sim in range(len(bank)):
        np.random.seed((seed+sim*2654435761)%4294967296)
        for day in range(bank.shape[1]):
            returns=fund_returns(mean,factor,active)
            for asset in range(13):
                bank[sim,day,asset]=np.exp(returns[asset]-offsets[asset])
            bank[sim,day,13]=ROSTRUM_DAILY+1.75*fof_vol*np.random.standard_t(10)

def build_banks(seed=20261012, trials=1000, days=85*252):
    """Reserve ~4.63 GB for production banks. Use an adequately sized server."""
    index=np.empty((trials,days,13),dtype=np.float64)
    funds=np.empty((trials,days,14),dtype=np.float64)
    bm,bc,em,ec=market_stats()
    generate_index(index,seed,bm,em,covariance_factor(bc),covariance_factor(ec))
    mean,cov,fof_vol=fund_stats()
    generate_funds(funds,seed,mean,covariance_factor(cov),fof_vol)
    if not np.isfinite(index).all() or not np.isfinite(funds).all():
        raise ValueError('Scenario bank produced non-finite returns.')
    index.flags.writeable=False
    funds.flags.writeable=False
    return ScenarioBanks(seed,index,funds)

def warm_cached(banks):
    # Compile cached paths using the real readonly bank signature before readiness.
    from .engine import simulate
    from .schema import SimulationRequest
    for model in ('index','funds'):
        simulate(SimulationRequest(model=model,age=84,years_until_retirement=0,
                                   simulations=100,annual_withdrawal=0),banks)
