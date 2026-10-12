"""New app entry point. Local mode works immediately; set SIMULATOR_API_URL for dedicated compute."""
import os
import time
import httpx
import streamlit as st
import plotly.graph_objects as go
from fast_simulator.schema import SimulationRequest, INDEX_NAMES, FUND_NAMES, PRESETS

st.set_page_config(page_title='BlueBridge Fast Simulator', page_icon='📈', layout='wide')
st.title('BlueBridge Portfolio Simulator')
st.caption('Explore retirement outcomes with daily simulation and monthly projection charts.')

def setting(name, default=''):
    value = os.getenv(name)
    if value is not None:
        return value
    try:
        return str(st.secrets.get(name, default))
    except FileNotFoundError:
        return default

api_url = setting('SIMULATOR_API_URL').rstrip('/')
api_key = setting('SIMULATOR_API_KEY')
model_label = st.sidebar.radio('Model', ['Market Index', 'Bluebell Offered Funds'])
model = 'index' if model_label == 'Market Index' else 'funds'
names = INDEX_NAMES + ['Savings'] if model == 'index' else FUND_NAMES + ['Rostrum']
preset = st.sidebar.selectbox('Portfolio', ['Custom'] + list(PRESETS)) if model == 'funds' else 'Custom'
if preset == 'Custom':
    default = ['US Equity', 'Bond/Fixed Income Fund'] if model == 'index' else ['KKP Plus', 'KFAFIX']
    selected = st.sidebar.multiselect('Select assets', names, default=default, key=f'selection_{model}')
else:
    selected = list(PRESETS[preset])

with st.sidebar.form('simulation_inputs'):
    initial = st.number_input('Initial amount (THB)', min_value=0., max_value=100_000_000., value=1_000_000., step=100_000.)
    contribution = st.number_input('Monthly contribution (THB)', min_value=0., max_value=300_000., value=10_000., step=1_000.)
    withdrawal = st.number_input('Annual withdrawal (THB)', min_value=0., max_value=3_000_000., value=100_000., step=10_000.)
    age = st.number_input('Your age', min_value=0, max_value=84, value=35)
    years = st.number_input('Years until retirement', min_value=0, max_value=84, value=20)
    target = st.number_input('Target wealth at retirement (THB)', min_value=0., max_value=100_000_000., value=5_000_000., step=100_000.)
    trials = st.slider('Simulations', 100, 500, 250, 10)
    inflation = st.slider('Annual inflation', 0., .15, .02, .005)
    st.subheader('Allocations')
    if preset == 'Custom':
        weights = {}
        for i,name in enumerate(selected):
            default_weight = .7 if i == 0 else (.3 if i == 1 else 0.)
            weights[name] = st.slider(name, 0., 1., default_weight, .01, key=f'w_{model}_{name}')
    else:
        weights = PRESETS[preset].copy()
        for name,value in weights.items():
            st.write(f'{name}: {value:.0%}')
    st.caption('Unallocated money becomes cash in the index model, or non-interest-bearing savings in the funds model.')
    submitted = st.form_submit_button('Run Simulation', type='primary', use_container_width=True)

if submitted:
    started = time.perf_counter()
    try:
        req = SimulationRequest(model=model, age=age, years_until_retirement=years,
            initial_amount=initial, monthly_contribution=contribution,
            annual_withdrawal=withdrawal, target=target, simulations=trials,
            inflation=inflation, weights=weights)
        with st.spinner('Running simulation…'):
            if api_url:
                headers = {'X-API-Key':api_key} if api_key else {}
                with httpx.Client(timeout=httpx.Timeout(180., connect=10.)) as client:
                    response = client.post(api_url+'/api/simulate', json=req.model_dump(), headers=headers)
                    if response.is_error:
                        detail = response.json().get('detail', response.text)
                        raise RuntimeError(f'Simulation service ({response.status_code}): {detail}')
                    result = response.json()
            else:
                from fast_simulator.engine import simulate
                result = simulate(req)
        st.session_state.fast_result = result
        st.session_state.fast_elapsed = time.perf_counter() - started
        st.session_state.pop('fast_pdf', None)
    except Exception as exc:
        st.error(str(exc))

result = st.session_state.get('fast_result')
if result:
    req = result['request']
    stats = result['statistics']
    st.caption(f"Showing the last completed {result['model']} run: age {req['age']}, retirement age {req['age']+req['years_until_retirement']}, {req['simulations']} trials. Submit Run to apply edited inputs.")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric('Median retirement wealth', f"THB {stats['median_retirement_wealth']:,.0f}")
    c2.metric('Target reached at retirement', f"{stats['success_probability']:.1%}")
    c3.metric('Funds last through horizon', f"{stats['survival_probability']:.1%}")
    c4.metric('Median maximum drawdown', f"{stats['median_max_drawdown']:.1%}")
    fig = go.Figure()
    for label in ['10','25','50','75','90']:
        fig.add_trace(go.Scatter(x=result['chart_ages'], y=result['percentiles'][label],
            mode='lines', name=f'P{label}', line={'width':3 if label=='50' else 1}))
    fig.add_vline(x=req['age']+req['years_until_retirement'], line_dash='dash')
    fig.update_layout(xaxis_title='Age', yaxis_title='Portfolio value (THB)', height=470)
    st.plotly_chart(fig, use_container_width=True)
    c1,c2,c3 = st.columns(3)
    c1.metric('Median ending wealth',f"THB {stats['median_ending_wealth']:,.0f}")
    c2.metric('Median ending wealth, today’s THB',f"THB {stats['median_real_ending_wealth']:,.0f}")
    annualized = stats['median_accumulation_annualized_return']
    c3.metric('Median accumulation annualized return', 'N/A' if annualized is None else f'{annualized:.2%}')
    hist = go.Figure(go.Histogram(x=result['ending_values'], nbinsx=40))
    hist.update_layout(xaxis_title='Ending value (THB)',yaxis_title='Trials',height=280)
    st.plotly_chart(hist, use_container_width=True)
    if result.get('sampling_mode') == 'shared_scenarios':
        st.caption('Fast mode uses a shared bank of independent trials. Repeated portfolios reuse scenarios for stable comparisons.')
    st.caption(f"Request completed in {st.session_state.fast_elapsed:.2f}s; engine {result['simulation_seconds']:.2f}s. Browser rendering is additional. Seed: {result['seed']}.")
    if st.button('Generate PDF report'):
        with st.spinner('Preparing report…'):
            from fast_simulator.report import build_report
            st.session_state.fast_pdf = build_report(result)
    if st.session_state.get('fast_pdf'):
        st.download_button('Download PDF', st.session_state.fast_pdf,
                           file_name='bluebridge_portfolio_report.pdf', mime='application/pdf')
else:
    st.info('Choose your inputs and allocations, then press Run Simulation.')
if not api_url:
    st.caption('Local computation mode. The first run compiles the engine; use a warmed dedicated backend for multi-user deployment.')
st.caption('For education and scenario planning. Historical data and model assumptions do not guarantee future returns.')
