def markdown_to_json(markdown):
    system_instruction = """Task: Convert Resume from Markdown to JSON Format

Objective: Transform a resume presented in Markdown format into a structured JSON object, adhering to the enhanced schema provided below.

Required Output Schema:
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

    return system_instruction, markdown

def resume_to_markdown(resume):
    system_instruction = "you are an AI tasked to convert PDF resumes to markdown format. Input is text extracted from PDF resume. Output is the resume in markdown format. Retain all information from the original resume; no alterations or additional data required, only reformat the text to markdown."

    return system_instruction, resume

def extract_resume_education(resume):
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

    return system_instruction, resume

def extract_resume_projects(resume):
    system_instruction = """
Task: Extract Project Details from a Resume

**Objective:** Extract comprehensive details for each project listed in a resume to evaluate the candidate's experience accurately.

**Details to Extract:**
1. **Project Name:** Provide the name of the project.
2. **Project Description:** Describe the project in detail.
3. **Role:** Specify the candidate's role in the project.
4. **Responsibilities:** List the candidate's responsibilities in the project.
5. **Used Skills:** List all skills mentioned that were used in the project.
6. **Tech Stack:** List the technical stack used in the project.
7. **Duration:** Provide the duration of the project in months.
8. **Start Date:** Provide the start date in the format MM-YYYY.
9. **End Date:** Provide the end date in the format MM-YYYY, or specify "present" if ongoing.
10. **Team Size:** Specify the number of team members.

**Validation Rules:**
- Ensure the start date is a valid date and precedes or is equal to the end date.
- Only the last project can have an end date specified as "present".
- analyze the project description and responsibilities to identify the candidate's contribution level.

**Output Format:**
Respond in JSON format with the following structure for each project:
[
    {
        "name": "Project Name",
        "description": "Project Description",
        "role": "Role",
        "responsibilities": "Responsibilities",
        "usedSkills": ["Skill 1", "Skill 2", ...],
        "techstack": ["Tech Stack 1", "Tech Stack 2", ...],
        "duration": "Number of Months",
        "start": "MM-YYYY",
        "end": "MM-YYYY or present",
        "teamSize": "Number of Team Members"
    }
]
"""
    
    return system_instruction, resume
