# app.py - Final polished portfolio-ready dashboard with spacing fix

import streamlit as st
from analysis import analyze_cashflow, generate_ai_insights
import tempfile
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# -----------------------------
# Page config and font styling
# -----------------------------
st.set_page_config(page_title="SMB Cash Flow Dashboard", layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-card {
        background-color: #F5F5F5;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Page Title
# -----------------------------
st.title("SMB Cash Flow Insight Dashboard")
st.markdown("Upload a CSV of your business transactions to view key metrics, expense breakdown, and AI insights.")

# -----------------------------
# Section 1: CSV Upload
# -----------------------------
st.markdown("<b>Upload Transactions CSV</b>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    st.markdown("<hr>", unsafe_allow_html=True)

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # -----------------------------
    # Section 2: Dashboard Metrics + Pie Chart
    # -----------------------------
    summary = analyze_cashflow(tmp_path)

    st.markdown("<b>Financial Summary</b>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns([1,1])

        # --- Left Column: Metrics container matching pie chart height ---
        with col1:
            st.markdown(
                f"<div style='background-color:#F5F5F5; padding:20px; border-radius:10px; "
                f"box-shadow:2px 2px 8px rgba(0,0,0,0.1); min-height:400px; margin-bottom:20px'>"
                f"<h3 style='font-weight:bold;'>Total Revenue</h3><h2>${summary['total_revenue']:,}</h2>"
                f"<h3 style='font-weight:bold;'>Total Expenses</h3><h2>${summary['total_expenses']:,}</h2>"
                f"<h3 style='font-weight:bold;'>Net Cash Flow</h3><h2>${summary['net_cash_flow']:,}</h2>"
                f"<h3 style='font-weight:bold;'>Top Expense Category</h3><h2>{summary['top_expense_category']}</h2>"
                f"</div>", unsafe_allow_html=True
            )

        # --- Right Column: Interactive Pie Chart ---
        with col2:
            df_pie = pd.DataFrame({
                "Category": list(summary["expense_breakdown"].keys()),
                "Amount": list(summary["expense_breakdown"].values())
            })
            colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3']
            fig = px.pie(df_pie, names="Category", values="Amount",
                         color_discrete_sequence=colors,
                         title="Expense Breakdown")
            st.plotly_chart(fig, width='stretch')

    # Add spacing below metrics container to prevent overlap
    st.markdown("<div style='margin-bottom:30px'></div>", unsafe_allow_html=True)

    # -----------------------------
    # Section 3: AI Insights
    # -----------------------------
    st.markdown("<b>AI Insights</b>", unsafe_allow_html=True)
    with st.spinner("Generating insights..."):
        insights = generate_ai_insights(summary)
        st.write(insights)

    # -----------------------------
    # Section 4: Download Full PDF Report
    # -----------------------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SMB Cash Flow Report", ln=True, align='C')
    pdf.ln(10)

    # Metrics
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 6,
                   f"Financial Summary:\n"
                   f"Total Revenue: ${summary['total_revenue']:,}\n"
                   f"Total Expenses: ${summary['total_expenses']:,}\n"
                   f"Net Cash Flow: ${summary['net_cash_flow']:,}\n"
                   f"Top Expense Category: {summary['top_expense_category']}\n\n")

    # Pie chart image
    chart_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.write_image(chart_file.name)  # Save Plotly figure as PNG
    pdf.image(chart_file.name, x=30, w=150)
    pdf.ln(10)

    # AI Insights
    safe_insights = insights.encode('latin-1', errors='replace').decode('latin-1')
    pdf.multi_cell(0, 6, "AI Insights:\n" + safe_insights)

    # Save PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_file.name)

    st.download_button(
        label="Download Full PDF Report",
        data=open(pdf_file.name, "rb").read(),
        file_name="smb_cashflow_report.pdf",
        mime="application/pdf"
    )