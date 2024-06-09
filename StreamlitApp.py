import os 
import json
import pandas as pd
import traceback
import streamlit as st
from dotenv import load_dotenv
from langchain_community.callbacks.manager import get_openai_callback
from src.MCQGenerator.utils import read_file, get_table
from src.MCQGenerator.logger import logging
from src.MCQGenerator.MCQGenerator import combined_chain

with open(r"C:\Users\makin\Desktop\My workspace\GENAI\Response.json", 'r') as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQ Creator Application")

with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF file")
    mcq_count = st.number_input("No of MCQs", min_value=3, max_value=30)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity Level of the questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text = read_file(uploaded_file)
                with get_openai_callback() as cb:
                    response = combined_chain(
                        {
                            "text": text,
                            "number": mcq_count,
                            "subject": subject,
                            "tone": tone,
                            "response_json": json.dumps(RESPONSE_JSON)
                        }
                    )
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("ERROR")
            
            else:
                print(f"Total Tokens: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost: {cb.total_cost}")
                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    # print(type(quiz))
                    if quiz is not None:
                        # quiz = json.loads(quiz)
                        # print(type(quiz))
                        table_data = get_table(quiz)
                        print(type(table_data))
                        print(table_data)
                        if table_data is not None:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            st.text_area(label="Review", value=response["review"])
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response)