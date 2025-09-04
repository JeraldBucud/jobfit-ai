import streamlit as st

st.title("JobFit AI - Resume Analyzer")
st.write("Upload your CV and paste a job description to get started.")

# Placeholder inputs
resume = st.text_area("Paste Resume Text")
job_desc = st.text_area("Paste Job Description")

if st.button("Analyze Fit"):
    st.success("⚡ Analysis coming soon! (placeholder)")
