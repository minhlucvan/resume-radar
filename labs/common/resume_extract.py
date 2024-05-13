# chat_pdf.py
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.llms import OpenAI
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
import json
import requests

import getpass
import os
import re

from common import env
from common import healing
from common import llm_model
from common import prompts

import hashlib

def hash_pdf_url(url):   
    return hashlib.md5(url.encode()).hexdigest()


load_dotenv()

# get llm model

def get_llm_openai():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.9)
    return llm

# get llm model gemini


def get_llm_gemini():
    if "GOOGLE_API_KEY" not in os.environ:
        os.environ["GOOGLE_API_KEY"] = getpass.getpass(
            "Provide your Google API Key")

    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    return llm

def extract_data(text):
    system_instruction, prompt = prompts.resume_to_markdown(text)
    return llm_model.run(system_instruction, prompt)


def extract_json(text):
    system_instruction, prompt = prompts.markdown_to_json(text)
    return llm_model.run(system_instruction, prompt, is_json=True)

def extract_pdf_text(pdf):
    pdf_reader = PdfReader(pdf)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

def extract_education_data(text):
    system_instruction, prompt = prompts.extract_resume_education(text)
    return llm_model.run(system_instruction, prompt)

# extract project data
def extract_project_data(text):
    system_instruction, prompt = prompts.extract_resume_projects(text)
    return llm_model.run(system_instruction, prompt)

# load pdf from url
# return the pdf content as File the same as the uploaded file
def load_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    pdf = response.content
    
    pdf_hash = hash_pdf_url(pdf_url)
    
    pdf_filename = f"{pdf_hash}.pdf"
    
    data_path = os.path.join("data")
    
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    dir_path = os.path.join("data", 'dumb')
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    pdf_path = os.path.join("data", 'dumb', pdf_filename)
    
    # create a file from the pdf content
    with open(pdf_path, 'wb') as f:
        f.write(pdf)
    
    file = open(pdf_path, 'rb')
    
    return file

def has_cached_data(pdf_url):
    pdf_hash = hash_pdf_url(pdf_url)
    pdf_filename = f"{pdf_hash}.json"
    pdf_path = os.path.join("data", 'dumb', pdf_filename)
    
    return os.path.exists(pdf_path)

def load_data(data):
    data_dict = json.loads(data) if isinstance(data, str) else data
    
    # bytes to string
    if isinstance(data_dict, bytes):
        data_dict = data_dict.decode('utf-8')
    
    if isinstance(data_dict, str):
        data_dict = json.loads(data_dict)
    
    return data_dict

def get_cached_data(pdf_url):
    pdf_hash = hash_pdf_url(pdf_url)
    pdf_filename = f"{pdf_hash}.json"
    pdf_path = os.path.join("data", 'dumb', pdf_filename)
    
    with open(pdf_path, 'r') as f:
        data = json.load(f)
    
    return data

def extract_resume(url_or_file, silent=True):

    pdf_url = None
    # upload a pdf file
    pdf_file = None
    
    if isinstance(url_or_file, str):
        pdf_url = url_or_file
    else:
        pdf_file = url_or_file
    
    pdf = None
    
    if pdf_url:
        pdf = load_pdf_from_url(pdf_url)
    
    if pdf_file:
        pdf = pdf_file

    if pdf is None:
        st.info("Please upload a PDF file")
        return

    with st.spinner("Extracting text from PDF..."):
        text = extract_pdf_text(pdf)
        if not silent:
            st.write('Extracted text:')
            st.text_area("Extracted text", text)

    with st.spinner("Extracting data from text..."):
        data = extract_data(text)
        if not silent:
            st.write('Extracted data:')
            st.text_area(data)

    # extract yml from structured data
    with st.spinner("Extracting yml from structured data..."):
        try:
            json_data = extract_json(data)
            
            if not silent:
                st.write('Extracted Json:')
                st.text_area("Extracted Json", json_data)
        except Exception as e:
            st.write('Error extracting json data:', e)
            st.stop()

    # extract project data
    with st.spinner("Extracting project data..."):
        try:
            parsed_project_data = extract_project_data(text)
            if not silent:
                st.write('Extracted project data:')
                st.write(parsed_project_data)
        except Exception as e:
            st.write('Error extracting project data:', e)
            st.stop()
        
    with st.spinner("Extracting education data..."):
        parsed_education_data = extract_education_data(text)
        if not silent:
            st.write('Extracted education data:')

    extracted_data = {
        "text": text,
        "data": data,
        "properties": json_data,
        "projects": parsed_project_data,
        "educations": parsed_education_data
    }

    extracted_data_json = json.dumps(extracted_data, indent=4)
    
    if not silent:
        st.text_area("Extracted data", extracted_data_json)
    
    return extracted_data_json
