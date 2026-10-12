"""User-requested PDF export; never part of the simulation API."""
from io import BytesIO
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table

def build_report(result):
    styles = getSampleStyleSheet()
    output = BytesIO()
    story = [Paragraph('BlueBridge Portfolio Simulation', styles['Title']), Spacer(1, 5*mm)]
    request = result['request']
    story.append(Paragraph(escape(f"Model: {result['model']} | Trials: {request['simulations']} | Seed: {result['seed']}"), styles['Normal']))
    rows = [['Input', 'Value']]
    for key in ['age', 'years_until_retirement', 'initial_amount', 'monthly_contribution', 'annual_withdrawal', 'target', 'inflation']:
        rows.append([key.replace('_', ' ').title(), str(request[key])])
    for name, value in request['weights'].items():
        rows.append([name, f'{value:.1%}'])
    story.extend([Spacer(1, 4*mm), Table(rows, hAlign='LEFT'), Spacer(1, 5*mm)])
    # Figure instances avoid pyplot's global mutable state during concurrent exports.
    fig = Figure(figsize=(9,4), constrained_layout=True)
    ax = fig.subplots()
    for label in ['10','25','50','75','90']:
        ax.plot(result['chart_ages'], [v/1e6 for v in result['percentiles'][label]], label=f'P{label}')
    ax.set(xlabel='Age', ylabel='Portfolio value (THB millions)')
    ax.axvline(request['age']+request['years_until_retirement'], color='gray', linestyle='--')
    ax.legend(); ax.grid(alpha=.2)
    png = BytesIO(); fig.savefig(png, format='png', dpi=120); png.seek(0)
    story.append(Image(png, width=175*mm, height=78*mm))
    rows = [['Statistic', 'Value']]
    for name,value in result['statistics'].items():
        rows.append([name.replace('_',' ').title(), 'N/A' if value is None else f'{value:,.4f}'])
    story.extend([Spacer(1, 4*mm), Table(rows, hAlign='LEFT'), Spacer(1, 5*mm)])
    story.append(Paragraph('Historical-data scenarios for education and planning. Outcomes are not guaranteed. Daily simulation rules are retained; chart values are sampled monthly.',styles['Normal']))
    SimpleDocTemplate(output, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm).build(story)
    return output.getvalue()
