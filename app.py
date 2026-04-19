import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="BD Intelligence OS", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {background-color:#0e1117;color:white;}
.block {background:#1c1f26;padding:20px;border-radius:15px;}
.title {font-size:36px;font-weight:700;}
.metric {font-size:24px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 BD Intelligence OS (No API)</div>', unsafe_allow_html=True)

# ---------- NAV ----------
page = st.sidebar.selectbox("Navigation", [
    "Dashboard",
    "Analyze Company",
    "Pipeline",
    "Add Company",
    "Executive View"
])

# ---------- STORAGE ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["name","industry","score","probability","status"])

df = st.session_state.data

# ---------- SCRAPER ----------
def get_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text().lower()
        return text[:5000]
    except:
        return ""

# ---------- ANALYSIS ENGINE ----------
def analyze_text(text):

    keywords = {
        "growth": ["growth","scale","expansion","increase"],
        "tech": ["ai","platform","software","technology"],
        "market": ["market","global","region","gulf","mena"],
        "partnership": ["partner","collaboration","alliance"],
        "funding": ["funding","investment","series","capital"]
    }

    score = 50

    signals = {}

    for k, words in keywords.items():
        count = sum([len(re.findall(w, text)) for w in words])
        signals[k] = count

    score += signals["growth"] * 2
    score += signals["partnership"] * 3
    score += signals["market"] * 1.5
    score += signals["tech"] * 2

    score = min(score, 100)

    probability = int(score * 0.9)

    return score, probability, signals

# ---------- STRATEGY ENGINE ----------
def generate_strategy(signals):

    if signals["growth"] > 5:
        return "High growth → propose expansion partnership"

    if signals["funding"] > 3:
        return "Recently funded → pitch scaling support"

    if signals["tech"] > 5:
        return "Tech driven → integration partnership"

    return "General BD outreach recommended"

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.subheader("📊 Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Companies", len(df))
    col2.metric("High Score", len(df[df["score"] > 80]))
    col3.metric("Avg Score", int(df["score"].mean()) if not df.empty else 0)

    if not df.empty:
        st.dataframe(df.sort_values(by="score", ascending=False))

# ---------- ANALYZE ----------
elif page == "Analyze Company":

    st.subheader("🔍 Company Analysis")

    name = st.text_input("Company Name")
    website = st.text_input("Website URL")

    if st.button("Analyze"):

        st.info("Scraping website...")

        text = get_text(website)

        score, prob, signals = analyze_text(text)

        strategy = generate_strategy(signals)

        st.success("Analysis Complete")

        st.metric("Score", score)
        st.metric("Probability", f"{prob}%")

        st.write("### Signals")
        st.json(signals)

        st.write("### Strategy")
        st.success(strategy)

        st.write("### Suggested Outreach Email")
        st.code(f"""
Subject: Partnership Opportunity with {name}

We see strong growth and expansion signals in your company.
We would like to explore collaboration opportunities.

Best,
BD Team
""")

        # save
        new = pd.DataFrame([{
            "name": name,
            "industry": "Unknown",
            "score": score,
            "probability": prob,
            "status": "New"
        }])

        st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- PIPELINE ----------
elif page == "Pipeline":

    st.subheader("📈 BD Pipeline")

    if not df.empty:
        status = st.selectbox("Filter", ["All","New","Contacted","Negotiation"])

        if status != "All":
            filtered = df[df["status"] == status]
        else:
            filtered = df

        st.dataframe(filtered)

# ---------- ADD ----------
elif page == "Add Company":

    st.subheader("➕ Add Company")

    name = st.text_input("Name")
    industry = st.text_input("Industry")

    if st.button("Add"):
        new = pd.DataFrame([{
            "name": name,
            "industry": industry,
            "score": 60,
            "probability": 50,
            "status": "New"
        }])

        st.session_state.data = pd.concat([df, new], ignore_index=True)
        st.success("Added")

# ---------- EXEC ----------
elif page == "Executive View":

    st.subheader("🚀 Executive Insights")

    if not df.empty:

        top = df.sort_values(by="score", ascending=False).head(5)

        for _, row in top.iterrows():
            st.markdown(f"### {row['name']}")
            st.write(f"Score: {row['score']}")
            st.write(f"Probability: {row['probability']}%")

            if row["score"] > 80:
                st.success("🔥 High Priority Deal")
            else:
                st.info("Standard Opportunity")
