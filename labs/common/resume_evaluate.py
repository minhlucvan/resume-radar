import pandas as pd
import streamlit as st
import pytimeparse as ptp
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
import dateparser
import datetime
import json
import re

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
    filtered_df = df[df.index.str.match(pattern)]
    
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
    
    if value.lower() == "present" or value.lower() == "now":
        return datetime.datetime.now().date()
    
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
def calculate_critical_score(df, feature, aggreate_func):
    # filter dataframe
    filtered_df = df[df.index.str.match(feature)]
    
    if filtered_df.empty:
        return 0
    
    # aggregate values
    score = aggreate_func(filtered_df['value'], df)
    
    return score

# aggregate total work experience
def aggreate__total_work_experience(values, df):
    value = values.sum()
        
    if 'work_experience_duration' in df.index:
        value = df.loc['work_experience_duration']['value']  
    elif 'first_work_experience' in df.index and 'last_work_experience' in df.index:
        first_work_apperance = df.loc['first_work_experience']['value']
        last_work_apperance = df.loc['last_work_experience']['value']
        
        if first_work_apperance is None or last_work_apperance is None:
            return 0
        
        total_experience = last_work_apperance - first_work_apperance
        
        value = total_experience.days / 365
        
    return value * 10

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
        
        score = calculate_critical_score(df, criteria_feature, criteria_agg_func)
        weighted_score = score * criteria_weight
        
        criteria_df = pd.DataFrame({
            'critical': [criteria_name],
            'score': [score],
            'weight': [criteria_weight],
            'weighted_score': [weighted_score]
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
        filtered_df = df[df.index.str.match(pattern)]
        
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
def aggreate_project_experience(values, df):
    # complexity_feature = "projects_\d+_complexity"
    # complexcity_df = df[df.index.str.match(complexity_feature)]
    # complexcity_mean = complexcity_df['value'].mean()
    
    # contribution_feature = "projects_\d+_contribution"
    # contribution_df = df[df.index.str.match(contribution_feature)]
    # contribution_mean = contribution_df['value'].mean()
    
    # # work_experience_duration
    # work_experience_duration = df.loc['work_experience_duration']['value']
    
    # value = work_experience_duration * (complexcity_mean * contribution_mean)
    
    # return value
    
    # get work_experience_ratio
    work_experience_ratio = df.loc['work_experience_ratio']['value']
    work_experience_ratio = work_experience_ratio if work_experience_ratio is not None else 1
    value = values.sum()
    
    scaled_value = value * work_experience_ratio
    
    return scaled_value / 12.5 * 10

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
        
    
    data['total_empoyment_experience'] = total_duration
    data['total_empoyment_duration'] = total_experience
    
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
    for project in data['projects']:
        try:
            dureation = convert_wildcards_to_month(project['duration'])
            
            # define duration is 3 months
            if dureation is None or dureation == 0:
                dureation = 3
            
            dureation_years = dureation / 12
        except Exception as e:
            st.warning("Duration is not defined, setting default value to 3 months")
            dureation = 3
            dureation_years = 3 / 12
            
        project['duration_years'] = dureation_years
        experience_score = project['contribution'] * (project['complexity'] * dureation_years)
        project['experience_score'] = experience_score
    
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

def aggreate_empoyment_duration(values, df):
    return values.sum() * 10

def append_first_work_experience(df):
    append_df = pd.DataFrame(columns=df.columns)
    
    # projects_0_start
    start_project_partern = "projects_\d+_start"
    start_project_partern_df = df[df.index.str.match(start_project_partern)].dropna()
    
    # get first work experience by min value
    first_work_experience = start_project_partern_df[start_project_partern_df['value'] == start_project_partern_df['value'].min()]
    first_work_experience_df = pd.DataFrame([first_work_experience.values[0]], columns=append_df.columns, index=['first_work_experience'])
    
    if not first_work_experience_df.empty:
        append_df = pd.concat([append_df, first_work_experience_df])
    
    # projects_0_end
    end_project_partern = "projects_\d+_end"
    end_project_partern_df = df[df.index.str.match(end_project_partern)].dropna()
    
    # last work experience is the max value
    last_work_experience_values = end_project_partern_df[end_project_partern_df['value'] == end_project_partern_df['value'].max()]
    last_work_experience_df = pd.DataFrame([last_work_experience_values.values[0]], columns=append_df.columns, index=['last_work_experience'])
    
    if not last_work_experience_df.empty:    
        append_df = pd.concat([append_df, last_work_experience_df])
        
    if not last_work_experience_df.empty and not first_work_experience_df.empty:
        work_experience_duration = last_work_experience_df['value'].values[0] - first_work_experience_df['value'].values[0]
        work_experience_duration_value = work_experience_duration.days / 365 if isinstance(work_experience_duration, datetime.timedelta) else work_experience_duration
        work_experience_duration_df = pd.DataFrame([work_experience_duration_value], columns=append_df.columns, index=['work_experience_duration'])
        
        if not work_experience_duration_df.empty:
            append_df = pd.concat([append_df, work_experience_duration_df])
    
    # projects_4_duration_years
    work_experience_duration_partern = "projects_\d+_duration_years"
    work_experience_duration_values = df[df.index.str.match(work_experience_duration_partern)]
        
    # total project duration
    total_work_experience = work_experience_duration_values['value'].sum()
    
    total_work_experience_df = pd.DataFrame([total_work_experience], columns=append_df.columns, index=['total_work_experience'])
    
    if not total_work_experience_df.empty:
        append_df = pd.concat([append_df, total_work_experience_df])
        
    # set a ratio between work_experience_duration and total_work_experience
    if not work_experience_duration_df.empty and not total_work_experience_df.empty:
        work_experience_ratio = work_experience_duration_df['value'].values[0] / total_work_experience_df['value'].values[0]
        work_experience_ratio_df = pd.DataFrame([work_experience_ratio], columns=append_df.columns, index=['work_experience_ratio'])
        
        if not work_experience_ratio_df.empty:
            append_df = pd.concat([append_df, work_experience_ratio_df])

    return append_df

# Streamlit app
def evaluate_resume(data, print=False):
    # define sample criteria
    criterias = [
        {
          "name": "Employment Duration",
            # total_empoyment_experience 
            "feature": "total_empoyment_experience",
            'aggregate_func': aggreate_empoyment_duration,
            "preprocess_func": preprocess_empoyment_history,
            'weight': 1,
        },
        {
            "name": "Work Experience",
            # properties_WorkExperiences_totalExperiences
            "feature": "total_empoyment_duration",
            "weight": 1,
            # match all features
            'append_feature': '*',
            'append_func': append_first_work_experience,
            "aggregate_func": aggreate__total_work_experience,
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
            "min_value": 2,
        }
    ]
    
    data_dict = json.loads(data)
    
    if isinstance(data_dict, str):
        data_dict = json.loads(data_dict)
        
    if print:
        st.write("Data")
        st.write(data_dict['data'])

    # preprocess data
    processed_data = preprocess_data(data_dict, criterias)
    
    # Flatten dictionary
    flat_data = flatten_dict(processed_data)

    # Build dataframe
    df = build_dataframe(flat_data)
    
    # clean data
    clean_data = progress_resume_features(df)
    
    st.write("Cleaned data")
    # st.dataframe(clean_data, use_container_width=True)
    
    # append new features
    extended_data = append_features(clean_data, criterias)
    st.write("Extended data")
    # st.dataframe(extended_data, use_container_width=True)
    
    # enchance data
    enchanced_data = enchance_data(extended_data, criterias)
    st.write("Enchanced data")
    st.dataframe(enchanced_data, use_container_width=True)
    
    # Calculate scores
    scores_df = calculate_scores(enchanced_data, criterias)
    st.write("Scores")
    st.dataframe(scores_df, use_container_width=True)
    
    # total score
    total_score = calculate_total_score(scores_df)
    st.write(f"#### Total score: {total_score}")
    
    level_ranges = [
        {"level": "Fresh-", "min": 0},
        {"level": "Fresh", "min": 5},
        {"level": "Fresh+", "min": 10},
        
        {"level": "Junior-", "min": 15},
        {"level": "Junior", "min": 22},
        {"level": "Junior+", "min": 29},
        
        {"level": "Mid-", "min": 35},
        {"level": "Mid", "min": 42},
        {"level": "Mid+", "min": 49},
        
        {"level": "Senior-", "min": 58},
        {"level": "Senior", "min": 68},
        {"level": "Senior+", "min": 78},
    ]
    
    # final level
    level = get_level(total_score, level_ranges)
    
    return level
    
