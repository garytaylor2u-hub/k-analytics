# csv_analyzer_pro.py
# The ultimate one-click CSV analyzer: Profile + Graph + AI Insights + Plain-English Summary

import pandas as pd
import matplotlib.pyplot as plt
from ydata_profiling import ProfileReport
import os
import json

# ================== CHOOSE YOUR AI BACKEND ==================
# Options: "openai", "gemini", "grok"
BACKEND = "grok"        # ← change this one line to switch
# =============================================================

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
XAI_API_KEY    = os.getenv("XAI_API_KEY")

# Load data
csv_file = 'sales_with_forecast.csv'
df = pd.read_csv(csv_file)

# === 1. Professional Interactive Profile Report ===
print("Generating full interactive profile report...")
profile = ProfileReport(
    df,
    title="Data Quality & Insights Report",
    explorative=True,
    minimal=False,
    correlations={"auto": {"calculate": True}},
    missing_diagrams={"heatmap": True, "dendrogram": True},
    interactions={"continuous": True}
)
profile.to_file("data_profile_report.html")
print("Interactive report saved → data_profile_report.html (open in browser!)")

# === 2. Quick Console Summary ===
print("\n" + "="*70)
print("QUICK STATS SUMMARY")
print("="*70)
print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
print(f"Memory: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
print(f"Missing values: {df.isnull().sum().sum():,}")
print(f"Duplicate rows: {df.duplicated().sum():,}")
print(f"Data types:\n{df.dtypes.value_counts()}")
print("="*70)

# === 3. Actual vs Forecast Graph ===
df['Date'] = pd.to_datetime(df['Date'])
plt.figure(figsize=(10, 6))
actual = df[df['Scenario'] == 'Actual']
forecast = df[df['Scenario'] == 'Forecast']
plt.plot(actual['Date'], actual['Sales'], 'o-', label='Actual', color='blue', linewidth=2)
plt.plot(forecast['Date'], forecast['Sales'], 's--', label='Forecast', color='green', linewidth=2)
plt.title('Sales: Actual vs Forecast', fontsize=16)
plt.xlabel('Date')
plt.ylabel('Sales')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('sales_forecast_graph.png', dpi=300, bbox_inches='tight')
# plt.show()  # Comment out when running from cmd
plt.close()

# === 4. AI Explains the ENTIRE Profile Report in Plain English ===
def explain_profile_in_english():
    profile_json = json.loads(profile.to_json())
    prompt = f"""
    You are an expert data analyst speaking to a business leader.
    Here is the full technical profile of a dataset (JSON format).
    Summarize the TOP 5 most important data quality insights in plain, non-technical English.
    Highlight anything that would worry or surprise a manager.

    JSON:
    {json.dumps(profile_json, indent=2)[:15000]}
    """
    if BACKEND == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=400, temperature=0.3)
        return resp.choices[0].message.content.strip()

    elif BACKEND == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        resp = model.generate_content(prompt)
        return resp.text.strip()

    elif BACKEND == "grok":
        from xai_sdk import Client
        from xai_sdk.chat import user, system
        client = Client(api_key=XAI_API_KEY)
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are a world-class data analyst. Be concise, blunt, and helpful."))
        chat.append(user(prompt))
        resp = chat.sample()
        return resp.content.strip()

print("\n" + "="*70)
print(f"ASKING {BACKEND.upper()} TO EXPLAIN THE DATA PROFILE IN PLAIN ENGLISH")
print("="*70)
english_summary = explain_profile_in_english()
print(english_summary)

# === 5. Regular AI Insights on Sales Trends ===
def get_sales_insights():
    sample = df.to_dict(orient='records')[-8:]
    prompt = f"""
    Analyze this sales data (actual + forecast):
    {sample}
    In 3-4 short bullet points:
    - How do actual sales compare to early trend?
    - Is the forecast optimistic, conservative, or on track?
    - Any challenges or opportunities?
    Be concise.
    """
    if BACKEND == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=200, temperature=0.5)
        return resp.choices[0].message.content.strip()
    elif BACKEND == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        resp = model.generate_content(prompt)
        return resp.text.strip()
    elif BACKEND == "grok":
        from xai_sdk import Client
        from xai_sdk.chat import user, system
        client = Client(api_key=XAI_API_KEY)
        chat = client.chat.create(model="grok-4")
        chat.append(system("Be concise, truthful, and a bit fun."))
        chat.append(user(prompt))
        resp = chat.sample()
        return resp.content.strip()

print("\n" + "="*70)
print(f"ASKING {BACKEND.upper()} FOR SALES TREND INSIGHTS")
print("="*70)
sales_insights = get_sales_insights()
print(sales_insights)