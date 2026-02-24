import streamlit as st
import pandas as pd
from analysis import analyze_cashflow, generate_ai_insights, generate_expense_pie, create_pdf
from io import BytesIO

st.set_page_config(page_title="SMB Cash Flow Dashboard", layout="wide")

st.title("SMB Cash Flow Dashboard")
st.markdown("Upload your transaction CSV to get insights, metrics, and a PDF report.")

# -----------------------------
# Section 1: File Upload
# -----------------------------
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        # Read CSV into DataFrame
        df = pd.read_csv(uploaded_file)

        # Section 2: Dashboard Metrics + Pie Chart
        summary = analyze_cashflow(df)

        st.markdown("<b>Financial Summary</b>", unsafe_allow_html=True)
        with st.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"${summary['total_income']:,.2f}")
            col2.metric("Total Expenses", f"${summary['total_expenses']:,.2f}")
            col3.metric("Net Cash Flow", f"${summary['net_cashflow']:,.2f}")

            # Pie chart
            pie_buf = generate_expense_pie(summary['expense_breakdown'])
            st.image(pie_buf, use_column_width=True)

        # Section 3: AI Insights
        st.markdown("<b>AI Insights</b>", unsafe_allow_html=True)
        insights = generate_ai_insights(summary)
        st.write(insights)

        # Section 4: Download PDF
        st.markdown("<b>Download Report</b>", unsafe_allow_html=True)
        pdf_buffer = create_pdf(summary, insights, pie_buf)
        st.download_button(
            label="Download PDF",
            data=open(pdf_buffer, "rb").read(),
            file_name="financial_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")
