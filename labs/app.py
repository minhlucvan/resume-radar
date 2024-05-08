# main.py
import streamlit as st

def main():
    # set page name
    st.set_page_config(page_title="Resume Analysis", page_icon=":memo:")
        
    # display README.md
    with open("README.md", "r") as f:
        st.markdown(f.read())

if __name__ == '__main__':
    main()
