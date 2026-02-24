# analysis.py

import pandas as pd
from openai import OpenAI
import os

# Initialize OpenAI client safely using environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_cashflow(file_path):
    """
    Reads a CSV of transactions and calculates financial metrics.
    
    CSV should have columns:
    date, description, amount, category
    """
    df = pd.read_csv(file_path)

    # Calculate revenue, expenses, net cash flow
    total_revenue = df[df["amount"] > 0]["amount"].sum()
    total_expenses = df[df["amount"] < 0]["amount"].sum()
    net_cash_flow = total_revenue + total_expenses

    # Expense breakdown by category
    expense_breakdown = (
        df[df["amount"] < 0]
        .groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .to_dict()
    )

    # Identify top expense category
    top_expense_category = max(expense_breakdown, key=expense_breakdown.get)

    # Convert all numeric types to plain Python int for readability
    summary = {
        "total_revenue": int(total_revenue),
        "total_expenses": int(abs(total_expenses)),
        "net_cash_flow": int(net_cash_flow),
        "top_expense_category": top_expense_category,
        "expense_breakdown": {k: int(v) for k, v in expense_breakdown.items()}
    }

    return summary


def generate_ai_insights(summary):
    """
    Generates AI-driven financial insights based on metrics.
    """
    prompt = f"""
You are a financial analyst advising a small business owner.

Based on the following metrics:
Total Revenue: ${summary['total_revenue']}
Total Expenses: ${summary['total_expenses']}
Net Cash Flow: ${summary['net_cash_flow']}
Top Expense Category: {summary['top_expense_category']}
Expense Breakdown: {summary['expense_breakdown']}

Generate:
1. A concise cash flow summary (3-4 sentences)
2. Two potential financial risks
3. Three actionable optimization recommendations

Keep it clear and practical.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    # Analyze CSV
    summary = analyze_cashflow("sample_transactions.csv")
    print("=== Summary Metrics ===")
    print(summary)

    # Generate AI insights
    insights = generate_ai_insights(summary)
    print("\n=== AI Insights ===")
    print(insights)