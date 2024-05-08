# chat_pdf.py
import streamlit as st
from dotenv import load_dotenv
import json
from common import resume_extract


load_dotenv()

def main():
    st.header("Resume Extractor")
    
    pdf_url = st.text_input("Enter the URL of the PDF file")

    # upload a pdf file
    pdf_file = st.file_uploader("Upload your PDF", type='pdf')
    
    pdf = None
    
    if pdf_url:
        pdf = pdf_url
    
    if pdf_file:
        pdf = pdf_file

    if pdf is None:
        st.info("Please upload a PDF file")
        return
    
    data = resume_extract.extract_resume(pdf)
    
    st.text_area("Resume data", json.dumps(data, indent=4))

if __name__ == '__main__':
    main()
