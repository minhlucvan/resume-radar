import pandas as pd
import streamlit as st
import pytimeparse as ptp
import dateparser
import datetime
import json
import re
import streamlit as st
import plotly.graph_objects as go

# flatten nested dictionary
# convert nested dictionary to flat dictionary
# for example, {'a': {'b': 1, 'c': 2}} -> {'a_b': 1, 'a_c': 2}
# array support, {'a': {'b': [1, 2], 'c': 3}} -> {'a_b_0': 1, 'a_b_1': 2, 'a_c': 3 }
# nested array support, {'a': {'b': [{'c': 1}, {'c': 2}]}} -> {'a_b_0_c': 1, 'a_b_1_c': 2}
def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)


# build dataframe from flat dictionary
def build_dataframe(flat_dict):
    df = pd.DataFrame(flat_dict, index=[0])
    # transpose dataframe
    df = df.T.reset_index()
    df.columns = ['feature', 'value']
    
    # set index as feature
    df.set_index('feature', inplace=True)
    
    return df

# process data with regex
def process_data_with_regex(df, pattern, callback):

    # Filter DataFrame to include only rows where index matches the pattern
    filtered_df = df[df.index.str.match(pattern)] if pattern != '*' else df
    
    if filtered_df.empty:
        return df
    
    # Apply the callback function to the filtered DataFrame
    filtered_df['value'] = filtered_df['value'].apply(callback)

    # Update the original DataFrame with the new values
    df.update(filtered_df)
    
    return df

# convert wildcards to days
# 2 months -> 2/12
# 4 years -> 4.0
def convert_wildcards_to_year(value):
    # ignore if value is not a string
    if not isinstance(value, str):
        return value
    
    # to lower case
    value = value.lower()
    
    # remove all special characters regex
    value = re.sub(r'[^\w\s]', '', value)
    
    # if value is 4 years
    if "year" in value:
        years = int(value.split()[0])
        return years
    
    # if value is 2 months
    if "month" in value:
        months = int(value.split()[0])
        return months / 12
    
    seconds = ptp.parse(value)
    
    if seconds is None:
        return value
    
    return seconds / (60 * 60 * 24)

# convert wildcards to months
def convert_wildcards_to_month(value):
    # ignore if value is not a string
    if not isinstance(value, str):
        return value
    
    # to lower case
    value = value.lower()
    
    # remove ~
    value = value.replace("~", "")
    
    # if value is number string return as integer
    # 12 -> 12
    if value.isdigit():
        return int(value)
    
    # if value is 4 years
    if "year" in value:
        years = int(value.split()[0])
        return years * 10
    
    # if value is 2 months
    if "month" in value:
        months = int(value.split()[0])
        return months
    
    seconds = ptp.parse(value)
    
    if seconds is None:
        return value
    
    return seconds / (60 * 60 * 24 * 30)

# convert wildcards to date
# May 2020 -> 2020-05-01
def convert_wildcards_to_date(value):
    if not isinstance(value, str) or value == "":
        return value
    
    # remove ~
    value = value.replace("~", "")
    
    # if empty set value to present
    if value == "":
        return datetime.datetime.now().date()
    
    if value.lower() == "present" or value.lower() == "now":
        return datetime.datetime.now().date()
    
    # if value is a year return 01-01-year
    if value.isdigit():
        try:
            parsed_date = datetime.datetime.strptime(value, '%Y')
            
            if parsed_date is not None and parsed_date > datetime.datetime.now():
                return datetime.datetime.now().date()
            
            return parsed_date.date()
        except ValueError:
            print("Cannot parse date")
    
    
    # 2022-04
    try:
        parsed_date = datetime.datetime.strptime(value, '%Y-%m')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    # March, 2022
    try:
        parsed_date = datetime.datetime.strptime(value, '%B, %Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    # 06-2022' -> 2022-06-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%m-%Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    # 5/2020 -> 2020-05-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%m/%Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    # 05/2020 -> 2020-05-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%m/%Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
        
    # 2021/10 -> 2021-10-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%Y/%m')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    # May 2020 -> 2020-05-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%B %Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    # May 2020 -> 2020-05-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%b %Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
    
    try:
        date = dateparser.parse(value)
        if date is None:
            return value
        return date.date()
    except Exception as e:
        st.warning(f"Cannot parse value: '{value}' to date.")
    
    return value

# progress resume features
def progress_resume_features(df):
    # projects_0_duration, 2 months -> 2/12
    df = process_data_with_regex(df, "projects_\d+_duration", convert_wildcards_to_year)
    
    # WorkExperiences_totalExperiences, 4 years -> 4
    df = process_data_with_regex(df, "properties_WorkExperiences_totalExperiences", convert_wildcards_to_year)
     
    # projects_0_start, May 2020 -> 2020-05-01
    df = process_data_with_regex(df, "projects_\d+_start", convert_wildcards_to_date)
    
    # projects_0_end, May 2020 -> 2020-05-01
    df = process_data_with_regex(df, "projects_\d+_end", convert_wildcards_to_date)
    
    return df

# calculate_critical_score
def calculate_critical_score(aggreate_func, df, feature, weight, score_df):
    # filter dataframe
    filtered_df = df[df.index.str.match(feature)] if feature != '*' else df
    
    # aggregate values
    score, weight = aggreate_func(filtered_df['value'], df, score_df, weight)
    
    return score, weight

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

# calculate scores
def calculate_scores(df, criterias):
    score_df = pd.DataFrame(columns=['critical', 'score', 'weight', 'weighted_score'])
    
    # work experience score
    for value in criterias:
        criteria_name = value['name']
        criteria_feature = value['aggregate_feature'] if 'aggregate_feature' in value else value['feature']
    
        criteria_weight = value['weight']
        criteria_agg_func = value['aggregate_func']
        score, weight = calculate_critical_score(criteria_agg_func, df, criteria_feature, criteria_weight, score_df)
        weighted_score = score * weight
        
        criteria_df = pd.DataFrame({
            'critical': [criteria_name],
            'score': [score],
            'weight': [weight],
            'weighted_score': [weighted_score],
        })
        
        score_df = pd.concat([score_df, criteria_df])
        
    score_df.set_index('critical', inplace=True)
        
    return score_df
        
# enchance data
# adding new features
def enchance_data(df, criterias):
    for value in criterias:
        if 'enchance_func' not in value:
            continue
        
        criteria_enchance_func = value['enchance_func']
        
        pattern = value['feature']
        
        # Filter DataFrame to include only rows where index matches the pattern
        filtered_df = df[df.index.str.match(pattern)] if pattern != '*' else df
        
        if filtered_df.empty:
            return df
        
        if criteria_enchance_func is None:
            continue
        
        extended_df = criteria_enchance_func(filtered_df)
        
        # concat new columns
        df = pd.concat([df, pd.DataFrame(columns=extended_df.columns)], axis=1)
        
    return df

# append features
def append_features(df, criterias):
    for value in criterias:
        if 'append_func' not in value:
            continue
        
        criteria_append_func = value['append_func']
        
        if criteria_append_func is None:
            continue
        
        feature = value['append_feature'] if 'append_feature' in value else value['feature']
        
        filtered_df = df if feature == '*' else df[df.index.str.match(feature)]
        
        if filtered_df.empty:
            return df

        append_df = criteria_append_func(filtered_df)
        
        df = pd.concat([df, append_df])
        
    return df

# aggreate_front_end_experience
def aggreate_front_end_experience(values):
    return values.sum()
    
# aggreate_project_experience
def aggreate_project_experience(values, df, score_df, weight):
    
    # get work_experience_ratio
    total_projects_factor = df.loc['total_projects_factor']['value']
    total_experience = get_total_experience(df)
    
    total_projects = df.loc['total_projects']['value']
    
    mean_project_duration = total_experience / total_projects if total_projects > 0 else 0.3

    value = total_projects_factor * mean_project_duration
        
    if value == 0:
        return 0, 0
    
    return value, weight

# none aggregate function
def none_aggreate(values, _):
    return 0

def get_level(score, level_ranges):
    # sort level ranges by min value descending
    level_ranges_sorted = sorted(level_ranges, key=lambda x: x['min'], reverse=True)
    
    for level_range in level_ranges_sorted:
        if score >= level_range['min']:
            return level_range['level']
    return "Unknown"


# append_techstack_range
def append_techstack_range(df):
    nice_df = df.copy().dropna()
    # drop non string values
    nice_df = nice_df[nice_df['value'].apply(lambda x: isinstance(x, str))]
    # concatenate all techstack values as string
    all_techstack = ', '.join(nice_df['value'].values)

    # add new row total_techstack, all_techstack
    total_teckstack = pd.DataFrame({'value': [all_techstack]}, index=['Total_techstack'])
    return total_teckstack

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
        project_factor = project['contribution'] * project['complexity']
        experience_score = project_factor * dureation_years
        project['experience_score'] = experience_score
        total_projects_duration += dureation_years
        total_projects_factor += project_factor
        
    data['total_projects'] = total_projects
    data['total_projects_duration'] = total_projects_duration
    data['total_projects_factor'] = total_projects_factor
        
    return data

def preprocess_data(data, criterias=[]):
    output = data
    for value in criterias:
        if 'preprocess_func' not in value:
            continue
        
        preprocess_func = value['preprocess_func']
        
        if preprocess_func is None:
            continue
        
        output = preprocess_func(output)
    
    return output

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

def find_level(score, level_ranges):
    level = "Unknown"
    for item in level_ranges:
        if score < item["min"]:
            return level
        
        level = item["level"]
    return "Principal"

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

def dict_to_markdown(data):
    markdown = ""
    for key, value in data.items():
        markdown += f" - {key}: {value}\n"
    return markdown

# {
#         "degree": null,
#         "fieldOfStudy": "Information Technology",
#         "institution": "Cao Thang Technical College",
#         "graduationYear": "2012",
#         "gpa": null
#       }


def get_criteria_descriptions(data, df, scores_df, criterias):
    descriptions = []
    
    for value in criterias:
        if 'describe_func' not in value:
            continue
        
        describe_func = value['describe_func']
        
        if describe_func is None:
            continue
        
        description = describe_func(data, df, scores_df, value)
        descriptions.append({
            "name": value['name'],
            "description": description
        })
    
    return descriptions

def build_level_step(level_ranges, color_scale=None):
    steps = []
    
    for item in level_ranges:
        # Determine the appropriate color based on the level
        if item["level"] in color_scale:
            color = color_scale[item["level"]]
        else:
            # white color
            color = "#FFFFFF"
        
        steps.append({'range': [item["min"], 100], 'color': color})
    return steps

def describe_work_experience(data, df, scores_df, value):
    total_experience = get_total_experience(df)
    nice_total_experience = round(total_experience, 2)
    return f"Total experience: {nice_total_experience} years"

# plot_skill_level
# plot chart with score and level ranges
# a progress bar chart with score and level ranges
def plot_skill_level(score, level_ranges, title="Skill Level"):
    # Define the color scale
    #00876c
    #439a72
    #6aad78
    #8fbf80
    #b4d18b
    #d9e398
    #fff4a8
    #fbd88a
    #f7bc72
    #f19f60
    #eb8055
    #e16050
    #d43d51
    color_scale = {
        "Intern": "#008728",
        "Fresher-": "#00876c",
        "Fresher": "#439a72",
        "Fresher+": "#6aad78",
        "Junior-": "#8fbf80",
        "Junior": "#b4d18b",
        "Junior+": "#d9e398",
        "Middle-": "#fff4a8",
        "Middle": "#fbd88a",
        "Middle+": "#f7bc72",
        "Senior-": "#f19f60",
        "Senior": "#eb8055",
        "Senior+": "#e16050",
        "Principal": "#d43d51",
    }
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': title},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 100]},
            'steps' : build_level_step(level_ranges, color_scale),
            'threshold' : {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            },
            'bar': {
                'color': "black",
                'thickness': 0.05
            }
        }
    ))
    
    level_ranges_reversed = level_ranges[::-1]
    
    # adding legend for level ranges
    for item in level_ranges_reversed:
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=10, color=color_scale[item["level"]]),
            name=item["level"]
        ))
        
    # remove x and y axis
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    
    return fig

# Streamlit app
def evaluate_resume(data_dict, print=False):
    # define sample criteria
    criterias = [
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

    if print:
        st.write(data_dict['data'])

    # preprocess data
    processed_data = preprocess_data(data_dict, criterias)
    
    # Flatten dictionary
    flat_data = flatten_dict(processed_data)

    # Build dataframe
    df = build_dataframe(flat_data)
    
    # clean data
    clean_data = progress_resume_features(df)
    
    if print:
        st.write("Cleaned data")
        st.dataframe(clean_data, use_container_width=True)
    
    # append new features
    extended_data = append_features(clean_data, criterias)
    if print:
        st.write("Extended data")
        st.dataframe(extended_data, use_container_width=True)
    
        
    level_ranges = [
        {"level": "Intern", "min": 0},
        
        {"level": "Fresher-", "min": 10},
        {"level": "Fresher", "min": 15},
        {"level": "Fresher+", "min": 20},
        
        {"level": "Junior-", "min": 25},
        {"level": "Junior", "min": 32},
        {"level": "Junior+", "min": 39},
        
        {"level": "Middle-", "min": 45},
        {"level": "Middle", "min": 52},
        {"level": "Middle+", "min": 59},
        
        {"level": "Senior-", "min": 68},
        {"level": "Senior", "min": 78},
        {"level": "Senior+", "min": 88},
        
        {"level": "Principal", "min": 98}
    ]
    
    


    # level_ranges_df = pd.DataFrame(level_ranges)
    # level_ranges_df.set_index('level', inplace=True)
    
    # st.write("Level ranges")
    # st.dataframe(level_ranges_df, use_container_width=True)
    
    # enchance data
    enchanced_data = enchance_data(extended_data, criterias)
    
    if print:
        st.write("Enchanced data")
        st.dataframe(enchanced_data, use_container_width=True)
    
    # Calculate scores
    scores_df = calculate_scores(enchanced_data, criterias)
  
    # total score
    total_score = calculate_total_score(scores_df)
    
    st.write(f"#### Total score: {total_score}")
    st.write("Scores")
    st.dataframe(scores_df, use_container_width=True)
    
    # final level
    level = get_level(total_score, level_ranges)
    
    candidate_name = enchanced_data.loc['properties_General_name']['value'] if 'properties_General_name' in enchanced_data.index else "Unknown"

    fig = plot_skill_level(total_score, level_ranges, candidate_name)
    
    st.plotly_chart(fig, use_container_width=True)
    
    
    descriptions = get_criteria_descriptions(processed_data, enchanced_data, scores_df, criterias)

    return level, descriptions
    

