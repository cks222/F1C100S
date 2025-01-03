import streamlit as st

import os
import shutil
import jieba.analyse as aly
from collections import Counter
from database import MyDataBase
import pandas as pd
import random
from database import load_database
from local_llm_model import get_ans
from knowledge_extract import generate_qa
from st_aggrid import AgGrid, DataReturnMode, GridUpdateMode, GridOptionsBuilder
from langchain.schema import SystemMessage, HumanMessage, AIMessage


dfwdith = 1400 #685

def get_type_name(files):
    content = []
    for file in files:
        try:
            with open(file.name, encoding="utf-8") as f:
                data = f.readlines(1)
                content.extend(aly.tfidf(data[0]))
        except:
            continue
    count = Counter(content)
    kw = count.most_common(2)

    return "".join([i[0] for i in kw])


def upload(files):
    global database_list, database_namelist, input_qa

    check_txt = False

    for file in files:
        if check_txt:
            break
        if file.name.endswith(".txt"):
            check_txt = True
    else:
        if check_txt == False:
            raise Exception("Please upload a folder containing the txt file")

    type_name = get_type_name(files)
    save_path = os.path.join("data/database_dir", type_name)

    if os.path.exists(save_path) == False:
        os.mkdir(save_path)
        os.mkdir(os.path.join(save_path, "txt"))
    for file in files:
        if file.name.endswith(".txt"):
            shutil.copy(file.name, os.path.join(save_path, "txt"))

    database = MyDataBase(save_path, type_name)
    database_list.append(database)
    database_namelist.append(type_name)
    knowledge_names.choices.append((type_name, type_name))
    input_qa.choices.append((type_name, type_name))
    context = pd.DataFrame(database.document.contents, columns=["context"])
    return type_name, context


def database_change(name):
    global database_list, database_namelist
    context = pd.DataFrame(
        database_list[database_namelist.index(name)].document.contents,
        columns=["question"],
    )
    return context

def generate_rag_result(knowledge_name, question):
    # Call your data generation function here
    database = database_list[database_namelist.index(knowledge_name)]
    # search_result = database.search(question, 3)
    search_result = database.search(question, 1)
    result = search_result.values[0][0]+"\n"+search_result.values[0][1]
    return result

def process_qa_data(input_qa):
    global database_list, database_namelist
    select_database = database_list[database_namelist.index(input_qa)]
    contexts = select_database.document.contents
    qa_df = generate_qa(input_qa, contexts)
    select_database.create_emb_database(qa_df)
    return qa_df


def page1():
    global dfwdith
    st.header("📚Knowledge Base Management")    
    col1, col2 = st.columns([1, 3])
    with col1:
        knowledge_names = st.selectbox("Knowledge base selection", database_namelist)
    if "current_context" not in st.session_state:
     
        df = pd.DataFrame(database_list[0].document.contents, columns=["context"])
        options_builder = GridOptionsBuilder.from_dataframe(df)
        options_builder.configure_default_column(
            groupable=True,
            value=True,
            enableRowGroup=True,
            aggFunc="sum",
            editable=True,
            wrapText=True,
            autoHeight=True,
            cellStyle={"white-space": "pre-wrap"},
        )
        options_builder.configure_column(
            "context",
            maxWidth=dfwdith,
        )

        grid_options = options_builder.build()
        AgGrid(
            df,
            grid_options,
        )

    uploaded_files = st.file_uploader(
        "Upload a knowledge base", accept_multiple_files=True
    )
    if uploaded_files:
        upload(uploaded_files)
    if st.button("Change Database"):
        database_change(knowledge_names)


def page2():
    global dfwdith
    st.header("☯Generate Q&A datasets")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        input_qa = st.selectbox(
            "Knowledge base selection", database_namelist, key="qa_dataset_select"
        )
    if "qa_output" not in st.session_state:
        # st.session_state['qa_output'] = pd.DataFrame(database_list[0].document.qa_df, columns=["question", "answer"])
        pass
    df = pd.DataFrame(database_list[0].document.qa_df, columns=["question", "answer"])

    options_builder = GridOptionsBuilder.from_dataframe(df)
    options_builder.configure_default_column(
        wrapText=True,
        autoHeight=True,
        cellStyle={"white-space": "pre-wrap"},
    )
    options_builder.configure_column(
        "question",
        maxWidth=dfwdith/3,
    )
    options_builder.configure_column(
        "answer",
        maxWidth=dfwdith/3*2,
    )
    options_builder.configure_grid_options(
        theme="blue", enable_pagination=True, paginationAutoPageSize=True
    )
    grid_options = options_builder.build()
    AgGrid(
        df,
        grid_options,
    )

    # st.dataframe(st.session_state['qa_output'], width=2000, height= 1600)
    # st.dataframe(st.session_state['qa_output'], use_container_width = True)
    if st.button("Generate Q&A datasets"):
        st.session_state["qa_output"] = process_qa_data(input_qa)


def page3():
    col1, col2 = st.columns([1, 3])
    with col1:
        input_qa = st.selectbox(
            "Knowledge Base Q&A", database_namelist, key="qa_rag_select"
        )

    st.title("🦜 Welcome to the QA page")

    prompt = st.chat_input("Please input the question")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    with st.container():
        st.header(" 🎈  Search results for the question")

        for message in st.session_state["messages"]:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)

        if prompt:
            st.session_state["messages"].append(HumanMessage(content=prompt))
            with st.chat_message("user"):
                st.markdown(prompt)

            rag_result = generate_rag_result(input_qa, prompt)
            #st.text_area("LLM generated answers", rag_result)

            st.session_state["messages"].append(AIMessage(content=rag_result))
            with st.chat_message("assistant"):
                st.markdown(rag_result)

    # if st.button("Generate answers"):
    #     text_output, rag_result = generate_rag_result(input_qa, prompt)
    #     st.text_area("LLM generated answers", text_output)
    #     st.session_state['rag_results'] = rag_result


if __name__ == "__main__":
    st.set_page_config(
        page_title="WebXT Chatbot",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None
    )

    database_list, database_namelist = load_database()

    pg = st.navigation(
        [
            st.Page(page1, title="📚Knowledge Base Management"),
            st.Page(page2, title="☯Generate Q&A datasets"),
            st.Page(page3, title="🦜Knowledge Base Q&A"),
        ]
    )

    pg.run()

    for i in database_list:
        print(i.document.contents)
        print(i.document.qa_df)

    df = pd.DataFrame(database_list[0].document.qa_df, columns=["question", "answer"])

    print(df)
