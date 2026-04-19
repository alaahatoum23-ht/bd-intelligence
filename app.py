import streamlit as st

st.set_page_config(page_title="BD Intelligence", layout="wide")

st.title("🚀 BD Intelligence System")

st.subheader("🔍 Search Company")

company = st.text_input("Enter company name")

if company:
    st.success(f"Analysis for {company}")
    st.write("### 🤝 Partnership Idea")
    st.write("Collaborate on market expansion in GCC.")

    st.write("### 📊 Why this works")
    st.write("Company shows growth signals and regional alignment.")

    st.write("### ✉️ Email Draft")
    st.code(f"""
Subject: Partnership Opportunity with {company}

Dear Team,

We see a strong opportunity to collaborate with {company} in expanding into new markets.

Best regards,
Business Development Team
""")
