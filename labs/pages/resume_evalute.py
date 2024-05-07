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
from common import resume_evaluate


# Streamlit app
def main():
    st.title("Resume Features Analysis")

    # File upload
    uploaded_file = st.file_uploader("Upload YAML file")
    if uploaded_file is not None:
        # Load JSON file
        data = uploaded_file.read()
        
        evaluation = resume_evaluate.evaluate_resume(data, print=True)
            
        st.write("### Final level: ", evaluation)
        

if __name__ == "__main__":
    main()
