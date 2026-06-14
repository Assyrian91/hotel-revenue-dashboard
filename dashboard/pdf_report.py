from fpdf import FPDF
from datetime import datetime
import pandas as pd
import io

class HotelPDF(FPDF):
    def __init__(self, author: str = "Khoshaba Odeesho"):
        super().__init__()
        self.author_name = author
        self.set_margins(18, 18, 18)
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        # Dark header bar
        self.set_fill_color(10, 14, 26)
        self.rect(0, 0, 210, 18, "F")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(201, 168, 76)
        self.set_xy(10, 5)
        self.cell(0, 8, "HOTEL REVENUE INTELLIGENCE  ·  CONFIDENTIAL", align="L")
        self.set_text_color(100, 110, 130)
        self.set_xy(10, 5)
        self.cell(0, 8, f"Generated {datetime.now().strftime('%d %b %Y')}", align="R")

    def footer(self):
        self.set_y(-14)
        self.set_fill_color(10, 14, 26)
        self.rect(0, 283, 210, 14, "F")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(80, 90, 110)
        self.cell(0, 10, f"© {datetime.now().year} {self.author_name}  ·  Page {self.page_no()}", align="C")

    def gold_line(self):
        self.set_draw_color(201, 168, 76)
        self.set_line_width(0.5)
        self.line(18, self.get_y(), 192, self.get_y())
        self.set_line_width(0.2)
        self.set_draw_color(200, 200, 200)
        self.ln(4)

    def section_title(self, title: str):
        self.ln(6)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(201, 168, 76)
        self.cell(0, 8, title, ln=True)
        self.gold_line()

    def kpi_card_row(self, kpis: list):
        """kpis = list of (label, value, delta) tuples, max 4"""
        card_w = (210 - 36 - (len(kpis)-1)*4) / len(kpis)
        x_start = 18
        y = self.get_y()
        for i, (label, value, delta) in enumerate(kpis):
            x = x_start + i * (card_w + 4)
            # card bg
            self.set_fill_color(17, 24, 39)
            self.set_draw_color(201, 168, 76)
            self.set_line_width(0.3)
            self.rect(x, y, card_w, 24, "FD")
            # label
            self.set_font("Helvetica", "", 7)
            self.set_text_color(201, 168, 76)
            self.set_xy(x+3, y+3)
            self.cell(card_w-6, 5, label.upper(), ln=True)
            # value
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(245, 240, 232)
            self.set_xy(x+3, y+9)
            self.cell(card_w-6, 7, str(value), ln=True)
            # delta
            self.set_font("Helvetica", "", 7)
            self.set_text_color(16, 185, 129)
            self.set_xy(x+3, y+17)
            self.cell(card_w-6, 5, str(delta), ln=True)
        self.set_xy(18, y + 28)

    def data_table(self, headers: list, rows: list, col_widths: list = None):
        if not col_widths:
            col_widths = [(210-36) / len(headers)] * len(headers)
        # Header row
        self.set_fill_color(17, 24, 39)
        self.set_text_color(201, 168, 76)
        self.set_font("Helvetica", "B", 8)
        for h, w in zip(headers, col_widths):
            self.cell(w, 7, h, border="B", fill=True, align="C")
        self.ln()
        # Data rows
        self.set_font("Helvetica", "", 8)
        for i, row in enumerate(rows):
            self.set_fill_color(13, 17, 32) if i % 2 == 0 else self.set_fill_color(17, 24, 39)
            self.set_text_color(200, 210, 220)
            for val, w in zip(row, col_widths):
                self.cell(w, 6, str(val), fill=True, align="C")
            self.ln()
        self.ln(3)


def generate_pdf_report(
    monthly_df: pd.DataFrame,
    channel_df: pd.DataFrame,
    forecast_df: pd.DataFrame | None,
    ai_insight: str,
    title: str,
    period: str,
    author: str = "Khoshaba Odeesho"
) -> bytes:

    pdf = HotelPDF(author=author)
    pdf.set_creator(author)
    pdf.add_page()

    # ── Cover block ──────────────────────────────────────────────
    pdf.set_fill_color(10, 14, 26)
    pdf.rect(0, 18, 210, 55, "F")
    pdf.set_text_color(201, 168, 76)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_xy(18, 26)
    pdf.cell(0, 12, title.upper(), ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(138, 154, 181)
    pdf.set_x(18)
    pdf.cell(0, 7, f"Prepared by {author}  ·  Period: {period}", ln=True)
    pdf.set_x(18)
    pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%A, %d %B %Y at %H:%M')}", ln=True)
    pdf.set_fill_color(201, 168, 76)
    pdf.rect(18, 66, 174, 0.8, "F")
    pdf.set_xy(18, 74)

    # ── KPI Scorecard ────────────────────────────────────────────
    pdf.section_title("Executive KPI Scorecard")
    latest = monthly_df.iloc[-1]
    prev   = monthly_df.iloc[-2] if len(monthly_df) > 1 else latest
    pdf.kpi_card_row([
        ("Occupancy Rate",  f"{latest['occupancy_rate']:.1f}%",  f"{latest['occupancy_rate']-prev['occupancy_rate']:+.1f}% MoM"),
        ("ADR",             f"${latest['adr']:,.2f}",             f"${latest['adr']-prev['adr']:+.2f} MoM"),
        ("RevPAR",          f"${latest['revpar']:,.2f}",          f"${latest['revpar']-prev['revpar']:+.2f} MoM"),
        ("Total Revenue",   f"${latest['total_revenue']:,.0f}",   f"${latest['total_revenue']-prev['total_revenue']:+,.0f} MoM"),
    ])

    # ── Monthly KPI table ────────────────────────────────────────
    pdf.section_title("Monthly KPI Breakdown")
    headers = ["Month", "Occupancy %", "ADR ($)", "RevPAR ($)", "Revenue ($)"]
    widths  = [36, 35, 35, 35, 33]
    rows = [
        [r["month"],
         f"{r['occupancy_rate']:.1f}%",
         f"${r['adr']:,.2f}",
         f"${r['revpar']:,.2f}",
         f"${r['total_revenue']:,.0f}"]
        for _, r in monthly_df.iterrows()
    ]
    pdf.data_table(headers, rows, widths)

    # ── Channel table ────────────────────────────────────────────
    pdf.section_title("Booking Channel Performance")
    ch_headers = ["Channel", "Bookings", "Revenue ($)", "Avg Rate ($)", "Avg Stay"]
    ch_widths  = [45, 30, 38, 35, 26]
    ch_rows = [
        [r["booking_channel"],
         f"{int(r['total_bookings']):,}",
         f"${r['total_revenue']:,.0f}",
         f"${r['avg_rate']:,.2f}",
         f"{r['avg_stay']:.1f} nights"]
        for _, r in channel_df.iterrows()
    ]
    pdf.data_table(ch_headers, ch_rows, ch_widths)

    # ── Forecast snapshot ────────────────────────────────────────
    if forecast_df is not None:
        pdf.section_title("90-Day Revenue Forecast")
        future = forecast_df[forecast_df["date"] > pd.to_datetime(monthly_df["month"].iloc[-1] + "-01")]
        f_headers = ["Date", "RevPAR Forecast ($)", "Occupancy Forecast (%)", "ADR Forecast ($)"]
        f_widths  = [42, 48, 50, 34]
        f_rows = [
            [r["date"].strftime("%B %Y"),
             f"${r['revpar']:,.2f}",
             f"{r['occupancy_rate']:.1f}%",
             f"${r['adr']:,.2f}"]
            for _, r in future.head(6).iterrows()
        ]
        pdf.data_table(f_headers, f_rows, f_widths)

    # ── AI Insight ───────────────────────────────────────────────
    if ai_insight:
        pdf.section_title("AI Revenue Intelligence (Groq · Llama 3.1)")
        pdf.set_fill_color(17, 24, 39)
        pdf.set_draw_color(201, 168, 76)
        pdf.set_line_width(0.4)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.rect(18, y, 174, 4, "F")   # gold top bar
        pdf.set_fill_color(201, 168, 76)
        pdf.rect(18, y, 174, 1.5, "F")
        pdf.set_fill_color(13, 17, 32)
        pdf.rect(18, y+1.5, 174, 42, "F")
        pdf.set_xy(22, y+5)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(200, 210, 220)
        pdf.multi_cell(166, 5.5, ai_insight)
        pdf.ln(6)

    # ── Signature ────────────────────────────────────────────────
    pdf.set_text_color(80, 90, 110)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 6, f"This report was generated by {author}'s Hotel Revenue Intelligence Dashboard.", ln=True, align="C")

    buffer = io.BytesIO()
    pdf_bytes = pdf.output()
    return bytes(pdf_bytes)