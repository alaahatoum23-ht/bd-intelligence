import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import datetime

st.set_page_config(page_title="Alaa BD AI", layout="wide")

st.title("🚀 Alaa BD AI (Level 10 System)")

# ---------- SESSION ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "name","score","priority","stage",
        "deal","contact","notes","next_action","follow_up"
    ])

df = st.session_state.data

# ---------- DATA ----------
def scrape(url):
    try:
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text,"html.parser")
        return " ".join([t.get_text() for t in soup.find_all(["p","h1","h2"])])[:8000].lower()
    except:
        return ""

def wikipedia(company):
    try:
        url = f"https://en.wikipedia.org/wiki/{company.replace(' ','_')}"
        return scrape(url)
    except:
        return ""

def google(company):
    try:
        url = f"https://www.google.com/search?q={company}+company+news"
        return scrape(url)
    except:
        return ""

# ---------- INTELLIGENCE ----------
def analyze(text):

    insights = []

    score = 0

    # Contextual detection
    if "expanding to" in text:
        score += 15
        insights.append("Geographic expansion detected")

    if "raised" in text or "funding" in text:
        score += 20
        insights.append("Funding activity → ready to invest")

    if "we are hiring" in text:
        score += 10
        insights.append("Hiring → scaling operations")

    if "partner" in text:
        score += 15
        insights.append("Open to partnerships")

    if "enterprise" in text or "b2b" in text:
        score += 10
        insights.append("B2B business model")

    score = min(score,100)

    if score > 70:
        priority = "HIGH"
    elif score > 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Decision Output
    why = insights if insights else ["No strong signals"]

    deal = "Exploratory"
    if "funding" in text:
        deal = "Partnership / Vendor Deal"

    contact = "Business Development Manager"
    if "enterprise" in text:
        contact = "Head of Partnerships"

    deal_size = "Small"
    if score > 70:
        deal_size = "Large"

    competitors = []
    if "fintech" in text:
        competitors = ["Stripe-like","Payment platforms"]

    return score, priority, why, deal, contact, deal_size, competitors

# ---------- LEADS ----------
def generate_leads(industry):
    return [
        f"{industry} Company 1",
        f"{industry} Company 2",
        f"{industry} Startup X"
    ]

# ---------- NAV ----------
page = st.sidebar.selectbox("Menu", [
    "Dashboard","Analyze","Leads","CRM"
])

# ---------- DASHBOARD ----------
if page == "Dashboard":

    st.metric("Companies", len(df))
    st.metric("High Priority", len(df[df["priority"]=="HIGH"]))

    st.dataframe(df)

# ---------- ANALYZE ----------
elif page == "Analyze":

    name = st.text_input("Company Name")
    url = st.text_input("Website")

    if st.button("Analyze"):

        text = scrape(url) + wikipedia(name) + google(name)

        score, priority, why, deal, contact, deal_size, competitors = analyze(text)

        st.metric("Score", score)
        st.metric("Priority", priority)

        st.write("### Why this company")
        for w in why:
            st.write("-", w)

        st.write("### Opportunity")
        st.write(deal)

        st.write("### Deal Size")
        st.write(deal_size)

        st.write("### Who to Contact")
        st.write(contact)

        st.write("### Competitors")
        st.write(competitors)

        # Save
        new = pd.DataFrame([{
            "name": name,
            "score": score,
            "priority": priority,
            "stage": "New",
            "deal": deal,
            "contact": contact,
            "notes": "",
            "next_action": "",
            "follow_up": ""
        }])

        st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- LEADS ----------
elif page == "Leads":

    industry = st.text_input("Industry")

    if st.button("Generate Leads"):
        leads = generate_leads(industry)
        st.write(leads)

# ---------- CRM ----------
elif page == "CRM":

    for i,row in df.iterrows():

        st.write(f"### {row['name']}")

        st.text_area("Notes", key=f"notes{i}")
        st.text_input("Next Action", key=f"action{i}")
        st.date_input("Follow Up", key=f"date{i}")

        stage = st.selectbox("Stage",
            ["New","Contacted","Negotiation","Closed"], key=f"stage{i}")

        st.session_state.data.at[i,"stage"] = stage
