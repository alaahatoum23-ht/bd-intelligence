import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

st.set_page_config(layout="wide")

st.title("🚀 BD Intelligence OS - AI Powered")

# ---------- API ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------- INPUT ----------
company_name = st.text_input("Company Name")
website = st.text_input("Company Website")

# ---------- SCRAPER ----------
def get_website_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        return soup.get_text()[:4000]
    except:
        return "No data available"

# ---------- AI ----------
def analyze(company, content):
    prompt = f"""
    You are a senior business development strategist.

    Analyze the company below:

    Company: {company}
    Content: {content}

    Provide:
    - Clear company summary
    - Market position
    - Strategic partnership opportunities
    - Probability of success (0-100%)
    - Recommended BD approach
    - Risk factors
    """

    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ---------- RUN ----------
if st.button("Analyze Company"):

    if not company_name or not website:
        st.warning("Please enter all fields")
    else:
        st.info("Collecting real data...")

        content = get_website_text(website)

        st.info("Running AI analysis...")

        result = analyze(company_name, content)

        st.success("Analysis Ready")
        st.write(result)
