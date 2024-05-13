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

import hashlib

# excute prompt 
# extract project data
def run(system_instruction, text, is_json=False):

    genai.configure(api_key=env.get_gemini_key())

    # Set up the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  system_instruction=system_instruction,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[])

    convo.send_message(text, request_options={"timeout": 600})
    response = convo.last.text
    
    if is_json:
        return healing.load_json_attempt(response)

    return response
