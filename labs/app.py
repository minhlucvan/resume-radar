# main.py
import streamlit as st
import os

def main():
    # set page name
    st.set_page_config(page_title="Resume Analysis", page_icon=":memo:")
    
    # related to the __dirname
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    
    # display README.md
    with open(readme_path, "r") as f:
        st.markdown(f.read())

if __name__ == '__main__':
    main()
