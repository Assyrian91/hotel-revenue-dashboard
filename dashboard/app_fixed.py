import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
from kpis.calculate import get_monthly_kpis, get_channel_kpis, get_daily_kpis
from forecasting.narrative import get_kpi_insight, ask_data_question
from forecasting.forecast import run_forecast
from dashboard.pdf_report import generate_pdf_report

st.set_page_config(
    page_title="Hotel Revenue Intelligence | Khoshaba Odeesho",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
  html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #0a0e1a !important; }
  [data-testid="stSidebar"] { background: linear-gradient(180deg, #080c18 0%, #0d1425 100%) !important; border-right: 1px solid rgba(201,168,76,0.2); }
  [data-testid="stHeader"] { background: transparent !important; }
  html, body, * { font-family: 'Inter', sans-serif; color: #e8dcc8; }
  h1, h2, h3 { font-family: 'Playfair Display', serif !important; }
  [data-testid="stMetric"] { background: linear-gradient(135deg, #111827 0%, #1a2235 100%); border: 1px solid rgba(201,168,76,0.27); border-radius: 12px; padding: 1.1rem 1.3rem; box-shadow: 0 4px 24px rgba(0,0,0,0.27), inset 0 1px 0 rgba(201,168,76,0.13); }
  [data-testid="stMetric"] label { color: #c9a84c !important; font-size: 11px !important; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 500; }
  [data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 600 !important; color: #f5f0e8 !important; }
  [data-testid="stTabs"] button { color: #8a9ab5 !important; border-bottom: 2px solid transparent !important; font-size: 13px; letter-spacing: .5px; }
  [data-testid="stTabs"] button[aria-selected="true"] { color: #c9a84c !important; border-bottom: 2px solid #c9a84c !important; }
  [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #8a9ab5 !important; }
  [data-testid="stSidebar"] .stSelectbox > div, [data-testid="stSidebar"] .stMultiSelect > div { background: #111827 !important; border: 1px solid rgba(201,168,76,0.2) !important; border-radius: 8px; }
  [data-testid="stButton"] > button { background: linear-gradient(135deg, #c9a84c, #a07c2a) !important; color: #0a0e1a !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; letter-spacing: .5px; padding: .5rem 1.5rem !important; }
  [data-testid="stButton"] > button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(201,168,76,0.27) !important; }
  [data-testid="stChatInput"] textarea { background: #111827 !important; border: 1px solid rgba(201,168,76,0.27) !important; color: #e8dcc8 !important; border-radius: 10px !important; }
  [data-testid="stChatMessage"] { background: #111827 !important; border: 1px solid #1e2d45 !important; border-radius: 12px !important; }
  hr { border-color: rgba(201,168,76,0.13) !important; }
  .section-title { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #c9a84c; border-bottom: 1px solid rgba(201,168,76,0.2); padding-bottom: .4rem; margin: 1.5rem 0 1rem; }
  .author-badge { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: rgba(201,168,76,0.6); font-weight: 500; }
  .kpi-def { background: #111827; border-left: 3px solid #c9a84c; border-radius: 0 8px 8px 0; padding: .7rem 1rem; font-size: 13px; color: #8a9ab5; margin-bottom: .5rem; }
</style>
""", unsafe_allow_html=True)

GOLD = "#c9a84c"
BLUE = "#3b82f6"
GREEN = "#10b981"
PURPLE = "#8b5cf6"
RED = "#ef4444"
COLORS = [GOLD, BLUE, GREEN, PURPLE, RED, "#f59e0b"]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0d1120",
    font=dict(color="#8a9ab5", family="Inter", size=12),
    title_font=dict(color="#e8dcc8", family="Playfair Display", size=16),
    xaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45", tickcolor="#1e2d45"),
    yaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45", tickcolor="#1e2d45"),
    margin=dict(l=10, r=10, t=40, b=10),
)

LEGEND_STYLE = dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(201,168,76,0.13)", borderwidth=1)

@st.cache_data(ttl=3600)
def load_all():
    monthly = get_monthly_kpis()
    channel = get_channel_kpis()
    daily = get_daily_kpis()
    if not os.path.exists("data/processed/forecast_output.csv"):
        run_forecast(90)
    forecast = pd.read_csv("data/processed/forecast_output.csv")
    forecast["date"] = pd.to_datetime(forecast["date"])
    return monthly, channel, daily, forecast

monthly_df, channel_df, daily_df, forecast_df = load_all()

with st.sidebar:
    st.markdown('<p style="font-family:Playfair Display;font-size:22px;color:#c9a84c;font-weight:700;">👑 Hotel Intel</p>', unsafe_allow_html=True)
    st.markdown('<p class="author-badge">by Khoshaba Odeesho</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p style="color:#c9a84c;font-size:12px;letter-spacing:1px;text-transform:uppercase;font-weight:600;">Filters</p>', unsafe_allow_html=True)
    year_filter = st.selectbox("Year", ["All", "2020", "2021", "2022", "2023", "2024", "2025"])
    room_filter = st.multiselect(
        "Room Types",
        ["Standard", "Deluxe", "Suite", "Executive"],
        default=["Standard", "Deluxe", "Suite", "Executive"]
    )
    st.markdown("---")
    st.markdown('<p style="color:#c9a84c;font-size:12px;letter-spacing:1px;text-transform:uppercase;font-weight:600;">Features</p>', unsafe_allow_html=True)
    show_forecast = st.toggle("90-Day Forecast", value=True)
    show_chatbot = st.toggle("AI Data Chatbot", value=False)
    show_pdf = st.toggle("PDF Report Builder", value=False)
    st.markdown("---")
    st.markdown('<p style="color:#555f7a;font-size:11px;">Hotel Revenue Intelligence<br>© 2024 Khoshaba Odeesho<br>Python · Streamlit · Groq AI</p>', unsafe_allow_html=True)

mdf = monthly_df.copy()
if year_filter != "All":
    mdf = mdf[mdf["month"].str.startswith(year_filter)]

ddf = daily_df.copy()
if room_filter:
    ddf = ddf[ddf["room_type"].isin(room_filter)]

st.markdown("""
<div style="padding:1.5rem 0 .5rem">
  <p class="author-badge" style="margin-bottom:.3rem">Khoshaba Odeesho · Data & Analytics</p>
  <h1 style="font-family:Playfair Display;font-size:36px;color:#f5f0e8;margin:0;font-weight:700;line-height:1.2">
      Hotel Revenue<br><span style="color:#c9a84c">Intelligence Dashboard</span>
  </h1>
  <p style="color:#555f7a;font-size:14px;margin-top:.6rem">
      End-to-end KPI tracking · 90-day AI forecast · Groq-powered insights · Executive PDF reporting
  </p>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

st.markdown('<div class="section-title">📊 Performance Scorecard</div>', unsafe_allow_html=True)

latest = mdf.iloc[-1]
prev = mdf.iloc[-2] if len(mdf) > 1 else latest

c1, c2, c3, c4 = st.columns(4)
c1.metric("Occupancy Rate", f"{latest['occupancy_rate']:.1f}%", f"{latest['occupancy_rate']-prev['occupancy_rate']:+.1f}% MoM")
c2.metric("ADR", f"${latest['adr']:,.2f}", f"${latest['adr']-prev['adr']:+.2f} MoM")
c3.metric("RevPAR", f"${latest['revpar']:,.2f}", f"${latest['revpar']-prev['revpar']:+.2f} MoM")
c4.metric("Total Revenue", f"${latest['total_revenue']:,.0f}", f"${latest['total_revenue']-prev['total_revenue']:+,.0f} MoM")

c5, c6, c7, c8 = st.columns(4)
total_bookings = int(channel_df["total_bookings"].sum())
best_channel = channel_df.iloc[0]["booking_channel"]
best_channel_rev = channel_df.iloc[0]["total_revenue"]
revpar_trend = "▲ Growing" if mdf["revpar"].iloc[-1] > mdf["revpar"].iloc[-3] else "▼ Declining"
avg_daily_rooms = round(ddf.groupby("date")["rooms_sold"].sum().mean(), 0) if "rooms_sold" in ddf.columns else 0

c5.metric("Total Bookings", f"{total_bookings:,}", "2-year total")
c6.metric("Top Channel", best_channel, f"${best_channel_rev:,.0f} revenue")
c7.metric("RevPAR Trend", revpar_trend, "vs 3 months ago")
c8.metric("Avg Rooms/Day", f"{avg_daily_rooms:,.0f}", "sold daily")

with st.expander("📖 KPI Definitions & Formulas"):
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown('<div class="kpi-def"><strong style="color:#c9a84c">Occupancy Rate</strong><br>Rooms Sold ÷ Rooms Available × 100<br><em>Measures demand strength</em></div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi-def"><strong style="color:#c9a84c">ADR — Avg Daily Rate</strong><br>Total Room Revenue ÷ Rooms Sold<br><em>Measures pricing power</em></div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="kpi-def"><strong style="color:#c9a84c">RevPAR</strong><br>ADR × Occupancy Rate<br><em>Overall revenue efficiency</em></div>', unsafe_allow_html=True)

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Trends", "🏠 Room Analysis", "🌡️ Heatmaps", "🔗 Channels", "🔮 Forecast"
])

with tab1:
    st.markdown('<div class="section-title">KPI Trends Over Time</div>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=mdf["month"], y=mdf["revpar"], fill="tozeroy", name="RevPAR", line=dict(color=GOLD, width=2.5), fillcolor="rgba(201,168,76,0.12)"))
    fig.update_layout(title="RevPAR — Monthly Trend", height=280, legend=LEGEND_STYLE, **CHART_LAYOUT)
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=mdf["month"], y=mdf["occupancy_rate"], mode="lines+markers", name="Occupancy %", line=dict(color=BLUE, width=2), marker=dict(size=5, color=BLUE)))
        fig2.update_layout(title="Occupancy Rate (%)", height=260, legend=LEGEND_STYLE, **CHART_LAYOUT)
        st.plotly_chart(fig2, width="stretch")
    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=mdf["month"], y=mdf["adr"], name="ADR", marker_color=GOLD, opacity=0.85))
        fig3.update_layout(title="Average Daily Rate ($)", height=260, legend=LEGEND_STYLE, **CHART_LAYOUT)
        st.plotly_chart(fig3, width="stretch")

    fig4 = go.Figure(go.Bar(
        x=mdf["month"], y=mdf["total_revenue"],
        marker=dict(
            color=mdf["total_revenue"],
            colorscale=[
                [0.0, "rgb(30,45,69)"],
                [0.5, "rgb(180,140,60)"],
                [1.0, "rgb(201,168,76)"]
            ],
            showscale=False
        ), name="Revenue"
    ))
    fig4.update_layout(title="Monthly Total Revenue ($)", height=260, legend=LEGEND_STYLE, **CHART_LAYOUT)
    st.plotly_chart(fig4, width="stretch")

with tab2:
    st.markdown('<div class="section-title">Room Type Performance</div>', unsafe_allow_html=True)
    room_kpis = ddf.groupby("room_type").agg(rooms_sold=("rooms_sold","sum"), total_revenue=("total_revenue","sum"), avg_occ=("occupancy_rate","mean"), avg_adr=("adr","mean"), avg_revpar=("revpar","mean")).reset_index()
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(room_kpis, x="room_type", y="avg_revpar", color="room_type", color_discrete_sequence=COLORS, title="RevPAR by Room Type ($)")
        fig.update_layout(showlegend=False, height=300, legend=LEGEND_STYLE, **CHART_LAYOUT)
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig2 = px.scatter(room_kpis, x="avg_occ", y="avg_adr", size="total_revenue", color="room_type", color_discrete_sequence=COLORS, title="Occupancy vs ADR — Bubble = Revenue", labels={"avg_occ":"Occupancy %","avg_adr":"ADR ($)"})
        fig2.update_layout(height=300, legend=LEGEND_STYLE, **CHART_LAYOUT)
        st.plotly_chart(fig2, width="stretch")

    fig3 = px.pie(room_kpis, names="room_type", values="total_revenue", color_discrete_sequence=COLORS, title="Revenue Share by Room Type", hole=0.5)
    fig3.update_traces(textfont_color="#e8dcc8")
    fig3.update_layout(height=300, legend=LEGEND_STYLE, **CHART_LAYOUT)
    st.plotly_chart(fig3, width="stretch")

    st.markdown('<div class="section-title" style="font-size:16px">Detailed Room KPI Table</div>', unsafe_allow_html=True)
    display = room_kpis.copy()
    display.columns = ["Room Type","Rooms Sold","Total Revenue ($)","Avg Occupancy (%)","Avg ADR ($)","Avg RevPAR ($)"]
    display["Total Revenue ($)"] = display["Total Revenue ($)"].map("${:,.0f}".format)
    display["Avg Occupancy (%)"] = display["Avg Occupancy (%)"].map("{:.1f}%".format)
    display["Avg ADR ($)"] = display["Avg ADR ($)"].map("${:,.2f}".format)
    display["Avg RevPAR ($)"] = display["Avg RevPAR ($)"].map("${:,.2f}".format)
    st.dataframe(display, width="stretch", hide_index=True)

with tab3:
    st.markdown('<div class="section-title">Occupancy Heatmaps</div>', unsafe_allow_html=True)
    hdf = ddf.copy()
    hdf["date"] = pd.to_datetime(hdf["date"])
    hdf["day_of_week"] = hdf["date"].dt.day_name()
    hdf["month_num"] = hdf["date"].dt.month

    pivot = hdf.groupby(["month_num","day_of_week"])["occupancy_rate"].mean().reset_index()
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    pivot_table = pivot.pivot(index="day_of_week", columns="month_num", values="occupancy_rate")
    pivot_table = pivot_table.reindex(day_order)
    pivot_table.columns = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    fig_heat = px.imshow(
        pivot_table,
        color_continuous_scale=[
            [0.00, "rgb(13,17,32)"],
            [0.40, "rgb(30,58,95)"],
            [0.75, "rgb(180,140,60)"],
            [1.00, "rgb(201,168,76)"]
        ],
        title="Average Occupancy Rate by Day of Week × Month (%)",
        aspect="auto", text_auto=".0f"
    )
    fig_heat.update_layout(height=380, legend=LEGEND_STYLE, coloraxis_colorbar=dict(title="Occ %", tickfont=dict(color="#8a9ab5")), **CHART_LAYOUT)
    fig_heat.update_traces(textfont=dict(color="#e8dcc8", size=11))
    st.plotly_chart(fig_heat, width="stretch")

    hdf2 = ddf.copy()
    hdf2["date"] = pd.to_datetime(hdf2["date"])
    hdf2["month"] = hdf2["date"].dt.strftime("%b %Y")
    piv2 = hdf2.groupby(["room_type","month"])["revpar"].mean().reset_index()
    piv2_table = piv2.pivot(index="room_type", columns="month", values="revpar")

    fig_heat2 = px.imshow(
        piv2_table,
        color_continuous_scale=[
            [0.0, "rgb(13,17,32)"],
            [0.5, "rgb(30,58,95)"],
            [1.0, "rgb(201,168,76)"]
        ],
        title="RevPAR by Room Type × Month ($)",
        aspect="auto", text_auto=".0f"
    )
    fig_heat2.update_layout(height=300, legend=LEGEND_STYLE, coloraxis_colorbar=dict(title="RevPAR $", tickfont=dict(color="#8a9ab5")), **CHART_LAYOUT)
    fig_heat2.update_traces(textfont=dict(color="#e8dcc8", size=11))
    st.plotly_chart(fig_heat2, width="stretch")

with tab4:
    st.markdown('<div class="section-title">Booking Channel Intelligence</div>', unsafe_allow_html=True)
    ch_vals = channel_df["total_revenue"].tolist()
    ch_max = max(ch_vals)
    ch_colors = [f"rgba(201,168,76,{0.4 + 0.6*(v/ch_max):.2f})" for v in ch_vals]

    c1, c2 = st.columns(2)
    with c1:
        fig_ch = go.Figure(go.Bar(y=channel_df["booking_channel"], x=channel_df["total_revenue"], orientation="h", marker_color=ch_colors, name="Revenue"))
        fig_ch.update_layout(title="Total Revenue by Channel ($)", height=320, showlegend=False, legend=LEGEND_STYLE, **CHART_LAYOUT)
        st.plotly_chart(fig_ch, width="stretch")
    with c2:
        fig2 = px.scatter(channel_df, x="avg_stay", y="avg_rate", size="total_bookings", color="booking_channel", color_discrete_sequence=COLORS, title="Avg Stay vs Avg Rate — Bubble = Bookings", labels={"avg_stay":"Avg Stay (nights)","avg_rate":"Avg Rate ($)"})
        fig2.update_layout(height=320, legend=LEGEND_STYLE, **CHART_LAYOUT)
        st.plotly_chart(fig2, width="stretch")

    st.markdown('<div class="section-title" style="font-size:16px">Channel KPI Table</div>', unsafe_allow_html=True)
    ch_display = channel_df.copy()
    ch_display.columns = ["Channel","Total Bookings","Total Revenue ($)","Avg Rate ($)","Avg Stay (nights)"]
    ch_display["Total Revenue ($)"] = ch_display["Total Revenue ($)"].map("${:,.0f}".format)
    ch_display["Avg Rate ($)"] = ch_display["Avg Rate ($)"].map("${:,.2f}".format)
    st.dataframe(ch_display, width="stretch", hide_index=True)

with tab5:
    st.markdown('<div class="section-title">90-Day AI Forecast (Facebook Prophet)</div>', unsafe_allow_html=True)
    if show_forecast:
        metric_map = {"RevPAR ($)":"revpar","Occupancy Rate (%)":"occupancy_rate","ADR ($)":"adr"}
        metric_label = st.selectbox("Metric to forecast", list(metric_map.keys()))
        m = metric_map[metric_label]
        hist = mdf[["month", m]].copy()
        hist["date"] = pd.to_datetime(hist["month"] + "-01")
        fcast = forecast_df[forecast_df["date"] > hist["date"].max()].copy()
        fig_f = go.Figure()
        if f"{m}_low" in fcast.columns:
            fig_f.add_trace(go.Scatter(x=pd.concat([fcast["date"], fcast["date"][::-1]]), y=pd.concat([fcast[f"{m}_high"], fcast[f"{m}_low"][::-1]]), fill="toself", fillcolor="rgba(201,168,76,0.08)", line=dict(color="rgba(0,0,0,0)"), name="Confidence band"))
        fig_f.add_trace(go.Scatter(x=hist["date"], y=hist[m], name="Historical", line=dict(color=BLUE, width=2.5)))
        fig_f.add_trace(go.Scatter(x=fcast["date"], y=fcast[m], name="Forecast", line=dict(color=GOLD, width=2.5, dash="dash")))
        fig_f.update_layout(
            title=f"{metric_label} — Historical + 90-Day Forecast",
            height=420,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(0,0,0,0)", bordercolor="rgba(201,168,76,0.13)", borderwidth=1),
            **CHART_LAYOUT
        )
        st.plotly_chart(fig_f, width="stretch")
        st.markdown("**Forecast values — next 6 months**")
        preview = fcast[["date", m]].copy()
        preview.columns = ["Date", metric_label]
        preview["Date"] = preview["Date"].dt.strftime("%B %Y")
        st.dataframe(preview.head(6), width="stretch", hide_index=True)
    else:
        st.info("Enable '90-Day Forecast' in the sidebar to view forecasts.")

st.markdown("---")
st.markdown('<div class="section-title">🤖 AI Revenue Intelligence</div>', unsafe_allow_html=True)
_, col_btn = st.columns([5, 1])
with col_btn:
    run_insight = st.button("Generate Insight")
if run_insight:
    with st.spinner("Analysing your KPIs with Groq AI (Llama 3.1)..."):
        try:
            insight = get_kpi_insight(mdf)
            st.markdown(f'<div style="background:linear-gradient(135deg,#111827,#1a2235); border:1px solid rgba(201,168,76,0.27); border-left:4px solid #c9a84c; border-radius:10px; padding:1.2rem 1.5rem; color:#e8dcc8; font-size:14px; line-height:1.8;"><span style="color:#c9a84c; font-weight:600; font-size:12px; letter-spacing:1px; text-transform:uppercase;">AI Insight — Khoshaba Odeesho Revenue Dashboard</span><br><br>{insight}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Groq API error: {e}")

st.markdown("---")
if show_chatbot:
    st.markdown('<div class="section-title">💬 Ask Your Data (AI Chatbot)</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#555f7a;font-size:13px">Ask anything about the KPIs. Try: "Which month had the highest RevPAR?" or "Compare OTA vs Direct revenue."</p>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👑" if msg["role"] == "assistant" else "🧑"):
            st.markdown(msg["content"])
    if prompt := st.chat_input("Ask about your hotel data..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="👑"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_data_question(prompt, mdf, channel_df)
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("---")

if show_pdf:
    st.markdown('<div class="section-title">📄 Executive PDF Report</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#555f7a;font-size:13px">Generate a branded executive PDF report with all KPIs, tables, and AI insights.</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        report_title = st.text_input("Report Title", "Hotel Revenue Intelligence Report")
        report_period = st.text_input("Reporting Period", f"{year_filter} — All Months")
    with col2:
        include_ai = st.checkbox("Include AI Insight in report", value=True)
        include_fore = st.checkbox("Include Forecast data", value=True)
    if st.button("📄 Generate PDF Report"):
        with st.spinner("Generating executive PDF..."):
            try:
                ai_text = get_kpi_insight(mdf) if include_ai else ""
                pdf_bytes = generate_pdf_report(monthly_df=mdf, channel_df=channel_df, forecast_df=forecast_df if include_fore else None, ai_insight=ai_text, title=report_title, period=report_period, author="Khoshaba Odeesho")
                st.download_button(label="⬇️ Download PDF Report", data=pdf_bytes, file_name=f"hotel_revenue_report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf")
                st.success("PDF generated successfully!")
            except Exception as e:
                st.error(f"PDF error: {e}")

st.markdown('<div style="text-align:center;padding:2rem 0 1rem;color:#2a3550;font-size:12px;letter-spacing:.5px">HOTEL REVENUE INTELLIGENCE DASHBOARD · DESIGNED & BUILT BY <span style="color:#c9a84c">KHOSHABA ODEESHO</span> · PYTHON · STREAMLIT · GROQ AI · PROPHET</div>', unsafe_allow_html=True)
