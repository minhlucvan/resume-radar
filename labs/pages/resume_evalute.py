import streamlit as st
from common import resume_evaluate
from common import resume_extract


# Streamlit app
def main():
    st.title("Resume Evaluation")

    # File upload
    uploaded_file = st.file_uploader("Upload YAML file")
    if uploaded_file is not None:
        # Load JSON file
        data = uploaded_file.read()
        
        data = resume_extract.load_data(data)
        
        # st.markdown(data['data'], unsafe_allow_html=True)
        
        st.write("# Results")
        
        evaluation, descriptions = resume_evaluate.evaluate_resume(data, print=True)
        
        st.write("### Final level: ", evaluation)
        
        is_show_description = st.checkbox("Show reference", value=False)
        
        if is_show_description:
            st.write(f"#### References")
            for description in descriptions:
                st.write(f"###### {description['name']}")
                st.markdown(description['description'], unsafe_allow_html=True)
                st.text("")
                

if __name__ == "__main__":
    main()
