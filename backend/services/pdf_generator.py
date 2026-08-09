import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def format_currency(amount: float) -> str:
    return f"Rs. {amount:,.2f}"

def format_date_display(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d %B %Y")
    except Exception:
        return date_str

def generate_daily_pdf(date_str: str, stats: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=8
    )
    normal_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.whitesmoke
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    story = []
    
    # Header Title
    formatted_date = format_date_display(date_str)
    story.append(Paragraph("DAILY CUSTOMER ORDER REPORT", title_style))
    story.append(Paragraph(f"Date: {formatted_date}", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))
    
    # Summary Metrics Cards Table
    metrics_data = [
        [
            Paragraph("<b>Total Orders</b>", styles['Normal']),
            Paragraph("<b>Verified Orders</b>", styles['Normal']),
            Paragraph("<b>Pending Orders</b>", styles['Normal']),
            Paragraph("<b>Rejected Orders</b>", styles['Normal']),
            Paragraph("<b>Total Sales</b>", styles['Normal']),
        ],
        [
            Paragraph(f"<font size=14 color='#1E293B'><b>{stats['total_orders']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#16A34A'><b>{stats['verified']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#D97706'><b>{stats['pending']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#DC2626'><b>{stats['rejected']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#2563EB'><b>{format_currency(stats['total_sales'])}</b></font>", styles['Normal']),
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[100, 100, 100, 100, 140])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Orders Detail Section
    story.append(Paragraph("Order Details List", section_style))
    
    orders = stats.get("orders", [])
    if not orders:
        story.append(Paragraph("<i>No orders recorded for this date.</i>", subtitle_style))
    else:
        table_data = [
            [
                Paragraph("ID", normal_style),
                Paragraph("Customer Name", normal_style),
                Paragraph("Phone", normal_style),
                Paragraph("Tracking ID", normal_style),
                Paragraph("Product Code", normal_style),
                Paragraph("Product Name", normal_style),
                Paragraph("Amount", normal_style),
                Paragraph("Status", normal_style),
            ]
        ]
        
        for o in orders:
            order_id = f"#{o.get('id', 0):03d}"
            status_color = "#16A34A" if o.get('status') == 'Verified' else ("#D97706" if o.get('status') == 'Pending' else "#DC2626")
            status_p = Paragraph(f"<font color='{status_color}'><b>{o.get('status')}</b></font>", cell_style)
            
            table_data.append([
                Paragraph(order_id, cell_style),
                Paragraph(str(o.get('customer_name', '')), cell_style),
                Paragraph(str(o.get('phone', '')), cell_style),
                Paragraph(str(o.get('tracking_id', '')), cell_style),
                Paragraph(str(o.get('product_code', '')), cell_style),
                Paragraph(str(o.get('product_name', '')), cell_style),
                Paragraph(format_currency(float(o.get('amount', 0))), cell_style),
                status_p
            ])
            
        orders_table = Table(table_data, colWidths=[40, 95, 75, 75, 60, 95, 55, 45])
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(orders_table)
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_weekly_pdf(start_date_str: str, end_date_str: str, stats: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=6
    )
    normal_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.whitesmoke
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#334155')
    )

    story = []
    
    # Header Title
    date_range_txt = f"{format_date_display(start_date_str)}  to  {format_date_display(end_date_str)}"
    story.append(Paragraph("WEEKLY CUSTOMER ORDER REPORT", title_style))
    story.append(Paragraph(f"Date Range: {date_range_txt}", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))
    
    # Summary Metrics Table
    metrics_data = [
        [
            Paragraph("<b>Total Orders</b>", styles['Normal']),
            Paragraph("<b>Verified Orders</b>", styles['Normal']),
            Paragraph("<b>Pending Orders</b>", styles['Normal']),
            Paragraph("<b>Rejected Orders</b>", styles['Normal']),
            Paragraph("<b>Total Sales</b>", styles['Normal']),
        ],
        [
            Paragraph(f"<font size=14 color='#1E293B'><b>{stats['total_orders']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#16A34A'><b>{stats['verified']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#D97706'><b>{stats['pending']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#DC2626'><b>{stats['rejected']}</b></font>", styles['Normal']),
            Paragraph(f"<font size=14 color='#2563EB'><b>{format_currency(stats['total_sales'])}</b></font>", styles['Normal']),
        ]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[100, 100, 100, 100, 140])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Daily Breakdown Table
    story.append(Paragraph("Daily Performance Breakdown", section_style))
    daily_breakdown = stats.get("daily_breakdown", [])
    
    if not daily_breakdown:
        story.append(Paragraph("<i>No orders recorded in this date range.</i>", subtitle_style))
    else:
        breakdown_data = [
            [
                Paragraph("Date", normal_style),
                Paragraph("Total Orders", normal_style),
                Paragraph("Daily Sales Amount", normal_style)
            ]
        ]
        for b in daily_breakdown:
            breakdown_data.append([
                Paragraph(format_date_display(b["date"]), cell_style),
                Paragraph(str(b["orders"]), cell_style),
                Paragraph(format_currency(b["sales"]), cell_style)
            ])
            
        bd_table = Table(breakdown_data, colWidths=[200, 140, 200])
        bd_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(bd_table)
        
    story.append(Spacer(1, 20))
    
    # Orders Detail List
    story.append(Paragraph("Complete Orders List", section_style))
    orders = stats.get("orders", [])
    if not orders:
        story.append(Paragraph("<i>No detailed orders available.</i>", subtitle_style))
    else:
        table_data = [
            [
                Paragraph("ID", normal_style),
                Paragraph("Date", normal_style),
                Paragraph("Customer", normal_style),
                Paragraph("Tracking ID", normal_style),
                Paragraph("Product", normal_style),
                Paragraph("Amount", normal_style),
                Paragraph("Status", normal_style),
            ]
        ]
        
        for o in orders:
            order_id = f"#{o.get('id', 0):03d}"
            status_color = "#16A34A" if o.get('status') == 'Verified' else ("#D97706" if o.get('status') == 'Pending' else "#DC2626")
            status_p = Paragraph(f"<font color='{status_color}'><b>{o.get('status')}</b></font>", cell_style)
            
            table_data.append([
                Paragraph(order_id, cell_style),
                Paragraph(str(o.get('order_date', '')), cell_style),
                Paragraph(str(o.get('customer_name', '')), cell_style),
                Paragraph(str(o.get('tracking_id', '')), cell_style),
                Paragraph(str(o.get('product_name', '')), cell_style),
                Paragraph(format_currency(float(o.get('amount', 0))), cell_style),
                status_p
            ])
            
        orders_table = Table(table_data, colWidths=[35, 65, 110, 85, 125, 70, 50])
        orders_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        story.append(orders_table)
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
