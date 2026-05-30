import streamlit as st
from google import genai
import os

st.set_page_config(page_title="Faculty Assistant", layout="wide")

st.title("AI-Powered Faculty Assistant")
st.caption("Generate teaching content using Gemini AI")

topic = st.text_input("Enter Topic", placeholder="e.g. Artificial Intelligence in Education")

api_key = st.text_input("Gemini API Key", type="password")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if st.button("Generate") and topic and api_key:
    with st.spinner("Generating content..."):

        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an expert faculty assistant. For the topic: "{topic}"

Generate the following in a clear structured format:

1. LEARNING OBJECTIVES (3 objectives)
2. LECTURE OUTLINE (main sections with brief points)
3. MCQs (5 multiple choice questions with 4 options each and correct answer)
4. TOPIC SUMMARY (2-3 paragraph summary)

Format each section with clear headings.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text

        st.subheader("Generated Teaching Content")

        st.markdown(result)

        st.download_button(
            label="Download Content",
            data=result,
            file_name=f"{topic.replace(' ', '_')}_content.txt",
            mime="text/plain"
        )