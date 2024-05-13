import pandas as pd
from common.visualize import plot_skill_level
import streamlit as st
import pytimeparse as ptp
import dateparser
import datetime
import json
import re
import streamlit as st
import plotly.graph_objects as go
from common.utils import convert_wildcards_to_year, convert_wildcards_to_date

from common.basic_criterias import basic_criterias, calculate_total_score

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

def get_level(score, level_ranges):
    # sort level ranges by min value descending
    level_ranges_sorted = sorted(level_ranges, key=lambda x: x['min'], reverse=True)
    
    for level_range in level_ranges_sorted:
        if score >= level_range['min']:
            return level_range['level']
    return "Unknown"


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


# Streamlit app
def evaluate_resume(data_dict, print=False):
    # define sample criteria
    criterias = basic_criterias
    
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
    

