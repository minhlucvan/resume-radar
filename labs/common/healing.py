# chat_pdf.py
import os
import google.generativeai as genai
import json
import os
import re
from common import env
import streamlit as st
import pandas as pd
import io
from common import json_utils

# fix broken json
def fix_broken_json(text):
    
    json_content = json_utils.clean_json_text(text)
    
    try:
        return json.loads(json_content)
    except:
        pass
    
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

    system_instruction = """
    Task: Fix broken JSON, I will provide the broken JSON and you will fix it. make sure the JSON is valid and can be parsed by a JSON parser.
    
    Instructions:
    - Fix the broken JSON
    - Make sure the JSON is valid and can be parsed by a JSON parser.
    - Make sure the JSON is formatted correctly.
    - Make sure the JSON is complete and all the necessary fields are present.
    - Make sure the JSON is free of any syntax errors.
    - Make sure the JSON is free of any comments.
    - Make sure the JSON is has correct quotes and commas for the keys and values.
    
    Input: Broken JSON string
    
    Output: Fixed JSON string, make sure the JSON is valid and can be parsed by a JSON parser. NEVER return anything other than JSON.
"""

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  system_instruction=system_instruction,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[])

    convo.send_message(text)
    response = convo.last.text
    
    json_content = json_utils.clean_json_text(response)
    
    return json.loads(json_content)

def load_json_attempt(text):
    try:
        return json.loads(text)
    except:
        st.warning("Failed to load JSON, attempting to fix it")
        try:
            return fix_broken_json(text)
        except:
            st.error("Failed to fix JSON")
            st.text_area("Broken JSON", text)
            raise Exception("Failed to fix JSON")

def load_csv_attempt(text):
    try:
        csv_content = text
        
        # when has ```csv ``` pattern, get the content after ```csv to the ```
        if "```csv" in text:
            csv_content = text.split("```csv")[1]
            csv_content = csv_content.split("```")[0]
            
        # when has ``` csv pattern, get the content after ``` csv to the ```
        if "```" in csv_content:
            csv_content = csv_content.split("```")[1]
            csv_content = csv_content.split("```")[0]
        
        return pd.read_csv(io.StringIO(csv_content))
    except:
        st.error("Failed to load CSV")
        st.text_area("CSV", text)
        raise Exception("Failed to load CSV")