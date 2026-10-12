from streamlit.testing.v1 import AppTest
from pathlib import Path
from fast_simulator.engine import simulate, warmup
from fast_simulator.report import build_report

def test_frontend_submission_and_persistent_results(monkeypatch):
    monkeypatch.delenv('SIMULATOR_API_URL',raising=False)
    warmup()
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'Fast_Simulator.py',default_timeout=40).run()
    assert not app.exception
    # Short horizon keeps this a smoke test; financial rules have separate regressions.
    next(x for x in app.number_input if x.label=='Your age').set_value(80)
    next(x for x in app.number_input if x.label=='Years until retirement').set_value(2)
    next(x for x in app.button if x.label=='Run Simulation').click().run(timeout=40)
    assert not app.exception
    assert not app.error
    assert len(app.metric)==7
    app.radio[0].set_value('Bluebell Offered Funds').run()
    assert not app.exception
    assert len(app.metric)==7
    next(x for x in app.button if x.label=='Run Simulation').click().run(timeout=40)
    assert not app.exception
    assert not app.error
    assert app.session_state.fast_result['model']=='funds'
    next(x for x in app.button if x.label=='Generate PDF report').click().run(timeout=40)
    assert not app.exception
    assert app.session_state.fast_pdf.startswith(b'%PDF')

def test_report_generation_is_separate():
    result=simulate({'model':'index','age':84,'years_until_retirement':0,'seed':1})
    assert 'pdf' not in result
    assert build_report(result).startswith(b'%PDF')
