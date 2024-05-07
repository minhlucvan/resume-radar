import streamlit as st
from common import resume_evaluate
from common import resume_extract
import json
import os
import time

# generate a dumb data for the resume
# filename: data/dumnb/{timestamp}.json
def dumb_data(data, pdf_url=""):
    timestamp = int(time.time())
    filename = f"data/dumb/{timestamp}.json"
    
    with open(filename, "w") as f:
        data_json = json.loads(data) if isinstance(data, str) else data
        
        data_json["pdf_url"] = pdf_url
        
        json.dump(data_json, f)

def main():
    st.title("Resume analysis")
    
    # pdf url input
    pdf_url = st.text_input("Enter the URL of the PDF file")
    
    pdf_file = st.file_uploader("Or Upload a PDF file", type="pdf")
    
    # start button
    if st.button("Start analysis"):
        st.write("Analysis started...")
    
        pdf = None
        
        if pdf_file is not None:
            pdf = pdf_file
        
        if pdf_url is not None and pdf_url != "":
            pdf = pdf_url
        
        if pdf is None:
            st.stop()
        
        with st.spinner("Extracting resume data..."):
            data = resume_extract.extract_resume(pdf)
            
            dumb_data(data, pdf_url)
        
        with st.spinner("Evaluating resume..."):
            evaluation = resume_evaluate.evaluate_resume(data)
            
            st.write("### Final level: ", evaluation)
    
    
if __name__ == '__main__':
    main()