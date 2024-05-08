import streamlit as st
from common import resume_evaluate


# Streamlit app
def main():
    st.title("Resume Evaluation")

    # File upload
    uploaded_file = st.file_uploader("Upload YAML file")
    if uploaded_file is not None:
        # Load JSON file
        data = uploaded_file.read()
        
        evaluation = resume_evaluate.evaluate_resume(data, print=True)
            
        st.write("### Final level: ", evaluation)
        

if __name__ == "__main__":
    main()
