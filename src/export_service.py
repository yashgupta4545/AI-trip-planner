"""Export service generating PDF, CSV, and JSON representations of planned trips.
Uses ReportLab for PDF generation and standard library for CSV/JSON.
"""

import io
import json
import csv
from typing import Any, Dict
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def export_trip_to_json(trip_data: Dict[str, Any]) -> str:
    """Return formatted JSON string of full trip."""
    return json.dumps(trip_data, indent=2, ensure_ascii=False)


def export_itinerary_to_csv(itinerary: Dict[str, Any]) -> str:
    """Generate CSV string of the day-by-day itinerary activities."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Day Number", "Date", "Day Theme", "Time Slot",
        "Activity Title", "Description", "Duration (Hours)", "Estimated Ticket (INR)"
    ])

    for day in itinerary.get("days", []):
        day_num = day.get("day_number", 1)
        day_date = day.get("date", "")
        day_theme = day.get("theme", "")
        for act in day.get("activities", []):
            writer.writerow([
                day_num,
                day_date,
                day_theme,
                act.get("slot", ""),
                act.get("title", ""),
                act.get("description", ""),
                act.get("duration_hours", 0.0),
                act.get("ticket_cost_inr", 0.0)
            ])

    return output.getvalue()


def export_trip_to_pdf(itinerary: Dict[str, Any], budget: Dict[str, Any] = None) -> bytes:
    """Generate a clean, printable PDF document using ReportLab."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TripTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0d9488"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "TripSub",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        "TripH2",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        "TripBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    bold_style = ParagraphStyle(
        "TripBold",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a")
    )

    elements = []

    # Title Banner
    dest_name = itinerary.get("destination_name", "Destination")
    country = itinerary.get("country", "")
    duration = itinerary.get("duration_days", 3)
    elements.append(Paragraph(f"TripGenie AI - Itinerary: {dest_name}, {country}", title_style))
    elements.append(Paragraph(
        f"Trip Duration: {duration} Days | Style: {itinerary.get('travel_style', 'Moderate')} | Pace: {itinerary.get('pace', 'Balanced')} | Generated: {itinerary.get('start_date', '')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))

    # Day-by-Day Schedule Table
    elements.append(Paragraph("Day-by-Day Travel Schedule", h2_style))
    elements.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("Day", bold_style),
            Paragraph("Time & Slot", bold_style),
            Paragraph("Activity & Plan", bold_style),
            Paragraph("Est. Ticket", bold_style)
        ]
    ]

    for day in itinerary.get("days", []):
        day_num = day.get("day_number", 1)
        for act in day.get("activities", []):
            cost_str = f"INR {act.get('ticket_cost_inr', 0):,.0f}" if act.get('ticket_cost_inr', 0) > 0 else "Free / Incl."
            table_data.append([
                Paragraph(f"Day {day_num}", body_style),
                Paragraph(f"{act.get('slot')}<br/><font color='#64748b' size='7'>{act.get('time')}</font>", body_style),
                Paragraph(f"<b>{act.get('title')}</b><br/><font color='#475569' size='8'>{act.get('description')}</font>", body_style),
                Paragraph(cost_str, body_style)
            ])

    schedule_table = Table(table_data, colWidths=[45, 95, 320, 80])
    schedule_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ccfbf1")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(schedule_table)
    elements.append(Spacer(1, 14))

    # Budget Overview Section
    if budget and "breakdown" in budget:
        elements.append(Paragraph("Estimated Expense Breakdown", h2_style))
        elements.append(Spacer(1, 4))

        b_data = [
            [Paragraph("Category", bold_style), Paragraph("Estimated Amount (INR)", bold_style)]
        ]
        for cat, amt in budget.get("breakdown", {}).items():
            b_data.append([
                Paragraph(cat, body_style),
                Paragraph(f"INR {amt:,.2f}", body_style)
            ])
        b_data.append([
            Paragraph("<b>Total Estimated Cost</b>", bold_style),
            Paragraph(f"<b>INR {budget.get('total_estimated_cost_inr', 0):,.2f}</b>", bold_style)
        ])
        b_data.append([
            Paragraph("<b>Per-Person Cost</b>", bold_style),
            Paragraph(f"<b>INR {budget.get('per_person_cost_inr', 0):,.2f}</b>", bold_style)
        ])

        budget_table = Table(b_data, colWidths=[300, 240])
        budget_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        elements.append(budget_table)

    # Footer note
    elements.append(Spacer(1, 14))
    elements.append(Paragraph(
        "<font color='#94a3b8' size='7'>TripGenie AI - Your Journey. Your Budget. Your Adventure. "
        "Estimated costs and schedules are subject to seasonal changes and provider terms.</font>",
        body_style
    ))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


def export_budget_to_csv(budget: Dict[str, Any]) -> str:
    """Generate CSV string of the itemized budget breakdown and assumptions."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["TripGenie AI - Travel Budget Estimate"])
    writer.writerow(["Destination", budget.get("destination_name", "")])
    writer.writerow(["Country", budget.get("country", "")])
    writer.writerow(["Starting Location", budget.get("origin_city", "")])
    writer.writerow(["Duration (Days)", budget.get("num_days", 0)])
    writer.writerow(["Travelers", budget.get("num_travelers", 0)])
    writer.writerow(["Total Estimated Cost (INR)", budget.get("total_estimated_cost_inr", 0)])
    writer.writerow(["Cost per Traveler (INR)", budget.get("per_person_cost_inr", 0)])
    writer.writerow([])
    writer.writerow(["Expense Category", "Estimated Amount (INR)"])

    for cat, amt in budget.get("breakdown", {}).items():
        writer.writerow([cat, amt])

    writer.writerow([])
    writer.writerow(["Assumptions & Notes"])
    for asm in budget.get("assumptions", []):
        writer.writerow([asm])

    return output.getvalue()


def export_budget_to_pdf(budget: Dict[str, Any]) -> bytes:
    """Generate a clean printable PDF representation of the budget calculation."""
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BudgetTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0d9488"),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        "BudgetSub",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12
    )
    bold_style = ParagraphStyle(
        "BudgetBold",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a")
    )
    body_style = ParagraphStyle(
        "BudgetBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )

    elements = []
    dest_name = budget.get("destination_name", "Destination")
    country = budget.get("country", "")
    days = budget.get("num_days", 3)
    pax = budget.get("num_travelers", 1)

    elements.append(Paragraph(f"TripGenie AI - Budget Estimate: {dest_name}, {country}", title_style))
    elements.append(Paragraph(
        f"Origin: {budget.get('origin_city', 'N/A')} | Duration: {days} Days | Travelers: {pax} | Total: INR {budget.get('total_estimated_cost_inr', 0):,.2f}",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))

    b_data = [[Paragraph("Expense Category", bold_style), Paragraph("Estimated Cost (INR)", bold_style)]]
    for cat, amt in budget.get("breakdown", {}).items():
        b_data.append([Paragraph(cat, body_style), Paragraph(f"INR {amt:,.2f}", body_style)])
    
    b_data.append([Paragraph("<b>Total Estimated Trip Cost</b>", bold_style), Paragraph(f"<b>INR {budget.get('total_estimated_cost_inr', 0):,.2f}</b>", bold_style)])
    b_data.append([Paragraph("<b>Cost per Traveler</b>", bold_style), Paragraph(f"<b>INR {budget.get('per_person_cost_inr', 0):,.2f}</b>", bold_style)])

    b_table = Table(b_data, colWidths=[320, 220])
    b_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ccfbf1")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(b_table)
    elements.append(Spacer(1, 14))

    elements.append(Paragraph("<b>Assumptions & Guidance:</b>", bold_style))
    for asm in budget.get("assumptions", []):
        elements.append(Paragraph(f"• {asm}", body_style))

    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
