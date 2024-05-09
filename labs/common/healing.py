# chat_pdf.py
import os
import google.generativeai as genai
import json
import os
import re
from common import env
import streamlit as st

# fix broken json
def fix_broken_json(text):
    
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

    # extract content ```json content ```
    json_content = response.replace('```json\n', '').replace('```', '')
    
    # # remove any // comments to the end of the line
    # json_content = re.sub(r'//.*', '', json_content)
    
    # # remove all content before the first { and after the last }
    # first_brace_index = json_content.find("{")
    # last_brace_index = json_content.rfind("}")
    # first_square_brace_index = json_content.find("[")
    # last_square_brace_index = json_content.rfind("]")
    
    # if first_square_brace_index < first_brace_index:
    #     first_brace_index = first_square_brace_index 
    
    # if last_square_brace_index > last_brace_index:
    #     last_brace_index = last_square_brace_index
    
    # if first_brace_index > 0:
    #     json_content = json_content[first_brace_index:]
    
    # if last_brace_index < len(json_content) - 1:
    #     json_content = json_content[:last_brace_index + 1]
    
    return json_content

def load_json_attempt(text):
    try:
        return json.loads(text)
    except:
        st.warning("Failed to load JSON, attempting to fix it")
        nice_json = fix_broken_json(text)
        try:
            return json.loads(nice_json)
        except:
            st.error("Failed to fix JSON")
            st.text_area("Broken JSON", nice_json)
            raise Exception("Failed to fix JSON")
