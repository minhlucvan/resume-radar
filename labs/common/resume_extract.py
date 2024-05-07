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

import getpass
import os

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

# extract structured data
# create a prompt template to extract structured data
# pass the data to the prompt template
# extract the structured data from the data


def extract_structured_data(data):
    """
    At the command line, only need to run once to install the package via pip:

    $ pip install google-generativeai
    """

    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

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

    system_instruction = """You are recruitGPT, an AI tasked with processing resumes. Given a resume in markdown format, extract the information provided and follow the template below. Only use the information provided in the resume.

### General
- Name
- Date of Birth
- Desired Position

### Contacts
- Phone Number
- GitHub Profile
- Email Address
- LinkedIn Profile

### Work Experience
- Total Years of Experience
- Graduation Date

### Work History
- Company Name:
    + Start Date:
    + End Date:
    + Duration:
    + Position:

### Skillset
- ProgrammingLanguages: []
- Frameworks: []
- Databases: []
- UserInterfaces: []
- Clouds: []
- Tools: []
- Other: []

### Projects
- Project Name
    + Duration:
    + Information:
    + Responsibilities:
    + Tech Stack:
    + Team Size:
"""

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  system_instruction=system_instruction,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[])

    convo.send_message(data)
    return convo.last.text

# extract data from text
# create a prompt template to extract data from text
# pass the text to the prompt template
# extract the data from the text


def extract_data(text):
    """
    At the command line, only need to run once to install the package via pip:

    $ pip install google-generativeai
    """

    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

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

    system_instruction = "you are an AI tasked to convert PDF resumes to markdown format. Input is text extracted from PDF resume. Output is the resume in markdown format. Retain all information from the original resume; no alterations or additional data required, only reformat the text to markdown."

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  system_instruction=system_instruction,
                                  safety_settings=safety_settings)

    prompt_parts = [
        text
    ]

    response = model.generate_content(
        prompt_parts, request_options={"timeout": 600})
    return response.text

# extract pdf text
# create a pdf reader
# extract text from the pdf

# extract json from text


def extract_json(text):
    """
    At the command line, only need to run once to install the package via pip:

    $ pip install google-generativeai
    """

    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

    # Set up the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
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

    system_instruction = """Task: Convert Resume from Markdown to JSON Format

Objective: Transform a resume presented in Markdown format into a structured JSON object, adhering to the enhanced schema provided below.

Required Output Schema:

json
Copy code
{
  "General": {
    "name": "",
    "born": "",
    "position": ""
  },
  "Contacts": {
    "phone": "",
    "email": "",
    "LinkedIn": "",
    "GitHub": ""
  },
  "EmploymentHistory": [
    {
      "companyName": "",
      "type": "", 
      "startDate": "",
      "endDate": "",
      "position": "",
      "responsibility": "",
      "level": 0  // Level codes: 0-Internship, 1-Junior, 2-Mid, 3-Senior, 4-Leader/Manager, 5-Chief Levels
    }
  ]
}
Detailed Instructions:

Input Analysis:
Review the Markdown input to identify and categorize data according to the JSON schema elements: General, Contacts, and EmploymentHistory, including the new "level" field.
Data Transformation:
Convert the data from the Markdown format into corresponding JSON key-value pairs as defined in the schema. Carefully fill in each field:
For "EmploymentHistory", capture details like company name, employment type (e.g., full-time, part-time, freelance), start and end dates, position title, primary responsibilities, and the employment level based on predefined codes.
Validation:
Ensure the transformed JSON conforms exactly to the structure outlined in the output schema, including the new "level" field, and contains no extraneous keys.
Formatting:
Format the JSON output to be clear and readable, with proper indentation and spacing.
Additional Notes:

Direct mapping of Markdown fields to JSON keys is crucial. Ensure consistency in data types and date formats to comply with standard JSON formatting norms.
The "level" field should use integer values to represent the professional level as follows: 0 (Internship), 1 (Junior level or equivalent), 2 (Mid-level or equivalent), 3 (Senior level or equivalent), 4 (Leader or Manager), 5 (Chief levels).
"""

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  system_instruction=system_instruction,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[])

    convo.send_message(text)

    response = convo.last.text

    # get content ```json content ```
    json_content = response.replace('```json\n', '').replace('```', '')

    return json_content


def extract_pdf_text(pdf):
    pdf_reader = PdfReader(pdf)

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    return text

def extract_education_data(text):
    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

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
Task: Extract education details and certifications from a resume.

Instructions:

1. Extract education details and certifications from the resume provided.
2. Ensure accurate extraction of the following information:
   - Degree(s) obtained
   - Field(s) of study
   - University or School(s) attended
   - Graduation year(s)
   - GPA (if available)
   - Certifications obtained
   - Certification issuer(s)
   - Certification year(s)
3. Provide the extracted information in a JSON response with the following structure:

JSON Response Structure:
{
    "education": [
        {
            "degree": "Degree",
            "fieldOfStudy": "Field of Study",
            "institution": "University or School",
            "graduationYear": "YYYY",
            "gpa": "GPA (if available)"
        },
        ...
    ],
    "certifications": [
        {
            "name": "Certification Name",
            "issuer": "Certification Issuer",
            "year": "YYYY"
        },
        ...
    ]
}
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

    return json_content    

# extract project data
def extract_project_data(text):

    genai.configure(api_key=os.getenv("GENAI_API_KEY"))

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

    system_instruction = """Extract project details from a resume, including project name, complexity, used skills, tech stack, contribution, duration, start date, end date, team size, and project type for each project.

For each project:
- Provide the project name.
- Rate the complexity from 1 to 5 based on the project description and tech stack, where:
    - 1 represents a project with a basic stack or monolithic architecture, typically involving straightforward technologies and minimal integration challenges.
    - 2 represents a project with some complexity, potentially involving moderate integration challenges or the use of emerging technologies.
    - 3 represents a project with moderate complexity, involving multiple technologies or frameworks, moderate integration challenges, and possibly some scalability considerations.
    - 4 represents a project with high complexity, involving advanced technologies or frameworks, extensive integration challenges, significant scalability considerations, and potentially some distributed system components.
    - 5 represents a project with very high complexity, involving highly advanced technologies, extensive integration challenges across distributed systems, significant scalability requirements, and potentially microservices architecture.
- List all skills mentioned by the candidate that were used in the project.
- List the technical stack used in the project.
- Rate the contribution of the candidate to the project from 1 to 5, where:
    - 1 represents a developer with minimal impact on project decisions or leadership.
    - 2 represents a developer with some impact on project decisions or leadership.
    - 3 represents a developer with moderate impact on project decisions or leadership, or a junior technical leader.
    - 4 represents a developer with significant impact on project decisions or leadership, or a senior technical leader.
    - 5 represents a developer with critical impact on project decisions or leadership, or a principal technical leader.
- Provide the duration of the project in months.
- Provide the start date of the project in the format MM-YYYY.
- Provide the end date of the project in the format MM-YYYY, or specify "present" if the project is ongoing.
- Provide the team size for the project.
- Specify the project type as one of the following:
    - "pro" for professional projects.
    - "training" for projects undertaken during training or education.
    - "side" for side projects or personal projects.

Ensure that:
- The project start date is a valid date and precedes or is equal to the end date.
- Only the last project can have an end date specified as "present".

Respond in JSON format with the following structure for each project:
[{ 
    "name": "Project Name",
    "complexity": 1-5,
    "usedSkills": ["Skill 1", "Skill 2", ...],
    "techstack": ["Tech Stack 1", "Tech Stack 2", ...],
    "contribution": 1-5,
    "duration": "Number of Months",
    "start": "MM-YYYY",
    "end": "MM-YYYY or present",
    "teamSize": "Number of Team Members",
    "type": "pro/training/side"
}]
"""

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  system_instruction=system_instruction,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    convo.send_message(text)
    response = convo.last.text

    # extract content ```json content ```
    json_content = response.replace('```json\n', '').replace('```', '')

    return json_content

# load pdf from url
# return the pdf content as File the same as the uploaded file
def load_pdf_from_url(pdf_url):
    response = requests.get(pdf_url)
    pdf = response.content
    
    # create a file from the pdf content
    with open('temp.pdf', 'wb') as f:
        f.write(pdf)
    
    file = open('temp.pdf', 'rb')
    
    return file

def extract_resume(url_or_file):

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
        st.write('Extracted text:')

    with st.spinner("Extracting data from text..."):
        data = extract_data(text)
        st.write('Extracted data:')
        st.write(data)

    # extract yml from structured data
    with st.spinner("Extracting yml from structured data..."):
        json_data = extract_json(data)
        st.write('Extracted Json:')

    # extract project data
    with st.spinner("Extracting project data..."):
        project_data = extract_project_data(text)
        st.write('Extracted project data:')
        
    with st.spinner("Extracting education data..."):
        education_data = extract_education_data(text)
        st.write('Extracted education data:')
        st.text_area("Extracted education data", education_data)

    # combine all the extracted data into a dictionary
    parsed_yml = json.loads(json_data)

    parsed_project_data = json.loads(project_data)
    
    parsed_education_data = json.loads(education_data)

    extracted_data = {
        "text": text,
        "data": data,
        "properties": parsed_yml,
        "projects": parsed_project_data,
        "educations": parsed_education_data
    }

    extracted_data_json = json.dumps(extracted_data, indent=4)
    
    st.text_area("Extracted data", extracted_data_json)
    
    return extracted_data_json
