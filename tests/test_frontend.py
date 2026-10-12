from pathlib import Path
from streamlit.testing.v1 import AppTest
from fast_simulator.engine import warmup

ROOT=Path(__file__).resolve().parents[1]

def test_original_interface_with_both_optimized_models(monkeypatch):
    monkeypatch.delenv('SIMULATOR_API_URL',raising=False)
    warmup()
    app=AppTest.from_file(ROOT/'Fast_Simulator.py',default_timeout=40).run()
    assert not app.exception
    assert not app.error
    assert next(s for s in app.slider if s.label=='Simulations').max==500
    next(x for x in app.text_input if x.label=='Your Age').set_value('80').run()
    next(x for x in app.text_input if x.label=='Years Until Retirement').set_value('2').run()
    app.multiselect[0].set_value(['US Equity','Bond/Fixed Income Fund']).run()
    next(x for x in app.slider if x.label=='US Equity').set_value(.7).run()
    next(x for x in app.slider if x.label=='Bond Fund').set_value(.3).run()
    next(x for x in app.button if x.label=='Run Simulation').click().run(timeout=40)
    assert not app.exception
    assert not app.error
    assert len(app.metric)==6
    result=app.session_state.fast_result
    assert result['request']['weights']['US Equity']==.7
    assert result['request']['age']==80
    assert result['request']['years_until_retirement']==2
    assert len(app.get('plotly_chart'))==4  # desktop/mobile projection, pie, histogram
    next(x for x in app.radio if x.label=='Model Type').set_value('Bluebell Offered Mutual Funds Model').run()
    assert not app.exception
    assert len(app.metric)==6
    next(x for x in app.radio if x.label=='Portfolio').set_value('Bluebell Balance').run()
    next(x for x in app.button if x.label=='Run Simulation').click().run(timeout=40)
    assert not app.exception
    assert not app.error
    assert app.session_state.fast_result['model']=='funds'
    next(x for x in app.button if x.label=='Generate Portfolio Report').click().run(timeout=40)
    assert not app.exception
    assert app.session_state.fast_pdf.startswith(b'%PDF')


def test_original_assets_and_report_layout():
    import fast_simulator.original_report as report
    assert 'Portfolio Simulation Report' in report.build_portfolio_pdf.__code__.co_consts
    assert (ROOT/'style.css').is_file()
    assert (ROOT/'bluebridgeai1-removebg-preview.png').is_file()
    assert (ROOT/'.streamlit/config.toml').is_file()
    assert (ROOT/'pages/Retirement_Fund_Calculator.py').is_file()
