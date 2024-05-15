

from common.basic_criterias import none_aggreate
import pandas as pd
from common import llm_model
from common import prompts
import io
import streamlit as st

# 1. **Relevant Experience:**
#    - Look for candidates whose previous work experience aligns closely with the job requirements. This includes the type of roles they've held, the industries they've worked in, and the specific tasks they've performed.

# 2. **Skills and Qualifications:**
#    - Identify the key skills and qualifications necessary for the position. This could include technical skills, certifications, language proficiency, and soft skills. Ensure that the candidates possess these skills at the required level.

# 3. **Education and Training:**
#    - Review the educational background of candidates to ensure they have the necessary academic qualifications. Pay attention to the level of education, relevant courses, and any additional training or certifications that might be pertinent to the job.

# 4. **Achievements and Accomplishments:**
#    - Look for evidence of significant achievements in their previous roles. This can include awards, recognitions, successful projects, or any quantifiable accomplishments that demonstrate their capabilities and potential impact.

# 5. **Cultural Fit:**
#    - Consider how well the candidate might fit into your company’s culture and values. Look for signs of alignment with your organization's mission, values, and working style. This can often be inferred from their personal interests, volunteer work, and the way they describe their work experiences.

FRONT_END_SKILLS_AND_QUALIFICATIONS_METRICS_PATH = "data/metrics/front_end_skills_and_qualifications_metrics.csv"

def evalue_skill_and_qualifications(scores, df, __, ___):
    score = scores.sum()
    return score, 1

def describe_skill_and_qualifications(data, df, scores_df, value):
    return data['sematic_description']

def preprocess_skill_and_qualifications(data):
    resume = data['data']
    
    df = pd.read_csv(FRONT_END_SKILLS_AND_QUALIFICATIONS_METRICS_PATH)
    # Adding  column ID from index
    df['ID'] = df.index
    # set ID as index
    df.set_index('ID', inplace=True)
    
    criteria = df.to_markdown()
    system_instruction, prompt = prompts.evaluate_resume(resume, criteria)
    # st.write(system_instruction, prompt)
    output = llm_model.run(system_instruction, prompt, is_csv=True)
    
    # merge output with df on ID
    evaluation_df = pd.merge(df, output, on='ID')
    
    # add score column = Level * Evaluation
    evaluation_df['Score'] = evaluation_df['Level'] * evaluation_df['Evaluation']
    
    score = evaluation_df['Score'].sum()
    
    # description data frame
    descriptions_df = evaluation_df[["Level", "Criteria","Description", "Evaluation", "Score"]]
    
    # adding icon for evaluation column check or cross
    descriptions_df['Evaluation'] = descriptions_df['Evaluation'].apply(lambda x: '✅' if x == 1 else '❌')
    
    descriptions = descriptions_df.to_markdown()
    
    data['sematic_score'] = score
    data['sematic_description'] = descriptions
    
    return data

# Relevant Experience:
# Skills and Qualifications:
# Education and Training:
# Achievements and Accomplishments:
# Cultural Fit
sematic_criterias = [
    {
        "name": "Semantics: Skills and Qualifications",
        "feature": "sematic_score",
        'preprocess_func': preprocess_skill_and_qualifications,
        "aggregate_func": evalue_skill_and_qualifications,
        "describe_func": describe_skill_and_qualifications,
        "weight": 1
    },
]
