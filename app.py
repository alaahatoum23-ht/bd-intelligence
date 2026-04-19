import streamlit as st
import pandas as pd
from scraper import get_clean_text
from engine import analyze
from ui import load_style
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
load_style()

st.title("🚀 Alaa BD Intelligence")

# SESSION
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "name","score","priority","stage","deal","contact"
    ])

df = st.session_state.data

menu = st.sidebar.selectbox("Menu", ["Dashboard","Analyze","Compare","CRM"])

# DASHBOARD
if menu == "Dashboard":

    c1,c2,c3 = st.columns(3)
    c1.metric("Companies", len(df))
    c2.metric("High Priority", len(df[df["priority"]=="HIGH"]))
    c3.metric("Avg Score", int(df["score"].mean()) if not df.empty else 0)

    st.dataframe(df)

# ANALYZE
elif menu == "Analyze":

    name = st.text_input("Company")
    url = st.text_input("Website")

    if st.button("Analyze"):

        text = get_clean_text(url)

        if text == "":
            st.error("Failed to fetch data")
        else:
            result = analyze(text)

            st.metric("Score", result["score"])
            st.metric("Priority", result["priority"])

            st.write("### Insights")
            for i in result["insights"]:
                st.write("-", i)

            st.write("### Deal Strategy")
            st.write(result["deal"])

            st.write("### Contact")
            st.write(result["contact"])

            # Radar
            vals = [result["score"], 50, 60, 40, 70]
            angles = np.linspace(0, 2*np.pi, len(vals), endpoint=False)
            vals += vals[:1]
            angles = np.append(angles, angles[0])

            fig, ax = plt.subplots(subplot_kw=dict(polar=True))
            ax.plot(angles, vals)
            ax.fill(angles, vals, alpha=0.2)

            st.pyplot(fig)

            # Save
            new = pd.DataFrame([{
                "name": name,
                "score": result["score"],
                "priority": result["priority"],
                "stage": "New",
                "deal": result["deal"],
                "contact": result["contact"]
            }])

            st.session_state.data = pd.concat([df, new], ignore_index=True)

# COMPARE
elif menu == "Compare":

    if len(df) >= 2:
        selected = st.multiselect("Select", df["name"])

        if len(selected) >= 2:
            comp = df[df["name"].isin(selected)]
            st.dataframe(comp)
            st.bar_chart(comp.set_index("name")["score"])

# CRM
elif menu == "CRM":

    for i,row in df.iterrows():
        col1,col2 = st.columns([3,1])

        with col1:
            st.write(f"{row['name']} | {row['score']}")

        with col2:
            stage = st.selectbox("Stage",
                ["New","Contacted","Negotiation","Closed"],
                key=i)

            st.session_state.data.at[i,"stage"] = stage
