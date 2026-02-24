import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from openai import OpenAI

# ----------------------------
# Load OpenAI API Key
# ----------------------------
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is not set. "
        "If running locally, set your environment variable. "
        "If deployed, add it to Streamlit Secrets."
    )
client = OpenAI(api_key=api_key)

# ----------------------------
# Auto-detect CSV columns
# ----------------------------
def detect_columns(df: pd.DataFrame):
    df_cols = [c.strip().lower() for c in df.columns]
    column_mapping = {}
    possible_matches = {
        "date": ["date", "transaction date", "txn_date", "day"],
        "category": ["category", "type", "expense type", "cat"],
        "amount": ["amount", "amt", "value", "debit", "credit"]
    }

    for logical_name, variants in possible_matches.items():
        for variant in variants:
            if variant.lower() in df_cols:
                column_mapping[logical_name] = df.columns[df_cols.index(variant.lower())]
                break
        else:
            raise ValueError(f"Could not detect column for: {logical_name}")

    return column_mapping

# ----------------------------
# Financial Analysis
# ----------------------------
def analyze_cashflow(df: pd.DataFrame):
    mapping = detect_columns(df)
    amount_col = mapping["amount"]
    category_col = mapping["category"]
    date_col = mapping["date"]

    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce")

    total_income = df[df[amount_col] > 0][amount_col].sum()
    total_expenses = df[df[amount_col] < 0][amount_col].sum()
    net_cashflow = total_income + total_expenses

    expense_breakdown = (
        df[df[amount_col] < 0]
        .groupby(df[category_col])[amount_col]
        .sum()
        .abs()
        .sort_values(ascending=False)
    )

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cashflow": net_cashflow,
        "expense_breakdown": expense_breakdown
    }

# ----------------------------
# AI Insight Generator
# ----------------------------
def generate_ai_insights(summary: dict):
    prompt = f"""
You are a financial analyst advising a small business owner.

Total Income: ${summary['total_income']:,.2f}
Total Expenses: ${summary['total_expenses']:,.2f}
Net Cash Flow: ${summary['net_cashflow']:,.2f}

Top Expense Categories:
{summary['expense_breakdown'].to_string()}

Provide:
1. Short overall financial health summary
2. One risk or concern
3. One actionable recommendation
Keep it concise and professional.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strategic financial advisor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# ----------------------------
# Generate Pie Chart
# ----------------------------
def generate_expense_pie(expense_breakdown: pd.Series):
    fig, ax = plt.subplots()
    ax.pie(
        expense_breakdown,
        labels=expense_breakdown.index,
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Expense Breakdown by Category")
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    return buf

# ----------------------------
# Create PDF Report
# ----------------------------
def create_pdf(summary: dict, insights: str, pie_buffer: BytesIO):
    pdf_buffer = BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Financial Summary", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Total Income: ${summary['total_income']:,.2f}", ln=True)
    pdf.cell(0, 8, f"Total Expenses: ${summary['total_expenses']:,.2f}", ln=True)
    pdf.cell(0, 8, f"Net Cash Flow: ${summary['net_cashflow']:,.2f}", ln=True)
    pdf.ln(5)

    pdf.cell(0, 8, "AI Insights:", ln=True)
    pdf.multi_cell(0, 8, insights)
    pdf.ln(5)

    # Save pie chart image to PDF
    pie_buffer.seek(0)
    pdf.image(pie_buffer, x=None, y=None, w=150)

    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer


