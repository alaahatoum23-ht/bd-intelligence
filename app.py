import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Alaa BD PRO MAX", layout="wide")

st.title("🚀 Alaa BD PRO MAX")

# ---------- SESSION ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "name","score","priority","stage","strategy",
        "fit","growth","readiness","urgency","access"
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

# ---------- ANALYSIS ----------
def analyze_company(text):

    signals = {
        "growth": len(re.findall(r"(expand|growth|scale|launch)", text)),
        "funding": len(re.findall(r"(funding|raised|investment)", text)),
        "hiring": len(re.findall(r"(hiring|careers)", text)),
        "partnership": len(re.findall(r"(partner|collaboration)", text)),
        "enterprise": len(re.findall(r"(enterprise|b2b|clients)", text)),
        "product": len(re.findall(r"(platform|software|solution)", text)),
        "market": len(re.findall(r"(mena|gcc|global)", text)),
        "urgency": len(re.findall(r"(accelerate|rapid)", text)),
    }

    fit = signals["enterprise"]*4 + signals["product"]*3
    growth = signals["growth"]*5 + signals["hiring"]*2
    readiness = signals["funding"]*6 + signals["enterprise"]*3
    urgency = signals["urgency"]*5 + signals["growth"]*2
    access = signals["partnership"]*5 + signals["hiring"]*2

    score = int(min(
        fit*0.2 + growth*0.25 + readiness*0.25 + urgency*0.15 + access*0.15,
        100
    ))

    if score > 75:
        priority = "HIGH"
    elif score > 55:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return score, priority, {
        "fit": fit,
        "growth": growth,
        "readiness": readiness,
        "urgency": urgency,
        "access": access
    }

# ---------- RADAR CHART ----------
def radar_chart(data, title):
    labels = list(data.keys())
    values = list(data.values())

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    values += values[:1]
    angles = np.append(angles, angles[0])

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title(title)

    return fig

# ---------- NAV ----------
page = st.sidebar.selectbox("Menu", ["Dashboard","Analyze","Compare","CRM"])

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
            score, priority, dims = analyze_company(full_text)

            st.metric("Score", score)
            st.metric("Priority", priority)

            st.markdown("### 🧠 Radar Analysis")
            fig = radar_chart(dims, "BD Profile")
            st.pyplot(fig)

            st.markdown("### 📊 Dimensions Breakdown")
            fig2, ax = plt.subplots()
            ax.bar(dims.keys(), dims.values())
            st.pyplot(fig2)

            # Save
            new = pd.DataFrame([{
                "name": name,
                "score": score,
                "priority": priority,
                "stage": "New",
                "strategy": "TBD",
                **dims
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# ---------- COMPARE ----------
elif page == "Compare":

    st.subheader("⚖️ Compare Companies")

    if len(df) >= 2:

        names = df["name"].tolist()
        selected = st.multiselect("Select companies", names)

        if len(selected) >= 2:

            comp = df[df["name"].isin(selected)]

            st.dataframe(comp)

            st.markdown("### 📊 Score Comparison")
            st.bar_chart(comp.set_index("name")["score"])

            st.markdown("### 🧠 Radar Comparison")

            fig, ax = plt.subplots(subplot_kw=dict(polar=True))

            for _, row in comp.iterrows():
                values = [row["fit"], row["growth"], row["readiness"], row["urgency"], row["access"]]
                values += values[:1]

                angles = np.linspace(0, 2*np.pi, 5, endpoint=False)
                angles = np.append(angles, angles[0])

                ax.plot(angles, values, label=row["name"])

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(["fit","growth","readiness","urgency","access"])
            ax.legend()

            st.pyplot(fig)

    else:
        st.info("Add at least 2 companies")

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
