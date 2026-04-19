import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Alaa BD", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.main {
    background-color: #0f172a;
}
.header {
    font-size: 34px;
    font-weight: 700;
}
.card {
    background: #111827;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.metric {
    font-size: 28px;
    font-weight: bold;
}
.small {
    color: #9ca3af;
}
.section {
    margin-top: 30px;
}
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
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        text = " ".join([t.get_text() for t in soup.find_all(["p","h1","h2","h3"])])
        return text.lower()[:8000]
    except:
        return ""

# ---------- ANALYSIS ----------
def analyze_text(text):
    growth = len(re.findall(r"(growth|expand|scale)", text))
    funding = len(re.findall(r"(funding|investment)", text))
    tech = len(re.findall(r"(ai|platform|software)", text))
    partner = len(re.findall(r"(partner|collaboration)", text))

    score = min(growth*5 + funding*6 + tech*4 + partner*6, 100)
    prob = min(int(score * 0.9), 95)

    return score, prob

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.markdown("### Overview")

    c1, c2, c3 = st.columns(3)

    c1.markdown(f'<div class="card"><div class="metric">{len(df)}</div><div class="small">Companies</div></div>', unsafe_allow_html=True)

    high = len(df[df["score"] > 80]) if not df.empty else 0
    c2.markdown(f'<div class="card"><div class="metric">{high}</div><div class="small">High Value</div></div>', unsafe_allow_html=True)

    avg = int(df["score"].mean()) if not df.empty else 0
    c3.markdown(f'<div class="card"><div class="metric">{avg}</div><div class="small">Avg Score</div></div>', unsafe_allow_html=True)

    st.markdown("### Top Opportunities")

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
            st.error("Failed to fetch data")
        else:
            score, prob = analyze_text(text)

            st.success("Analysis Complete")

            col1, col2 = st.columns(2)
            col1.metric("Score", score)
            col2.metric("Probability", f"{prob}%")

            st.markdown("### Strategy")
            st.info("Expand partnership / market entry opportunity")

            st.markdown("### Email")
            st.code(f"Let's collaborate with {name} for expansion.")

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

# ---------- INSIGHTS ----------
elif page == "Insights":

    st.markdown("### Insights")

    if not df.empty:
        st.bar_chart(df.set_index("name")["score"])
    else:
        st.warning("No data")
