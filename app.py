import streamlit as st
import pandas as pd

st.set_page_config(page_title="BD Intelligence OS", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.big-title {
    font-size:40px !important;
    font-weight:700;
}
.card {
    padding:20px;
    border-radius:15px;
    background-color:#111;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<p class="big-title">🚀 BD Intelligence OS</p>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
page = st.sidebar.selectbox("Navigation", [
    "Dashboard",
    "Companies",
    "Add Company",
    "Executive View"
])

# ---------- DATA ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {"name": "Careem", "industry": "Tech", "score": 85},
        {"name": "Talabat", "industry": "Food", "score": 78},
        {"name": "Kitopi", "industry": "Cloud Kitchen", "score": 90}
    ])

df = st.session_state.data

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.subheader("📊 Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Companies", len(df))
    col2.metric("High Opportunities", len(df[df["score"] > 80]))
    col3.metric("Average Score", int(df["score"].mean()))

    st.subheader("🔥 Top Companies")
    st.dataframe(df.sort_values(by="score", ascending=False))

# ---------- COMPANIES ----------
elif page == "Companies":
    st.subheader("🏢 Company Intelligence")

    search = st.text_input("Search company")

    if search:
        result = df[df["name"].str.contains(search, case=False)]

        if not result.empty:
            company = result.iloc[0]

            st.markdown(f"## {company['name']}")
            st.write(f"Industry: {company['industry']}")
            st.write(f"Score: {company['score']}")

            st.subheader("🤖 AI Insights")
            st.success("Strong candidate for strategic partnership in GCC expansion.")

            st.subheader("✉️ Suggested Email")
            st.code(f"""
Subject: Partnership with {company['name']}

We see strong alignment between our companies for expansion opportunities.
""")

# ---------- ADD ----------
elif page == "Add Company":
    st.subheader("➕ Add Company")

    name = st.text_input("Name")
    industry = st.text_input("Industry")

    if st.button("Add"):
        new = pd.DataFrame([{
            "name": name,
            "industry": industry,
            "score": 70
        }])

        st.session_state.data = pd.concat([df, new], ignore_index=True)
        st.success("Added!")

# ---------- EXECUTIVE ----------
elif page == "Executive View":
    st.subheader("🚀 Executive Mode")

    top = df.sort_values(by="score", ascending=False).head(5)

    for _, row in top.iterrows():
        st.markdown(f"### {row['name']}")
        st.write(f"Score: {row['score']}")
        st.info("High-value partnership opportunity.")
