

from common.basic_criterias import none_aggreate

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


# Relevant Experience:
# Skills and Qualifications:
# Education and Training:
# Achievements and Accomplishments:
# Cultural Fit
sematic_criterias = [
    {
        "name": "Relevant Experience",
        "feature": "*",
        "aggregate_func": none_aggreate,
        "weight": 1
    },
    {
        "name": "Skills and Qualifications",
        "feature": "*",
        "aggregate_func": none_aggreate,
        "weight": 1
    },
    {
        "name": "Education and Training",
        "feature": "*",
        "aggregate_func": none_aggreate,
        "weight": 1
    },
    {
        "name": "Achievements and Accomplishments",
        "feature": "*",
        "aggregate_func": none_aggreate,
        "weight": 1
    },
]
