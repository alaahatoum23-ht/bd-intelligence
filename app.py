import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Alaa BD PRO MAX", layout="wide")

st.title("🚀 Alaa BD PRO MAX")

# ---------- SESSION ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "name","score","priority","stage","strategy"
    ])

df = st.session_state.data

# ---------- SCRAPERS ----------
def scrape_site(url):
    try:
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")

        text = " ".join([t.get_text() for t in soup.find_all(["h1","h2","p"])])
        return text.lower()[:8000]
    except:
        return ""

def google_search(company):
    try:
        url = f"https://www.google.com/search?q={company}+company+news"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        snippets = []
        for div in soup.find_all("div"):
            txt = div.get_text()
            if len(txt) > 60:
                snippets.append(txt)

        return " ".join(snippets)[:4000].lower()
    except:
        return ""

# ---------- ANALYSIS ----------
def analyze(text):

    signals = {
        "growth": len(re.findall(r"(expand|growth|scale|launch)", text)),
        "funding": len(re.findall(r"(funding|raised|investment)", text)),
        "hiring": len(re.findall(r"(hiring|join our team)", text)),
        "partnership": len(re.findall(r"(partner|collaboration)", text)),
        "market": len(re.findall(r"(mena|gcc|global)", text))
    }

    score = min(
        signals["growth"]*5 +
        signals["funding"]*7 +
        signals["hiring"]*3 +
        signals["partnership"]*5 +
        signals["market"]*2,
        100
    )

    # BD LOGIC
    if score > 80:
        priority = "HIGH"
    elif score > 60:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return score, priority, signals

# ---------- REPORT ----------
def generate_report(name, signals, score):

    why_now = "No strong signals."

    if signals["funding"] > 0:
        why_now = "Company recently shows funding signals → ready to scale."

    elif signals["growth"] > 2:
        why_now = "Active expansion → strong BD timing."

    deal_type = "Exploratory"

    if signals["partnership"] > 1:
        deal_type = "Partnership / Integration"

    strategy = "Start with intro meeting"

    if score > 80:
        strategy = "Direct BD pitch with clear value proposition"

    risks = "Limited visibility"

    if signals["market"] == 0:
        risks = "Market focus unclear"

    return {
        "why_now": why_now,
        "deal_type": deal_type,
        "strategy": strategy,
        "risks": risks
    }

# ---------- NAV ----------
page = st.sidebar.selectbox("Menu", ["Dashboard","Analyze","CRM"])

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.subheader("📊 Overview")

    c1,c2,c3 = st.columns(3)

    c1.metric("Companies", len(df))
    c2.metric("High Priority", len(df[df["priority"]=="HIGH"]))
    c3.metric("Avg Score", int(df["score"].mean()) if not df.empty else 0)

    if not df.empty:
        st.dataframe(df)

# ---------- ANALYZE ----------
elif page == "Analyze":

    name = st.text_input("Company Name")
    url = st.text_input("Website")

    if st.button("Run PRO MAX Analysis"):

        site = scrape_site(url)
        google = google_search(name)

        full_text = site + " " + google

        if full_text.strip() == "":
            st.error("No data found")
        else:
            score, priority, signals = analyze(full_text)
            report = generate_report(name, signals, score)

            st.markdown("## 🧠 BD Intelligence Report")

            st.metric("Score", score)
            st.metric("Priority", priority)

            st.markdown("### 🔍 Signals")
            st.json(signals)

            st.markdown("### 📊 Why Now")
            st.success(report["why_now"])

            st.markdown("### 🎯 Deal Type")
            st.info(report["deal_type"])

            st.markdown("### 🚀 Strategy")
            st.success(report["strategy"])

            st.markdown("### ⚠️ Risks")
            st.warning(report["risks"])

            # Save to CRM
            new = pd.DataFrame([{
                "name": name,
                "score": score,
                "priority": priority,
                "stage": "New",
                "strategy": report["strategy"]
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- CRM ----------
elif page == "CRM":

    st.subheader("📈 Pipeline")

    if not df.empty:
        for i, row in df.iterrows():

            col1, col2 = st.columns([3,1])

            with col1:
                st.write(f"**{row['name']}** | Score: {row['score']} | {row['priority']}")

            with col2:
                stage = st.selectbox(
                    "Stage",
                    ["New","Contacted","Negotiation","Closed"],
                    key=i
                )
                st.session_state.data.at[i,"stage"] = stage
    else:
        st.info("No deals yet")
