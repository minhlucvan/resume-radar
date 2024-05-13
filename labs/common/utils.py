import datetime
import dateparser
import streamlit as st
import re
import pytimeparse as ptp

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
    
    if value.lower() == "present" or value.lower() == "now" or value.lower() == "hiện tại":
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
    
    # 22/04/2024
    try :
        parsed_date = datetime.datetime.strptime(value, '%d/%m/%Y')
        return parsed_date.date()
    except ValueError:
        print("Cannot parse date")
        
    # 2023-09-01
    try:
        parsed_date = datetime.datetime.strptime(value, '%Y-%m-%d')
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
