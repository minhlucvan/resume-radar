# main.py
import streamlit as st

def main():
    
    # display README.md
    with open("README.md", "r") as f:
        st.markdown(f.read())

if __name__ == '__main__':
    main()
