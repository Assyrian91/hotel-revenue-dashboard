import os
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

def _client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_kpi_insight(kpi_df: pd.DataFrame) -> str:
    latest = kpi_df.tail(4).to_string(index=False)
    prompt = f"""
You are a senior hotel revenue manager analyst for a luxury property.
Here are the last 4 months of KPI data:

{latest}

Columns: month | occupancy_rate (%) | adr ($) | revpar ($) | total_revenue ($)

Write a sharp, executive-level insight in exactly 4 sentences:
1. Overall performance trend with specific numbers.
2. Biggest strength observed in the data.
3. The most critical risk or underperformance area.
4. One concrete, revenue-maximizing action the GM should take this week.

Be direct. Use real numbers from the data. No generic advice. No bullet points.
"""
    r = _client().chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}],
        max_tokens=280, temperature=0.35
    )
    return r.choices[0].message.content.strip()


def ask_data_question(question: str, monthly_df: pd.DataFrame, channel_df: pd.DataFrame) -> str:
    monthly_str = monthly_df.tail(12).to_string(index=False)
    channel_str = channel_df.to_string(index=False)

    prompt = f"""
You are an expert hotel revenue analyst AI assistant for Khoshaba Odeesho's Hotel Revenue Intelligence Dashboard.

You have access to the following data:

MONTHLY KPIs (last 12 months):
{monthly_str}

CHANNEL PERFORMANCE:
{channel_str}

User question: {question}

Answer the question directly using the data above. Be specific with numbers.
If the question cannot be answered from this data, say so clearly.
Keep your answer concise (3-5 sentences max) and professional.
"""
    r = _client().chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":prompt}],
        max_tokens=350, temperature=0.3
    )
    return r.choices[0].message.content.strip()