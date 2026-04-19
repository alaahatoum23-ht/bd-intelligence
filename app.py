import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openai import OpenAI

# ---------- CONFIG ----------
st.set_page_config(page_title="BD Intelligence OS", layout="wide")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- STYLE ----------
st.markdown("""
<style>
body {background-color:#0e1117;color:white;}
.big-title {font-size:38px;font-weight:700;}
.card {padding:20px;border-radius:15px;background:#1c1f26;}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<p class="big-title">🚀 BD Intelligence OS</p>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
page = st.sidebar.selectbox("Navigation", [
    "Dashboard",
    "AI Analysis",
    "Companies",
    "Add Company",
    "Executive View"
])

# ---------- STORAGE ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["name","industry","score"])

df = st.session_state.data

# ---------- SCRAPER ----------
def get_website_text(url):
    try:
        res = requests.get(url, timeout=6)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text()[:4000]
    except:
        return "No data"

# ---------- AI ----------
def analyze(company, content):
    prompt = f"""
    You are a senior business development strategist.

    Analyze:
    Company: {company}
    Content: {content}

    Return:
    - Summary
    - Market Position
    - Opportunities
    - Risks
    - Probability of partnership (0-100%)
    - Recommended BD approach
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ---------- SCORING ----------
def calculate_score(text):
    score = 50
    if "growth" in text.lower():
        score += 15
    if "expansion" in text.lower():
        score += 15
    if "partnership" in text.lower():
        score += 20
    return min(score,100)

# ---------- DASHBOARD ----------
if page == "Dashboard":
    st.subheader("📊 Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Companies", len(df))
    col2.metric("High Opportunities", len(df[df["score"] > 80]) if not df.empty else 0)
    col3.metric("Avg Score", int(df["score"].mean()) if not df.empty else 0)

    if not df.empty:
        st.dataframe(df.sort_values(by="score", ascending=False))

# ---------- AI ----------
elif page == "AI Analysis":

    st.subheader("🤖 AI Company Intelligence")

    name = st.text_input("Company Name")
    website = st.text_input("Website")

    if st.button("Analyze"):

        if not name or not website:
            st.warning("Fill all fields")
        else:
            st.info("Collecting data...")

            content = get_website_text(website)

            st.info("Running AI...")

            result = analyze(name, content)

            score = calculate_score(result)

            st.success("Analysis Ready")

            st.write(result)

            st.metric("BD Opportunity Score", score)

# ---------- COMPANIES ----------
elif page == "Companies":
    st.subheader("🏢 Companies")

    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No companies yet")

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
        st.success("Added")

# ---------- EXECUTIVE ----------
elif page == "Executive View":

    st.subheader("🚀 Executive Insights")

    if not df.empty:
        top = df.sort_values(by="score", ascending=False).head(5)

        for _, row in top.iterrows():
            st.markdown(f"### {row['name']}")
            st.write(f"Score: {row['score']}")
            st.info("High-value BD opportunity")
    else:
        st.warning("No data yet")
