import requests
from bs4 import BeautifulSoup
import os

# ================== CHOOSE YOUR AI BACKEND HERE ==================
# Options: "openai", "gemini", "grok"
BACKEND = "gemini"        # ← change this one line to switch
# =================================================================

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
XAI_API_KEY    = os.getenv("XAI_API_KEY")

# Choose your news source (Google News works great)
#url = "https://news.google.com"
url = "https://techcrunch.com/"

print(f"Fetching live headlines from {url}...")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Robust headline grabber with deduplication
headlines = []
seen_topics = set()

for tag in soup.find_all(['h3', 'h4', 'a'], class_=True):
    text = tag.get_text(strip=True)
    if text and 15 < len(text) < 250 and text not in headlines:
        words = set(w.lower() for w in text.split() if len(w) > 3)
        overlap = len(words & seen_topics) / len(words) if words else 0
        if overlap < 0.6:
            headlines.append(text)
            seen_topics.update(words)

headlines = headlines[:20]  # top 20 diverse stories

print("\nToday's top headlines:")
for i, h in enumerate(headlines, 1):
    print(f"{i:2}. {h}")

# Unified AI summarizer
def get_summary():
    headline_list = "\n".join(f"- {h}" for h in headlines)

    if BACKEND == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        try:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"""
                Today is November 29, 2025. Donald Trump is the current President of the United States.
                Here are today's top headlines:
                {headline_list}

                In 4-6 short bullet points, what are the biggest things happening in the world right now?
                Be factual and concise.
                """}],
                max_tokens=300,
                temperature=0.4
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI error: {e}"

    elif BACKEND == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')  # proven working free model
        prompt = f"""
        Today is November 29, 2025. Donald Trump is the current President.
        Here are today's top headlines:
        {headline_list}

        In 4-6 short bullet points, summarize the biggest global events.
        Be concise and factual.
        """
        try:
            resp = model.generate_content(prompt)
            return resp.text.strip()
        except Exception as e:
            return f"Gemini error: {e}"

    elif BACKEND == "grok":
        from xai_sdk import Client
        from xai_sdk.chat import user, system
        client = Client(api_key=XAI_API_KEY)
        chat = client.chat.create(model="grok-4")
        chat.append(system("You are Grok. Be concise, truthful, and a bit fun."))
        chat.append(user(f"""
        Today is November 29, 2025. Donald Trump is the current President.
        Here are today's top headlines:
        {headline_list}

        In 4-6 short bullet points, what are the biggest things happening in the world right now?
        """))
        try:
            resp = chat.sample()
            return resp.content.strip()
        except Exception as e:
            return f"Grok error: {e}"

    else:
        return "Invalid backend!"

# Run it
print(f"\nAsking {BACKEND.upper()} for today's summary...")
summary = get_summary()
print(f"\n{BACKEND.upper()} says:\n{summary}")