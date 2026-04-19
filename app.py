import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

st.set_page_config(page_title="Alaa BD", layout="wide")

st.title("🚀 Alaa BD Intelligence")

# ---------- SESSION ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "name","score","priority","stage"
    ])

df = st.session_state.data

# ---------- SCRAPER ----------
def scrape(url):
    try:
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        texts = []
        for tag in soup.find_all(["h1","h2","h3","p"]):
            t = tag.get_text().strip()
            if len(t) > 40:
                texts.append(t)

        return " ".join(texts).lower()
    except:
        return ""

# ---------- ANALYSIS ----------
def analyze(text):

    score = 0
    reasons = []

    if "enterprise" in text or "b2b" in text:
        score += 20
        reasons.append("B2B business")

    if "platform" in text or "software" in text:
        score += 15
        reasons.append("Tech platform")

    if "client" in text or "customers" in text:
        score += 10
        reasons.append("Has active customers")

    if "expand" in text or "growth" in text:
        score += 20
        reasons.append("Growth signals")

    if "hiring" in text or "careers" in text:
        score += 10
        reasons.append("Hiring activity")

    if "partner" in text:
        score += 15
        reasons.append("Partnership potential")

    score = min(score,100)

    if score > 70:
        priority = "HIGH"
    elif score > 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return score, priority, reasons

# ---------- NAV ----------
page = st.sidebar.selectbox("Menu", ["Dashboard","Analyze","CRM"])

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.subheader("📊 Overview")

    c1,c2,c3 = st.columns(3)

    c1.metric("Companies", len(df))
    c2.metric("High Priority", len(df[df["priority"]=="HIGH"]))
    c3.metric("Avg Score", int(df["score"].mean()) if not df.empty else 0)

    st.dataframe(df)

# ---------- ANALYZE ----------
elif page == "Analyze":

    name = st.text_input("Company Name")
    url = st.text_input("Website URL")

    if st.button("Analyze Company"):

        text = scrape(url)

        if text == "":
            st.error("Could not fetch data from website")
        else:
            score, priority, reasons = analyze(text)

            st.metric("Score", score)
            st.metric("Priority", priority)

            st.write("### Why this result")
            for r in reasons:
                st.write("-", r)

            # Save
            new = pd.DataFrame([{
                "name": name,
                "score": score,
                "priority": priority,
                "stage": "New"
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- CRM ----------
elif page == "CRM":

    st.subheader("📈 Pipeline")

    if not df.empty:
        for i,row in df.iterrows():

            col1,col2 = st.columns([3,1])

            with col1:
                st.write(f"**{row['name']}** | Score: {row['score']}")

            with col2:
                stage = st.selectbox(
                    "Stage",
                    ["New","Contacted","Negotiation","Closed"],
                    key=i
                )
                st.session_state.data.at[i,"stage"] = stage
