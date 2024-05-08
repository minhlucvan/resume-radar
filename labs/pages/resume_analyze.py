import streamlit as st
from common import resume_evaluate
from common import resume_extract
import json
import time
import hashlib

def hash_pdf_url(url):   
    return hashlib.md5(url.encode()).hexdigest()

# generate a dumb data for the resume
# filename: data/dumnb/{timestamp}.json
def dumb_data(data, pdf_url=""):
    timestamp = int(time.time())
    filename = hash_pdf_url(pdf_url) if pdf_url != "" else timestamp
    file_path = f"data/dumb/{filename}.json"
    
    with open(file_path, "w") as f:
        data_json = json.loads(data) if isinstance(data, str) else data
        
        data_json["pdf_url"] = pdf_url
        
        json.dump(data_json, f)

def main():
    st.title("Resume analysis")
        
    # pdf url input
    pdf_url = st.text_input("Enter the URL of the PDF file")
    
    pdf_file = st.file_uploader("Or Upload a PDF file", type="pdf")
    
    is_use_previous = st.checkbox("Use previous data", value=True)
    
    if pdf_url == "" and pdf_file is None:
        st.write("Please enter the URL of the PDF file or upload a PDF file.")
        st.stop()

    pdf = None
    
    if pdf_file is not None:
        pdf = pdf_file
    
    if pdf_url is not None and pdf_url != "":
        pdf = pdf_url
    
    if pdf is None:
        st.stop()
    
    with st.spinner("Extracting resume data..."):
        cached_data = resume_extract.get_cached_data(pdf) if pdf_url != "" and resume_extract.has_cached_data(pdf) else None
        data = resume_extract.extract_resume(pdf) if cached_data is None or not is_use_previous else cached_data
        
        dumb_data(data, pdf_url)
        
    st.markdown(data['data'], unsafe_allow_html=True)
    
    with st.spinner("Evaluating resume..."):
        st.write("# Results")
        evaluation, descriptions = resume_evaluate.evaluate_resume(data)
        
        st.write("### Final level: ", evaluation)
        
        is_show_description = st.checkbox("Show reference", value=False)
        
        if is_show_description:
            st.write(f"#### References")
            for description in descriptions:
                st.write(f"###### {description['name']}")
                st.markdown(description['description'], unsafe_allow_html=True)
                st.text("")
    
    
if __name__ == '__main__':
    main()