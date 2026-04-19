import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Alaa BD PRO MAX", layout="wide")

# ---------- UI STYLE ----------
st.markdown("""
<style>
body {background-color:#0f172a;}
.block-container {padding-top:2rem;}

.title {font-size:28px;font-weight:700;color:white;}
.card {
    background:#111827;
    padding:20px;
    border-radius:14px;
    margin-bottom:20px;
    box-shadow:0px 4px 20px rgba(0,0,0,0.4);
}
.metric-card {
    background:#1f2937;
    padding:15px;
    border-radius:12px;
    text-align:center;
    color:white;
}
.stButton>button {
    background: linear-gradient(90deg,#6366f1,#8b5cf6);
    color:white;
    border-radius:10px;
    height:45px;
    width:100%;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🚀 Alaa BD PRO MAX</div>', unsafe_allow_html=True)

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
        return " ".join([t.get_text() for t in soup.find_all(["h1","h2","p"])])[:10000].lower()
    except:
        return ""

def google_search(company):
    try:
        url = f"https://www.google.com/search?q={company}+company+news"
        res = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")

        texts = []
        for div in soup.find_all("div"):
            t = div.get_text()
            if len(t) > 60:
                texts.append(t)

        return " ".join(texts)[:4000].lower()
    except:
        return ""

# ---------- ENGINE ----------
def analyze(text):

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

    priority = "HIGH" if score > 75 else "MEDIUM" if score > 55 else "LOW"

    return score, priority, {
        "fit": fit,
        "growth": growth,
        "readiness": readiness,
        "urgency": urgency,
        "access": access
    }

# ---------- RADAR ----------
def radar_chart(data):
    labels = list(data.keys())
    values = list(data.values())
    values += values[:1]

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    angles = np.append(angles, angles[0])

    fig, ax = plt.subplots(subplot_kw=dict(polar=True))
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    return fig

# ---------- NAV ----------
page = st.sidebar.selectbox("Menu", ["Dashboard","Analyze","Compare","CRM"])

# ---------- DASHBOARD ----------
if page == "Dashboard":

    col1,col2,col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="metric-card">Companies<br><h2>{len(df)}</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="metric-card">High Priority<br><h2>{len(df[df["priority"]=="HIGH"])}</h2></div>', unsafe_allow_html=True)

    with col3:
        avg = int(df["score"].mean()) if not df.empty else 0
        st.markdown(f'<div class="metric-card">Avg Score<br><h2>{avg}</h2></div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- ANALYZE ----------
elif page == "Analyze":

    colA,colB = st.columns(2)
    with colA:
        name = st.text_input("Company Name")
    with colB:
        url = st.text_input("Website")

    if st.button("🚀 Run Analysis"):

        text = scrape_site(url) + " " + google_search(name)

        score, priority, dims = analyze(text)

        # METRICS
        c1,c2 = st.columns(2)
        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.metric("Score", score)
            st.metric("Priority", priority)
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            if score > 80:
                st.success("🔥 Strong Opportunity")
            elif score > 60:
                st.info("⚡ Medium Opportunity")
            else:
                st.warning("⚠️ Weak Opportunity")
            st.markdown('</div>', unsafe_allow_html=True)

        # RADAR
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🧠 Radar Analysis")
        st.pyplot(radar_chart(dims))
        st.markdown('</div>', unsafe_allow_html=True)

        # BAR
        st.markdown('<div class="card">', unsafe_allow_html=True)
        fig, ax = plt.subplots()
        ax.bar(dims.keys(), dims.values())
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

        # SAVE
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

    if len(df) >= 2:

        selected = st.multiselect("Select companies", df["name"])

        if len(selected) >= 2:

            comp = df[df["name"].isin(selected)]

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.dataframe(comp, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.bar_chart(comp.set_index("name")["score"])
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.info("Add more companies first")

# ---------- CRM ----------
elif page == "CRM":

    if not df.empty:
        for i, row in df.iterrows():
            col1,col2 = st.columns([3,1])

            with col1:
                st.write(f"**{row['name']}** | {row['score']} | {row['priority']}")

            with col2:
                stage = st.selectbox(
                    "Stage",
                    ["New","Contacted","Negotiation","Closed"],
                    key=i
                )
                st.session_state.data.at[i,"stage"] = stage
