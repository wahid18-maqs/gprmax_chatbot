import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
import os
import uuid
from utils.query_utils import load_db, query_chatbot
from utils.db_utils import add_data_to_db, data_to_db, add_uploaded_files_to_db, uploaded_files_to_db
from utils.streamlit_utils import cleanup_uploaded_files, db_error_check, print_bertscores, generate_qna_streamlit, rescan_projects, write_uploaded_files_to_disk
from utils.evaluation_utils import evaluate_bertscore
import uuid


# read in available projects once
if "available_projects" not in st.session_state:
    rescan_projects(st.session_state)
    


st.title("gprMax chatbot")

st.session_state["openai_api_key"] = st.text_input("OpenAI API key here")
os.environ["OPENAI_API_KEY"] = st.session_state["openai_api_key"]

st.divider()


st.header("Query")


st.session_state["query_project"] = "af6c69d5"

st.session_state["query"] = st.text_input("Query here")

if st.button("Go!", key = "8"):
    if st.session_state["openai_api_key"] == "":
        st.error("Please enter an OpenAI API key")
        st.stop()
    elif st.session_state["query_project"] == "":
        st.error("Please enter a project")
        st.stop()
    elif st.session_state["query"] == "":
        st.error("Please enter a query")
        st.stop()
    

    with st.spinner("Running"):

        embedding_function = OpenAIEmbeddings()
        llm = ChatOpenAI(model = "gpt-4o-mini")


        root_dir = f"dbs/{st.session_state["query_project"]}"
        db_dir = f"{root_dir}/db"

        # check if db exists
        if not os.path.exists(root_dir) or not os.path.exists(db_dir):
            st.error(f"Could not find database. Please make sure to download the '`dbs`' directory from GitHub and place it in the root directory")
            st.stop()
            
        answer_path = f"{root_dir}/answers/{str(uuid.uuid4())}.md"
        os.makedirs(f"{root_dir}/answers", exist_ok=True)

        db, docstore = load_db(db_dir, embedding_function)

        try:
            answer, sources = query_chatbot(st.session_state["query"], db, docstore, llm)
        except:
            st.error("Unable to generate answer. Please check OpenAI API key, or try again later")
            st.stop()

        st.header("Answer:")
        st.markdown(answer)

        st.header("Sources:")
        for s in sources:
            st.write(s)
        
