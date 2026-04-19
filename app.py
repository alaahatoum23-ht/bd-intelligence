import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Alaa BD Pro", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {background:#0f172a;color:white;}
.header {font-size:32px;font-weight:700;}
.card {background:#111827;padding:15px;border-radius:12px;margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🚀 Alaa BD Pro (Consulting Mode)</div>', unsafe_allow_html=True)

# ---------- NAV ----------
page = st.sidebar.selectbox("Navigation", [
    "Dashboard","Analyze","CRM Pipeline"
])

# ---------- DATA ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "name","score","prob","stage","priority","strategy"
    ])

df = st.session_state.data

# ---------- SCRAPER ----------
def scrape(url):
    try:
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        return " ".join([t.get_text() for t in soup.find_all(["p","h1","h2"])])[:9000].lower()
    except:
        return ""

# ---------- ANALYSIS ----------
def analyze(text):

    growth = len(re.findall(r"(growth|expand|scale)", text))
    funding = len(re.findall(r"(funding|investment)", text))
    market = len(re.findall(r"(mena|gcc|global)", text))
    tech = len(re.findall(r"(platform|software|ai)", text))

    score = min(growth*5 + funding*6 + market*4 + tech*3, 100)
    prob = int(score * 0.85)

    # Consulting logic
    attractiveness = "Low"
    if growth > 2 or funding > 1:
        attractiveness = "High"

    fit = "Medium"
    if tech > 2:
        fit = "High"

    timing = "Early"
    if funding > 1:
        timing = "Optimal"

    priority = "Low"
    if score > 75:
        priority = "High"

    strategy = "General outreach"

    if priority == "High":
        strategy = "Direct partnership proposal"
    elif attractiveness == "High":
        strategy = "Strategic alignment discussion"

    return score, prob, attractiveness, fit, timing, priority, strategy

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.subheader("📊 Overview")

    c1,c2,c3 = st.columns(3)

    c1.metric("Companies", len(df))
    c2.metric("High Priority", len(df[df["priority"]=="High"]))
    c3.metric("Avg Score", int(df["score"].mean()) if not df.empty else 0)

    if not df.empty:
        st.dataframe(df)

# ---------- ANALYZE ----------
elif page == "Analyze":

    name = st.text_input("Company")
    url = st.text_input("Website")

    if st.button("Run Analysis"):

        text = scrape(url)

        if text == "":
            st.error("Failed to fetch")
        else:
            score, prob, attr, fit, timing, priority, strategy = analyze(text)

            st.markdown("## 📊 Consulting Analysis")

            st.metric("Score", score)
            st.metric("Probability", f"{prob}%")

            st.markdown("### 🧠 Strategic View")
            st.write(f"Market Attractiveness: {attr}")
            st.write(f"Strategic Fit: {fit}")
            st.write(f"Timing: {timing}")

            st.markdown("### 🎯 Priority")
            if priority == "High":
                st.success("High Priority Deal")
            else:
                st.info("Normal Priority")

            st.markdown("### 🚀 Strategy")
            st.info(strategy)

            # save
            new = pd.DataFrame([{
                "name": name,
                "score": score,
                "prob": prob,
                "stage": "New",
                "priority": priority,
                "strategy": strategy
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- CRM ----------
elif page == "CRM Pipeline":

    st.subheader("📈 Deals Pipeline")

    if not df.empty:

        for i, row in df.iterrows():

            col1, col2 = st.columns([3,1])

            with col1:
                st.markdown(f"""
                <div class="card">
                <b>{row['name']}</b><br>
                Score: {row['score']} | Priority: {row['priority']}<br>
                Strategy: {row['strategy']}
                </div>
                """, unsafe_allow_html=True)

            with col2:
                stage = st.selectbox(
                    "Stage",
                    ["New","Contacted","Negotiation","Closed"],
                    index=["New","Contacted","Negotiation","Closed"].index(row["stage"]),
                    key=i
                )

                st.session_state.data.at[i,"stage"] = stage

    else:
        st.info("No deals yet")
