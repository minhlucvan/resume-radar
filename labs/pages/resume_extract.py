# chat_pdf.py
import streamlit as st
from dotenv import load_dotenv
import pickle
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains import LLMChain
import os
from langchain import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import json
import yaml
import requests
from common import resume_extract

import getpass
import os

load_dotenv()

def main():
    st.header("Chat with PDF")
    
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
