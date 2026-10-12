"""Original upstream BlueBridge PDF presentation, generated only on demand."""
from io import BytesIO
from copy import deepcopy
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as PDFImage, Table, TableStyle, PageBreak

def chart_to_png_buffer(figure, width: int=1400, height: int=750) -> BytesIO:
    """Convert a Plotly figure into a print-friendly PNG buffer."""
    report_figure = deepcopy(figure)
    for annotation in report_figure.layout.annotations or ():
        if annotation.text == 'Retirement':
            retirement_x = annotation.x
            annotation.update(font=dict(color='#000000'))
            for shape in report_figure.layout.shapes or ():
                if shape.x0 == retirement_x and shape.x1 == retirement_x:
                    shape.update(line=dict(color='#000000', width=2, dash='dash'))
    report_figure.update_layout(template='plotly_white', paper_bgcolor='white', plot_bgcolor='white', font=dict(color='#20354F', size=14), title_font=dict(color='#102A4C', size=22), margin=dict(l=90, r=50, t=90, b=80))
    report_figure.update_layout(legend=dict(font=dict(size=18, color='#20354F', family='Arial'), title=dict(font=dict(size=18, color='#20354F'))))
    report_figure.update_xaxes(gridcolor='#DCE4EE', linecolor='#8CA0B8', tickfont=dict(color='#405670'), title_font=dict(color='#405670'))
    report_figure.update_yaxes(gridcolor='#DCE4EE', linecolor='#8CA0B8', tickfont=dict(color='#405670'), title_font=dict(color='#405670'))
    image_bytes = report_figure.to_image(format='png', width=width, height=height, scale=2)
    image_buffer = BytesIO(image_bytes)
    image_buffer.seek(0)
    return image_buffer

def build_portfolio_pdf(projection_figure, allocation_figure, histogram_figure, statistics: dict[str, str], portfolio_name: str, disclaimer: str) -> bytes:
    """Create the complete portfolio report and return PDF bytes."""
    pdf_buffer = BytesIO()
    document = SimpleDocTemplate(pdf_buffer, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=15 * mm, bottomMargin=15 * mm, title='Portfolio Simulation Report', author='Bluebell Portfolio Simulator')
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='PortfolioReportTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=23, leading=28, textColor=colors.HexColor('#102A4C'), spaceAfter=5 * mm)
    heading_style = ParagraphStyle(name='PortfolioReportHeading', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=colors.HexColor('#17477F'), spaceBefore=4 * mm, spaceAfter=3 * mm)
    body_style = ParagraphStyle(name='PortfolioReportBody', parent=styles['BodyText'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor('#31465E'))
    disclaimer_style = ParagraphStyle(name='PortfolioReportDisclaimer', parent=body_style, fontSize=7.5, leading=10, textColor=colors.HexColor('#687A8F'))
    story = []
    image_buffers = []
    story.append(Paragraph('Portfolio Simulation Report', title_style))
    story.append(Paragraph(f'<b>Portfolio:</b> {portfolio_name}<br/><b>Generated:</b> {datetime.now():%d %B %Y}', body_style))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph('Simulation summary', heading_style))
    statistic_rows = [['Statistic', 'Result']]
    for statistic_name, statistic_value in statistics.items():
        statistic_rows.append([statistic_name, statistic_value])
    statistics_table = Table(statistic_rows, colWidths=[105 * mm, 65 * mm], repeatRows=1)
    statistics_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#17477F')), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F7FC')), ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#243A53')), ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C5D3E3')), ('FONTSIZE', (0, 0), (-1, -1), 9), ('ALIGN', (1, 1), (1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    story.append(statistics_table)
    story.append(Spacer(1, 6 * mm))
    story.append(PageBreak())
    story.append(Paragraph('Portfolio allocation', heading_style))
    allocation_png = chart_to_png_buffer(allocation_figure, width=1100, height=700)
    image_buffers.append(allocation_png)
    story.append(PDFImage(allocation_png, width=170 * mm, height=108 * mm))
    story.append(Paragraph('Projected portfolio outcomes', heading_style))
    projection_png = chart_to_png_buffer(projection_figure, width=1600, height=850)
    image_buffers.append(projection_png)
    story.append(PDFImage(projection_png, width=178 * mm, height=95 * mm))
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph('The percentile lines represent the range of simulated portfolio outcomes. The median is the middle simulated path, while the lower and upper percentiles represent less favorable and more favorable outcomes.', body_style))
    story.append(PageBreak())
    story.append(Paragraph('Distribution of final portfolio values', heading_style))
    histogram_png = chart_to_png_buffer(histogram_figure, width=1600, height=800)
    image_buffers.append(histogram_png)
    story.append(PDFImage(histogram_png, width=178 * mm, height=89 * mm))
    story.append(Spacer(1, 7 * mm))
    story.append(Paragraph('Important information', heading_style))
    story.append(Paragraph(disclaimer, disclaimer_style))
    document.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
