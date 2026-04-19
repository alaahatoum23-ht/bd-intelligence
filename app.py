import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Alaa BD", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {
    background-color:#0e1117;
    color:white;
}
.header {
    font-size:42px;
    font-weight:800;
    margin-bottom:10px;
}
.sub {
    color:#aaa;
    margin-bottom:30px;
}
.card {
    background:#1c1f26;
    padding:20px;
    border-radius:16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.metric {
    font-size:28px;
    font-weight:700;
}
.small {
    color:#888;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="header">🚀 Alaa BD</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Business Development Intelligence System</div>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
page = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "🔍 Analyze",
    "📈 Pipeline",
    "🧠 Executive"
])

# ---------- DATA ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["name","score","probability","status"])

df = st.session_state.data

# ---------- SCRAPER ----------
def get_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(res.text, "html.parser")

        texts = []
        for tag in soup.find_all(["p","h1","h2","h3"]):
            texts.append(tag.get_text())

        return " ".join(texts).lower()[:8000]
    except:
        return ""

# ---------- ANALYSIS ----------
def analyze_text(text):
    growth = len(re.findall(r"(growth|scale|expand|launch)", text))
    funding = len(re.findall(r"(funding|investment|series|capital)", text))
    market = len(re.findall(r"(mena|gcc|global|market)", text))
    tech = len(re.findall(r"(ai|platform|software|tech)", text))
    partnership = len(re.findall(r"(partner|collaborate|alliance)", text))

    score = min(growth*4 + funding*5 + partnership*6 + tech*3 + market*2, 100)

    probability = min(int((growth*2 + funding*3 + partnership*3 + tech + market)*2), 95)

    return score, probability, {
        "growth": growth,
        "funding": funding,
        "market": market,
        "tech": tech,
        "partnership": partnership
    }

# ---------- STRATEGY ----------
def generate_strategy(signals):
    if signals["funding"] > 5:
        return "🚀 High funding → scaling partnership"
    if signals["growth"] > 5:
        return "📈 Growth → expansion deal"
    if signals["tech"] > 5:
        return "🧠 Tech → integration partnership"
    if signals["partnership"] > 3:
        return "🤝 Open → direct outreach"
    return "📩 General BD approach"

# ---------- DASHBOARD ----------
if page == "📊 Dashboard":

    st.markdown("## Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card"><div class="metric">'+str(len(df))+'</div><div class="small">Companies</div></div>', unsafe_allow_html=True)

    with col2:
        high = len(df[df["score"] > 80]) if not df.empty else 0
        st.markdown(f'<div class="card"><div class="metric">{high}</div><div class="small">High Opportunities</div></div>', unsafe_allow_html=True)

    with col3:
        avg = int(df["score"].mean()) if not df.empty else 0
        st.markdown(f'<div class="card"><div class="metric">{avg}</div><div class="small">Average Score</div></div>', unsafe_allow_html=True)

    st.markdown("## Top Companies")

    if not df.empty:
        st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)
    else:
        st.info("No data yet")

# ---------- ANALYZE ----------
elif page == "🔍 Analyze":

    st.markdown("## Company Analysis")

    name = st.text_input("Company Name")
    website = st.text_input("Website")

    if st.button("Run Analysis"):

        text = get_text(website)

        if text.strip() == "":
            st.error("❌ Failed to fetch data")
        else:
            score, prob, signals = analyze_text(text)
            strategy = generate_strategy(signals)

            st.markdown("### Results")

            c1, c2 = st.columns(2)

            c1.metric("Score", score)
            c2.metric("Probability", f"{prob}%")

            st.markdown("### Signals")
            st.json(signals)

            st.markdown("### Strategy")
            st.success(strategy)

            st.markdown("### Outreach Email")
            st.code(f"""
Subject: Partnership with {name}

We identified strong potential for collaboration.
Let's explore opportunities together.

Best,
BD Team
""")

            new = pd.DataFrame([{
                "name": name,
                "score": score,
                "probability": prob,
                "status": "New"
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- PIPELINE ----------
elif page == "📈 Pipeline":

    st.markdown("## Deal Pipeline")

    if not df.empty:
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
            <b>{row['name']}</b><br>
            Score: {row['score']} | Probability: {row['probability']}%
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No deals yet")

# ---------- EXECUTIVE ----------
elif page == "🧠 Executive":

    st.markdown("## Executive Insights")

    if not df.empty:
        top = df.sort_values(by="score", ascending=False).head(5)

        for _, row in top.iterrows():
            st.markdown(f"""
            <div class="card">
            <h3>{row['name']}</h3>
            Score: {row['score']}<br>
            Probability: {row['probability']}%
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No insights yet")
