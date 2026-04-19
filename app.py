import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Alaa BD", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.main {background-color:#0f172a;}
.header {font-size:34px;font-weight:700;}
.card {
    background:#111827;
    padding:20px;
    border-radius:14px;
    margin-bottom:10px;
}
.metric {font-size:28px;font-weight:bold;}
.small {color:#9ca3af;}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="header">🚀 Alaa BD Platform</div>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Analyze",
    "Pipeline",
    "Insights"
])

# ---------- DATA ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["name","score","probability"])

df = st.session_state.data

# ---------- SCRAPER ----------
def get_text(url):
    try:
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=6)
        soup = BeautifulSoup(res.text, "html.parser")
        text = " ".join([t.get_text() for t in soup.find_all(["p","h1","h2","h3"])])
        return text.lower()[:8000]
    except:
        return ""

# ---------- ANALYSIS ----------
def analyze_text(text):

    signals = {
        "growth": len(re.findall(r"(growth|expand|scale|launch)", text)),
        "funding": len(re.findall(r"(funding|investment|series|capital)", text)),
        "tech": len(re.findall(r"(ai|platform|software|technology)", text)),
        "partnership": len(re.findall(r"(partner|collaboration|alliance)", text)),
        "market": len(re.findall(r"(mena|gcc|global|market)", text))
    }

    weights = {
        "growth": 4,
        "funding": 5,
        "tech": 3,
        "partnership": 6,
        "market": 2
    }

    score = 0
    explanation = []

    for key in signals:
        contribution = signals[key] * weights[key]
        score += contribution

        if signals[key] > 0:
            explanation.append(
                f"{key.upper()} detected ({signals[key]} mentions) → +{contribution} points"
            )

    score = min(score, 100)
    probability = min(int(score * 0.9), 95)

    return score, probability, signals, explanation

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.markdown("### Overview")

    c1, c2, c3 = st.columns(3)

    c1.markdown(f'<div class="card"><div class="metric">{len(df)}</div><div class="small">Companies</div></div>', unsafe_allow_html=True)

    high = len(df[df["score"] > 80]) if not df.empty else 0
    c2.markdown(f'<div class="card"><div class="metric">{high}</div><div class="small">High Value</div></div>', unsafe_allow_html=True)

    avg = int(df["score"].mean()) if not df.empty else 0
    c3.markdown(f'<div class="card"><div class="metric">{avg}</div><div class="small">Avg Score</div></div>', unsafe_allow_html=True)

    if not df.empty:
        st.dataframe(df.sort_values(by="score", ascending=False), use_container_width=True)

# ---------- ANALYZE ----------
elif page == "Analyze":

    st.markdown("### Analyze Company")

    name = st.text_input("Company")
    url = st.text_input("Website")

    if st.button("Analyze"):

        text = get_text(url)

        if text == "":
            st.error("❌ Failed to fetch data")
        else:
            score, prob, signals, explanation = analyze_text(text)

            st.success("Analysis Complete")

            col1, col2 = st.columns(2)
            col1.metric("Score", score)
            col2.metric("Probability", f"{prob}%")

            st.markdown("### 📊 Why this score?")
            for line in explanation:
                st.write("✔️ " + line)

            st.markdown("### 🧠 Interpretation")

            if score > 80:
                st.success("High opportunity: strong signals detected")
            elif score > 60:
                st.info("Moderate opportunity")
            else:
                st.warning("Low opportunity")

            st.markdown("### Strategy")
            st.info("Recommend partnership / expansion approach")

            st.markdown("### Email")
            st.code(f"Let's collaborate with {name} for expansion opportunities.")

            new = pd.DataFrame([{
                "name": name,
                "score": score,
                "probability": prob
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- PIPELINE ----------
elif page == "Pipeline":

    st.markdown("### Pipeline")

    if not df.empty:
        for _, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
            <b>{row['name']}</b><br>
            Score: {row['score']}<br>
            Probability: {row['probability']}%
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data")

# ---------- INSIGHTS ----------
elif page == "Insights":

    st.markdown("### Insights")

    if not df.empty:
        st.bar_chart(df.set_index("name")["score"])
    else:
        st.warning("No data yet")
