
# app/main.py
import streamlit as st
from core.analyzer import analyze_pdf

st.set_page_config(page_title="PDF Ligature Stego-Sniffer", layout="wide")
st.title("PDF Ligature Stego-Sniffer — Demo")

uploaded = st.file_uploader("Upload PDF (try your sample.pdf)", type=["pdf"])
if uploaded:
    result = analyze_pdf(uploaded)
    st.subheader("Summary")
    st.json(result["summary"])
    st.write("First 20 character records (truncated):")
    st.dataframe(result["characters"][:20])
