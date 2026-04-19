import streamlit as st

def load_style():
    st.markdown("""
    <style>
    body {background:#0f172a;}
    .card {
        background:#111827;
        padding:20px;
        border-radius:12px;
        margin-bottom:15px;
    }
    </style>
    """, unsafe_allow_html=True)
