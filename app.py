import streamlit as st
import pandas as pd
from analysis import analyze_cashflow, generate_ai_insights, generate_expense_pie, create_pdf
from io import BytesIO

st.set_page_config(page_title="SMB Cash Flow Dashboard", layout="wide")
st.title("SMB Cash Flow Dashboard")
st.markdown("Upload your transaction CSV to get insights, metrics, and a PDF report.")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Show detected columns (optional)
        st.write("Detected Columns:", df.columns.tolist())

        summary = analyze_cashflow(df)

        # Dashboard metrics
        st.markdown("<b>Financial Summary</b>", unsafe_allow_html=True)
        with st.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Income", f"${summary['total_income']:,.2f}")
            col2.metric("Total Expenses", f"${summary['total_expenses']:,.2f}")
            col3.metric("Net Cash Flow", f"${summary['net_cashflow']:,.2f}")

            pie_buf = generate_expense_pie(summary['expense_breakdown'])
            st.image(pie_buf, use_column_width=True)

        # AI Insights
        st.markdown("<b>AI Insights</b>", unsafe_allow_html=True)
        insights = generate_ai_insights(summary)
        st.write(insights)

        # PDF download
        st.markdown("<b>Download Report</b>", unsafe_allow_html=True)
        pdf_bytes = create_pdf(summary, insights, pie_buf)

        st.download_button(
            label="Download PDF",
            data=pdf_bytes,  # Pass raw bytes directly
            file_name="financial_report.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")


