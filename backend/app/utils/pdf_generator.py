import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def create_report_pdf(title: str, user_name: str, data: dict, report_type: str) -> io.BytesIO:
    """
    Generates a PDF document in memory and returns a BytesIO stream.
    report_type can be 'disease', 'soil', 'yield'.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"<b>Kisaan Mitra</b> - {title}", title_style))
    elements.append(Spacer(1, 20))
    
    # Header Info
    date_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")
    elements.append(Paragraph(f"<b>Generated For:</b> {user_name}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {date_str}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Report Specific Data
    if report_type == "disease":
        elements.append(Paragraph("<b>Disease Diagnosis Report</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        table_data = [
            ["Crop", data.get("crop", "Unknown")],
            ["Disease Detected", data.get("disease", "Unknown")],
            ["Confidence Match", f"{data.get('confidence', 0)}%"]
        ]
        t = Table(table_data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold')
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Recommended Treatment:</b>", styles['Heading3']))
        elements.append(Paragraph(data.get("treatment", "Consult local expert."), normal_style))
        
    elif report_type == "soil":
        elements.append(Paragraph("<b>Soil Health Analysis</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        table_data = [
            ["Metric", "Value"],
            ["Nitrogen (N)", f"{data.get('N', 0)} mg/kg"],
            ["Phosphorus (P)", f"{data.get('P', 0)} mg/kg"],
            ["Potassium (K)", f"{data.get('K', 0)} mg/kg"],
            ["pH Level", str(data.get('ph', 0))],
            ["Soil Health Score", f"{data.get('score', 0)}/100"]
        ]
        t = Table(table_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#009688")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"<b>Rating:</b> {data.get('rating', 'Unknown')}", normal_style))
        
    elif report_type == "yield":
        elements.append(Paragraph("<b>Yield Forecast Report</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        table_data = [
            ["Crop", data.get("crop", "Unknown")],
            ["Region", data.get("region", "Unknown")],
            ["Expected Yield", f"{data.get('estimated_yield', 0)} t/ha"]
        ]
        t = Table(table_data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold')
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Optimization Note:</b> To achieve this yield, ensure proper irrigation and fertilizer schedules are followed as per local agro-climatic zone standards.", normal_style))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
