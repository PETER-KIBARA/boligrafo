import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from django.utils import timezone

class ReportPDFService:
    @staticmethod
    def generate_patient_report(report_data):
        """
        Generates a PDF report for a specific patient.
        report_data is a dictionary containing patient info, vitals, prescriptions, etc.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  # Center
            spaceAfter=20
        )
        elements.append(Paragraph("Patient Medical Report", title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Patient Info Section
        elements.append(Paragraph("Patient Information", styles['Heading2']))
        patient_info = [
            ["Name:", report_data.get('patient_name', 'N/A')],
            ["Email:", report_data.get('patient_email', 'N/A')],
            ["Phone:", report_data.get('patient_phone', 'N/A')],
        ]
        info_table = Table(patient_info, colWidths=[100, 300])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 20))

        # Summary Stats
        elements.append(Paragraph("Health Summary", styles['Heading2']))
        summary_info = [
            ["Avg Systolic:", f"{report_data.get('avg_systolic', 'N/A')} mmHg"],
            ["Avg Diastolic:", f"{report_data.get('avg_diastolic', 'N/A')} mmHg"],
            ["Avg Heartrate:", f"{report_data.get('avg_heartrate', 'N/A')} bpm"],
        ]
        summary_table = Table(summary_info, colWidths=[150, 250])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))

        # Vitals Table
        elements.append(Paragraph("Recent Vital Readings", styles['Heading2']))
        vitals = report_data.get('vitals', [])
        if vitals:
            vitals_data = [["Date", "BP (Systolic/Diastolic)", "Heart Rate"]]
            for v in vitals[:10]:  # Limit to 10 for the report
                created_at = v.get('created_at', '')
                if created_at:
                    try:
                        # Assuming ISO format from serializer
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        date_str = created_at[:16]
                else:
                    date_str = 'N/A'
                
                vitals_data.append([
                    date_str,
                    f"{v.get('systolic', 'N/A')}/{v.get('diastolic', 'N/A')}",
                    str(v.get('heartrate', 'N/A'))
                ])
            
            v_table = Table(vitals_data, colWidths=[150, 200, 100])
            v_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(v_table)
        else:
            elements.append(Paragraph("No vitals data available.", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Prescriptions
        elements.append(Paragraph("Current Prescriptions", styles['Heading2']))
        prescriptions = report_data.get('prescriptions', [])
        if prescriptions:
            for p in prescriptions:
                text = f"<b>{p.get('medication', 'Unknown')}</b> - {p.get('dosage', '')} ({p.get('frequency', '')})<br/>" \
                       f"Duration: {p.get('duration_days', '')} days<br/>" \
                       f"Instructions: {p.get('instructions', 'None')}"
                elements.append(Paragraph(text, styles['Normal']))
                elements.append(Spacer(1, 5))
        else:
            elements.append(Paragraph("No prescriptions found.", styles['Normal']))
        elements.append(Spacer(1, 10))

        # Appointments
        elements.append(Paragraph("Upcoming Appointments", styles['Heading2']))
        appointments = report_data.get('appointments', [])
        if appointments:
            for a in appointments:
                date_val = a.get('date', 'TBD')
                time_val = a.get('time', '')
                text = f"<b>{date_val} {time_val}</b> - {a.get('reason', '')} (Status: {a.get('status', '')})"
                elements.append(Paragraph(text, styles['Normal']))
                elements.append(Spacer(1, 5))
        else:
            elements.append(Paragraph("No upcoming appointments.", styles['Normal']))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
