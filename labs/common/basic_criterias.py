import pandas as pd
import streamlit as st
import pytimeparse as ptp
import dateparser
import datetime
import json
import re
import streamlit as st
import plotly.graph_objects as go
from common.utils import convert_wildcards_to_date, convert_wildcards_to_month

# calculate_total_score
def calculate_total_score(df):
    # weighted mean of scores
    return (df['weighted_score'].sum() / df['weight'].sum())

def aggreate_empoyment_duration(values, df, score_df, weight):
    return values.sum() * 10, weight

def education_aggreate(values, df, score_df, weight):
    current_score = calculate_total_score(score_df)
    if values.empty:
        return 0, 0
    
    return current_score + 10, weight

def certification_aggreate(values, df, score_df, weight):
    current_score = calculate_total_score(score_df)
    if values.empty:
        return 0, 0
    
    value = values.count() * 2.4
    return current_score + value, weight

def describe_empoyment_history(data, df, scores_df, value):
    empoyment_values = data['properties']['EmploymentHistory']
    empoyment_df = pd.DataFrame(empoyment_values)
    
    return empoyment_df.to_markdown()

def describe_project_experience(data, df, scores_df, value):
    projects_values = data['projects']
    projects_df = pd.DataFrame(projects_values)
    
    projects_df['usedSkills'] = projects_df['usedSkills'].apply(lambda x: ', '.join(x))
    projects_df['techstack'] = projects_df['techstack'].apply(lambda x: ', '.join(x))
    
    return projects_df.to_markdown()

def describe_education(data, df, scores_df, value):
    educations_values = data['educations']['education']
    education_df = pd.DataFrame(educations_values)
    
    return education_df.to_markdown()

def describe_certifications(data, df, scores_df, value):
    certifications_values = data['educations']['certifications']
    certification_df = pd.DataFrame(certifications_values)
    
    return certification_df.to_markdown()

# validate_employment_history that startDate is before endDate and no overlapping
def validate_employment_history(data):
    employment_history = data['properties']['EmploymentHistory']
    
    for i, employment in enumerate(employment_history):
        if 'startDate' not in employment or 'endDate' not in employment:
            continue
        
        start_date = employment['startDate']
        end_date = employment['endDate']
        
        if start_date is None or end_date is None:
            continue

        if start_date > end_date:
            return False
        
        if i == len(employment_history) - 1:
            break
        
        next_start_date = employment_history[i + 1]['startDate']
        
        if end_date > next_start_date:
            return False
            
    return True

def convert_empoyment_history_to_date(data):
    for employment in data['properties']['EmploymentHistory']:
        if 'startDate' in employment:
            start_date = convert_wildcards_to_date(employment['startDate'])
            employment['startDate'] = start_date
            
        if 'endDate' in employment:
            end_date = convert_wildcards_to_date(employment['endDate'])
            employment['endDate'] = end_date

    return data

def calc_employment_duration(data):
    employment_history = data['properties']['EmploymentHistory']
    total_duration = 0
    
    for employment in employment_history:
        if 'startDate' not in employment or 'endDate' not in employment:
            continue
        
        start_date = employment['startDate']
        end_date = employment['endDate']
        
        if start_date is None or end_date is None:
            continue
        
        duration = end_date - start_date
        duration_years = duration.days / 365 if isinstance(duration, datetime.timedelta) else duration
        total_duration += duration_years
        employment['duration'] = duration_years
    
    data['total_empoyment_duration'] = total_duration
    
    return data

# calculate employment experience
# employment experience =
def calc_employment_experience(data):
    employment_history = data['properties']['EmploymentHistory']
    total_experience = 0
    total_duration = 0
    
    for employment in employment_history:
        if 'startDate' not in employment or 'endDate' not in employment:
            continue
        
        start_date = employment['startDate']
        end_date = employment['endDate']
        
        if start_date is None or end_date is None:
            continue
        
        duration = end_date - start_date
        duration_years = duration.days / 365 if isinstance(duration, datetime.timedelta) else duration
        employment['duration'] = duration_years
        total_duration += duration_years
        
        # caculate level
        if 'level' not in employment:
            employment['level'] = 1
        
        # level a enum: 0 = intern, 1 = junior, 2 = mid, 3 = senior, 4 = lead, 5 = chief
        level = employment['level'] if employment['level'] > 0 else 1
        
        # consider intern as 0.5
        if level == 0:
            level = 0.5
        
        # caculate experience = duration_years * level
        experience = duration_years * level
        employment['experience'] = experience
        total_experience += experience
        
    
    data['total_empoyment_experience'] = total_experience
    data['total_empoyment_duration'] = total_duration
    
    return data



def preprocess_empoyment_history(data):
    data = convert_empoyment_history_to_date(data)    

    retried = 0
    
    while not validate_employment_history(data) and retried < 2:     
        data = correct_employment_history(data)
        retried += 1
    
    data = calc_employment_duration(data)
    
    data = calc_employment_experience(data)
    
    return data

def sort_employment_history(employment_history):
    sorted_history = sorted(employment_history, key=lambda x: x['startDate'])
    return sorted_history

# correct_employment_history
# fill overlapping end date with the next start date
def correct_employment_history(data):
    employment_history = data['properties']['EmploymentHistory']

    employment_history = sort_employment_history(employment_history)
    
    # loop through employment history
    # if end_date 1 is greater than start_date 2
    # set end_date 1 to start_date 2
    for i, employment in enumerate(employment_history):
        if i == len(employment_history) - 1:
            break
        
        end_date = employment['endDate']
        next_start_date = employment_history[i + 1]['startDate']
        
        if end_date > next_start_date:
            employment['endDate'] = next_start_date
        
    data['properties']['EmploymentHistory'] = sort_employment_history(employment_history)
    
    return data

# preprocess_data
def preprocess_projects(data):
    # process data.projects.experience_score = data.projects.contribution * (data.projects.complexity * data.projects.duration/12 )
    total_projects = len(data['projects'])
    total_projects_duration = 0
    total_projects_factor = 0
    for project in data['projects']:
        try:
            dureation = convert_wildcards_to_month(project['duration'])
            
            # define duration is 3 months
            if dureation is None or dureation < 3:
                dureation = 3
            
            dureation_years = dureation / 12
        except Exception as e:
            st.warning("Duration is not defined, setting default value to 3 months")
            dureation = 3
            dureation_years = 3 / 12
            
        project['duration_years'] = dureation_years
        project['complexity'] = project['complexity'] if 'complexity' in project else 1
        project_factor = project['contribution'] * project['complexity']
        experience_score = project_factor * dureation_years
        project['experience_score'] = experience_score
        project['project_factor'] = project_factor
        total_projects_duration += dureation_years
        total_projects_factor += project_factor
        
    data['total_projects'] = total_projects
    data['total_projects_duration'] = total_projects_duration
    data['total_projects_factor'] = total_projects_factor
        
    return data


# aggregate total work experience
def aggreate__total_work_experience(values, df, score_df, weight):
    value = get_total_experience(df)
    
    return value * 10, weight

# aggregate techstack range
def aggreate_techstack_range(values):
    return len(values)

def aggreate_skills_range(values):
    return len(values)

def enchance_frontend_experience(df):
    enchanced_df = pd.DataFrame(columns=['Frontend_experience'])
    df.index = df.index
    
    return enchanced_df

def append_frontend_experience(df):
    frontend_experience_df = pd.DataFrame(columns=df.columns)
    
    return frontend_experience_df


def get_total_experience(df):
    if 'total_empoyment_duration' in df.index:
        return df.loc['total_empoyment_duration']['value']
    elif 'total_empoyment_duration' in df.index:
        return df.loc['total_empoyment_duration']['value']
    elif 'work_experience_duration' in df.index:
        return df.loc['work_experience_duration']['value']  
    elif 'first_work_experience' in df.index and 'last_work_experience' in df.index:
        first_work_apperance = df.loc['first_work_experience']['value']
        last_work_apperance = df.loc['last_work_experience']['value']
        
        if first_work_apperance is None or last_work_apperance is None:
            return 0
        
        total_experience = last_work_apperance - first_work_apperance
        
        return total_experience.days / 365
    return 0

def describe_work_experience(data, df, scores_df, value):
    total_experience = get_total_experience(df)
    nice_total_experience = round(total_experience, 2)
    return f"Total experience: {nice_total_experience} years"


# aggreate_project_experience
def aggreate_project_experience(values, df, score_df, weight):
    
    # get work_experience_ratio
    total_projects_factor = df.loc['total_projects_factor']['value']
    total_experience = get_total_experience(df)
    
    total_projects_factor = df.loc['total_projects_factor']['value']
    
    total_projects = df.loc['total_projects']['value']
    
    mean_project_factor = total_projects_factor / total_projects if total_projects > 0 else 0

    value = mean_project_factor * total_experience
        
    if value == 0:
        return 0, 0
    
    return value, weight

# none aggregate function
def none_aggreate(values, _, __, ___):
    return 0, 0

basic_criterias = [
    {
        "name": "Employment Experience",
        # total_empoyment_experience 
        "feature": "total_empoyment_experience",
        'aggregate_func': aggreate_empoyment_duration,
        "preprocess_func": preprocess_empoyment_history,
        'describe_func': describe_empoyment_history,
        'weight': 0,
    },
    {
        "name": "Work Experience",
        # properties_WorkExperiences_totalExperiences
        "feature": "*",
        "weight": 1,
        # match all features
        'append_feature': '*',
        "aggregate_func": aggreate__total_work_experience,
        "describe_func": describe_work_experience,
        "min_value": 2,
        "max_value": 5
    },
    {
        "name": "Project Experience",
        # projects_7_experience_score
        "feature": "projects_\d+_experience_score",
        "weight": 1,
        "aggregate_func": aggreate_project_experience,
        'preprocess_func': preprocess_projects,
        'describe_func': describe_project_experience,
        "min_value": 2,
    },
    {
        "name": "Deegree",
        # educations_education_1_institution
        "feature": "educations_education_\d+_institution",
        'aggregate_func': education_aggreate,
        "describe_func": describe_education,
        "weight": 1,
    },
    {
        "name": "certifications",
        # educations_certifications_1_name
        "feature": "educations_certifications_\d+_name",
        'aggregate_func': certification_aggreate,
        "describe_func": describe_certifications,
        "weight": 1,
    },
]
