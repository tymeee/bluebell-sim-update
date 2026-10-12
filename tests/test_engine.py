"""Financial-rule regressions and concurrent seeded execution checks."""
import inspect
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pytest
from fast_simulator import kernels
from fast_simulator.engine import simulate, warmup, path_summary, covariance_factor, FEE_DRAG
from fast_simulator.schema import SimulationRequest, INDEX_NAMES, FUND_NAMES, PRESETS
from tests.legacy_kernels import run_path, sim_path


def call_with_mapping(function, mapping):
    signature = inspect.signature(getattr(function, 'py_func', function))
    return function(*[mapping[name] for name in signature.parameters])

@pytest.mark.parametrize('withdrawal', [0., 120_000., 3_000_000.])
@pytest.mark.parametrize('accumulation', [0, 1])
def test_index_rules_match_original(withdrawal, accumulation):
    n = 3*252
    weights = np.arange(1,14,dtype=float)/250
    args = dict(acum_years=accumulation, duration=n, matured_duration=504,
                assets=1_000_000*weights, savings_account=100_000., pure_cash_amt=536_000.,
                contribution_weights=weights, inserted_funds=10_000.,
                savings_account_weight=.1, saving_daily_return=1.0175**(1/252),
                withdrawal_percentage=withdrawal, daily_hazard_rate=.00011, pure_cash_weight=.536,
                stock_allocations=weights[[0,1,2,7,8,9,10,11,12]],
                bond_mutualfund_allocation=weights[3], hybrid_mutualfund_aggresive_allocation=weights[4],
                hybrid_mutualfund_moderate_allocation=weights[5], hybrid_mutualfund_conservative_allocation=weights[6],
                target=800_000.)
    for country in ['us','thai']:
        for kind,rate in [('gov',.04),('inv',.05),('spec',.08)]:
            args[f'{country}_{kind}_bond']=0.
            args[f'{country}_{kind}_bond_daily_return']=(1+rate)**(1/252)
    args.update(bull_mult=np.tile(FEE_DRAG,(n,1)),bear_mult=np.tile(FEE_DRAG,(n,1)))
    legacy = call_with_mapping(run_path, {**args,'assets':args['assets'].copy()})
    args.update(bull_mean=np.zeros(13),bear_mean=np.zeros(13),
                bull_factor=np.zeros((13,13)),bear_factor=np.zeros((13,13)),
                active=np.arange(13,dtype=np.int64),fee_drag=FEE_DRAG)
    current = call_with_mapping(kernels.index_path, {**args,'assets':args['assets'].copy()})
    np.testing.assert_allclose(current[0],legacy[0],rtol=1e-7)
    assert current[1:] == legacy[1:]
    args['scenarios']=np.tile(FEE_DRAG,(n,1))
    cached=call_with_mapping(kernels.index_cached_path,{**args,'assets':args['assets'].copy()})
    np.testing.assert_allclose(cached[0],legacy[0],rtol=1e-7)
    assert cached[1:]==legacy[1:]

@pytest.mark.parametrize('withdrawal', [0., 120_000., 3_000_000.])
@pytest.mark.parametrize('accumulation', [0, 1])
def test_fund_rules_match_original(withdrawal, accumulation):
    n=3*252
    weights=np.arange(1,14,dtype=float)/250
    locations=np.linspace(-.0001,.0003,13)
    aliases=['ktp','gqg','eae','gtech','gnph','gcore','kkpplus','kkpcash','kfa','ugi','healthcarea','propa','sp500a']
    args=dict(acum_years=accumulation,duration=n,inserted_funds=10_000.,
              yearly_withdrawals=withdrawal,savings_amt=636_000.,savings_alloc=.636,
              rostrum_amt=0.,rostrum_alloc=0.,rostrum_returns=np.ones(n)*1.0004,
              target=800_000.)
    for i,alias in enumerate(aliases):
        args[f'{alias}_amt']=1_000_000*weights[i]
        args[f'{alias}_alloc' if alias!='ktp' else 'ktprecious_alloc']=weights[i]
        args[f'{alias}_returns']=np.repeat(locations[i],n)
    legacy=call_with_mapping(sim_path,args)
    args.update(mean=locations,factor=np.zeros((13,13)),active=np.arange(13,dtype=np.int64),
                rostrum_daily=1.0004,fof_vol=0.)
    current=call_with_mapping(kernels.fund_path,args)
    np.testing.assert_allclose(current[0],legacy[0],rtol=1e-12)
    assert current[1:]==legacy[1:]
    offsets=np.array([.00185,.0002,.001,.001875,.0002,.00034,0.,0.,0.,0.,.0001,0.,.0002])
    args['scenarios']=np.column_stack([np.tile(np.exp(locations-offsets),(n,1)),np.repeat(1.0004,n)])
    cached=call_with_mapping(kernels.fund_cached_path,args)
    np.testing.assert_allclose(cached[0],legacy[0],rtol=1e-12)
    assert cached[1:]==legacy[1:]

@pytest.mark.parametrize('model', ['index','funds'])
def test_seeded_concurrent_runs_are_identical(model):
    weights={'US Equity':.7,'Bond/Fixed Income Fund':.3} if model=='index' else PRESETS['Bluebell Balance']
    request=SimulationRequest(model=model,age=80,years_until_retirement=2,
                              simulations=100,weights=weights,seed=987654,annual_withdrawal=0)
    expected=simulate(request)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(simulate,[request]*4))
    for result in results:
        assert result['statistics']==expected['statistics']
        assert result['percentiles']==expected['percentiles']
        assert result['ending_values']==expected['ending_values']
        assert result['statistics']['valid_annualized_trials']==100
    assert request.age+request.years_until_retirement in expected['chart_ages']
    assert len(expected['chart_ages'])<=63

@pytest.mark.parametrize('model', ['index','funds'])
def test_bankruptcy_before_retirement_returns_zero_goal(model):
    result=simulate(SimulationRequest(model=model,initial_amount=0,monthly_contribution=0,
                    annual_withdrawal=120000,age=80,years_until_retirement=2,seed=1,simulations=100))
    assert result['statistics']['success_probability']==0
    assert result['statistics']['survival_probability']==0
    assert result['statistics']['median_accumulation_annualized_return'] is None

def test_summary_uses_all_days_and_excludes_contributions():
    path=np.repeat(100.,252)
    for i in range(252):
        path[i]=100+10*(i//21+1)
    dd, annualized, retired, ending=path_summary(path,252,100.,10.)
    assert annualized==pytest.approx(0)
    assert dd==0
    assert ending==220

@pytest.mark.parametrize('change', [
    {'weights':{'US Equity':1.1}}, {'weights':{'US Equity':float('nan')}},
    {'weights':{'US Equity':.7,'Savings':.4}}, {'weights':{'unknown':.1}},
    {'age':80,'years_until_retirement':5}, {'simulations':1001},
    {'model':'funds','weights':{'Rostrum':.1}},
])
def test_invalid_requests_rejected(change):
    with pytest.raises(ValueError):
        SimulationRequest(**change)

def test_covariance_validation():
    cov=np.array([[1.,.25],[.25,2.]])
    factor=covariance_factor(cov)
    np.testing.assert_allclose(factor@factor.T,cov)
    factor=covariance_factor(np.ones((2,2)))
    np.testing.assert_allclose(factor@factor.T,np.ones((2,2)))
    with pytest.raises(ValueError):
        covariance_factor(np.array([[1.,2.],[2.,1.]]))

from numba import njit
@njit
def sample_fund_distribution(n, mean, factor, active):
    np.random.seed(12345)
    out=np.empty((n,len(active)))
    for i in range(n):
        full=kernels.fund_returns(mean,factor,active)
        for j in range(len(active)):
            out[i,j]=full[active[j]]
    return out

def test_student_t_covariance_and_location_preserved():
    mean=np.array([.1,-.2,.3])
    cov=np.array([[1.,.4,.1],[.4,2.,-.3],[.1,-.3,1.]])
    factor=covariance_factor(cov)
    samples=sample_fund_distribution(120000,mean,factor,np.array([0,5,12],dtype=np.int64))
    np.testing.assert_allclose(samples.mean(axis=0),mean,atol=.025)
    np.testing.assert_allclose(np.cov(samples.T),cov*5/3,rtol=.06,atol=.025)

@pytest.mark.parametrize('model',['index','funds'])
def test_shared_bank_is_repeatable_and_preserves_fresh_option(model):
    from fast_simulator.scenarios import build_banks
    banks=build_banks(seed=123,trials=100,days=252)
    names=INDEX_NAMES if model=='index' else FUND_NAMES
    request=SimulationRequest(model=model,age=84,years_until_retirement=0,
        weights={name:1/13 for name in names},annual_withdrawal=0,simulations=100)
    a=simulate(request,banks)
    b=simulate(request,banks)
    assert a['sampling_mode']=='shared_scenarios'
    assert a['percentiles']==b['percentiles']
    assert a['statistics']==b['statistics']
    request.seed=123
    assert simulate(request,banks)['sampling_mode']=='fresh'
    request.seed=None
    request.age=83
    with pytest.raises(ValueError,match='exceeds'):
        simulate(request,banks)
