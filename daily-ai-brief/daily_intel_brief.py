# daily_intel_brief.py — Final Edition with Fixes
import streamlit as st
import feedparser
from datetime import datetime
import os

st.set_page_config(page_title="AI Daily Brief", page_icon="🧠", layout="centered")

# Backend
BACKEND = st.sidebar.selectbox("AI Engine", ["grok", "openai", "gemini"], index=0)

# Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

st.title("🧠 Your Personal AI Intelligence Brief")
st.caption(f"Today • {datetime.now():%A, %B %d, %Y}")

# Persona
st.sidebar.header("Who You Are")
role = st.sidebar.selectbox("Your role", ["CEO / Founder", "Investor", "Data Leader", "Product Manager", "Analyst", "Journalist", "Engineer", "Curious Human"], index=1)
focus = st.sidebar.multiselect("What you care about", ["AI & Tech", "Markets & Finance", "Politics", "Geopolitics", "Climate & Energy", "Startups", "Health", "Culture"], default=["AI & Tech", "Markets & Finance"])
depth = st.sidebar.slider("Depth level", 1, 5, 3, help="1 = quick scan • 5 = deep implications")

# Sources (expanded with free/no-paywall)
sources = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Google News (Top)": "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "NPR (U.S.)": "https://feeds.npr.org/1001/rss.xml"
}
source_name = st.sidebar.selectbox("Source", list(sources.keys()))
feed_url = sources[source_name]

if st.sidebar.button("Generate My Brief", type="primary", use_container_width=True):
    with st.spinner(f"Fetching real news from {source_name} and briefing {BACKEND.upper()}..."):
        feed = feedparser.parse(feed_url)
        entries = feed.entries[:25]
        headlines = [e.title for e in entries if hasattr(e, 'title')]
        links = [e.link for e in entries if hasattr(e, 'link')]

        def get_brief():
            prompt = f"""
            You are a world-class intelligence analyst briefing a {role}.
            Today is {datetime.now():%B %d, %Y}. Donald Trump is the current U.S. President.
            Primary focus: {', '.join(focus)}.

            Here are today's top real headlines from {source_name}:
            {chr(10).join(f'• {h}' for h in headlines)}

            Write a crisp, high-signal brief with exactly this format (use Markdown bold for story numbers/titles, but no extra asterisks — keep it clean):

            **1. [Headline]**

            Why it matters: [one sentence]

            Action: [one line]

            **2. [Headline]**

            Why it matters: ...

            Action: ...

            Only 3–5 stories. Tone: Senior advisor — direct, no fluff, slightly witty. Depth {depth}/5.
            """
            if BACKEND == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                resp = client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=600, temperature=0.4)
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
                chat.append(system("You are a world-class intelligence analyst. Be concise, blunt, and a little fun."))
                chat.append(user(prompt))
                return chat.sample().content.strip()

        brief = get_brief()

        st.success("Brief Ready")
        st.markdown(
    brief
    .replace("**", "<b>", 1)                    # first ** → <b>
    .replace("**", "</b>", 1)                   # second ** → </b>
    .replace("**", "<b>")                       # all remaining ** → <b>
    .replace("**", "</b>"), 
    unsafe_allow_html=True
)

        st.divider()
        with st.expander("Raw Headlines (click to expand)", expanded=False):
            for i, e in enumerate(entries, 1):
                h = e.title if hasattr(e, 'title') else "Untitled"
                link = e.link if hasattr(e, 'link') else "#"
                
                preview = ""
                if hasattr(e, 'content') and e.content:
                    preview = e.content[0].value[:140] + "..." if len(e.content[0].value) > 140 else e.content[0].value
                elif hasattr(e, 'summary') and e.summary:
                    preview = e.summary[:140] + "..."
                elif hasattr(e, 'description') and e.description:
                    preview = e.description[:140] + "..."
                else:
                    preview = "Read full article for details..."
                
                st.markdown(f"**{i}.** [{h}]({link})<br><small>{preview}</small>", unsafe_allow_html=True)

else:
    st.info("Configure your role & focus → click **Generate My Brief**")
    st.caption("Built with ❤️ using Streamlit + RSS + OpenAI/Gemini/Grok • November 2025")