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
        return text.lower()[:10000]
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

# ---------- CONSULTING ENGINE ----------
def analyze_company(text):

    text = text.lower()

    signals = {
        "growth": len(re.findall(r"(expand|expanding|growth|scaling|launch)", text)),
        "funding": len(re.findall(r"(funding|raised|series|investment)", text)),
        "hiring": len(re.findall(r"(hiring|join our team|careers)", text)),
        "partnership": len(re.findall(r"(partner|collaboration|alliance)", text)),
        "enterprise": len(re.findall(r"(enterprise|b2b|clients|solutions)", text)),
        "product": len(re.findall(r"(platform|technology|software|solution)", text)),
        "market": len(re.findall(r"(mena|gcc|global|expansion)", text)),
        "urgency": len(re.findall(r"(accelerate|rapid|immediately)", text)),
    }

    fit = signals["enterprise"]*4 + signals["product"]*3
    growth = signals["growth"]*5 + signals["hiring"]*2
    readiness = signals["funding"]*6 + signals["enterprise"]*3
    urgency = signals["urgency"]*5 + signals["growth"]*2
    access = signals["partnership"]*5 + signals["hiring"]*2

    score = int(min(
        fit*0.2 +
        growth*0.25 +
        readiness*0.25 +
        urgency*0.15 +
        access*0.15,
        100
    ))

    if score > 75:
        priority = "HIGH"
    elif score > 55:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    if signals["funding"] > 0:
        why_now = "Funding detected → company is scaling"
    elif signals["growth"] > 2:
        why_now = "Expansion signals → strong timing"
    elif signals["hiring"] > 1:
        why_now = "Hiring → internal growth phase"
    else:
        why_now = "No strong urgency"

    if priority == "HIGH":
        strategy = "Direct high-value partnership pitch"
    elif priority == "MEDIUM":
        strategy = "Strategic intro + discovery"
    else:
        strategy = "Light outreach"

    risks = []
    if signals["growth"] == 0:
        risks.append("No growth signals")
    if signals["funding"] == 0:
        risks.append("No funding signals")
    if signals["enterprise"] == 0:
        risks.append("Weak B2B signals")
    if not risks:
        risks.append("No major risks")

    return {
        "score": score,
        "priority": priority,
        "why_now": why_now,
        "strategy": strategy,
        "risks": risks,
        "signals": signals,
        "dimensions": {
            "fit": fit,
            "growth": growth,
            "readiness": readiness,
            "urgency": urgency,
            "access": access
        }
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

    if st.button("Run Analysis"):

        site = scrape_site(url)
        google = google_search(name)

        full_text = site + " " + google

        if full_text.strip() == "":
            st.error("No data found")
        else:
            result = analyze_company(full_text)

            st.markdown("## 🧠 BD Intelligence Report")

            st.metric("Score", result["score"])
            st.metric("Priority", result["priority"])

            st.markdown("### 📊 Why Now")
            st.success(result["why_now"])

            st.markdown("### 🚀 Strategy")
            st.info(result["strategy"])

            st.markdown("### ⚠️ Risks")
            for r in result["risks"]:
                st.warning(r)

            st.markdown("### 📈 Dimensions")
            st.json(result["dimensions"])

            st.markdown("### 🔍 Signals")
            st.json(result["signals"])

            # Save
            new = pd.DataFrame([{
                "name": name,
                "score": result["score"],
                "priority": result["priority"],
                "stage": "New",
                "strategy": result["strategy"]
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
                st.caption(f"Strategy: {row['strategy']}")

            with col2:
                stage = st.selectbox(
                    "Stage",
                    ["New","Contacted","Negotiation","Closed"],
                    key=i
                )
                st.session_state.data.at[i,"stage"] = stage
    else:
        st.info("No deals yet")
