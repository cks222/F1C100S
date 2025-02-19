import json
import os
import streamlit as st
from datetime import datetime
import streamlit as st
import pandas as pd
import chardet
from langchain.schema import HumanMessage, AIMessage
from src_code.api import API
from st_aggrid import AgGrid, GridOptionsBuilder

a = API()

dfwdith = 1400  # 685

DATA_Server = {
    "currentknowledge": {"id": "", "knowledgename": ""},
    "knowledges": [],
    "qas": {},
}


def InitData():
    global DATA_Server
    DATA_Server["knowledges"] = a.get_knowledges()
    if len(DATA_Server["knowledges"]) > 0:
        DATA_Server["currentknowledge"] = DATA_Server["knowledges"][0]
    for k in DATA_Server["knowledges"]:
        DATA_Server["qas"][k["id"]] = a.qas(k["id"])
    return DATA_Server


def Add_Qas(qas, createk=False, overwirte=False, knowledgename=""):
    # qas={"q":"","a":""}
    global DATA_Server
    ck = DATA_Server["currentknowledge"]
    if createk:
        ck = a.add_knowledge(knowledgename)
        DATA_Server["knowledges"].append(ck)
        DATA_Server["currentknowledge"] = ck
    kid = ck["id"]
    a.add_qas(knowledgeid=kid, qas=json.dumps(qas), overwrite=overwirte)
    DATA_Server["qas"][kid] = a.qas(kid)
    return DATA_Server


def Search(sentence):
    global DATA_Server
    kid = DATA_Server["currentknowledge"]["id"]
    return a.search(kid, 3, sentence)


def upload(file, addNew, overwrite):
    if file is None:
        raise Exception("XXX")
    if not file.name.endswith(".csv"):
        raise Exception("Please upload a folder containing the txt file")

    save_path = os.path.join(
        os.getcwd(), "data/user_uploaded", datetime.now().strftime("%Y-%m-%d")
    )

    if os.path.exists(save_path) == False:
        os.makedirs(save_path)
    filepath = os.path.join(save_path, file.name)
    with open(filepath, "wb") as f:
        content = file.read()
        result = chardet.detect(content)
        encoding = result["encoding"]
        f.write(content)
    df = pd.read_csv(filepath, encoding=encoding)
    qn = df.columns[0]
    an = df.columns[1]
    df.rename(columns={qn: "Q", an: "A"}, inplace=True)
    QAs = df.to_dict(orient="records")
    return Add_Qas(
        [{"q": QA["Q"], "a": QA["A"]} for QA in QAs],
        addNew,
        overwrite,
        file.name[0 : len(file.name) - 4],
    )


def delk(kid):
    return a.del_knowledge(kid)


def optionname(k):
    return k["knowledgename"]


@st.cache_data
def initSession():
    st.session_state.filename = ""
    st.session_state.delkid = ""


def QAView():
    global dfwdith
    st.header("🐬Generate Q&A datasets")
    if True:
        col1, col2 = st.columns([1, 3])
        with col1:
            index = 0
            if len(st.session_state.data["knowledges"]) > 0:
                index = st.session_state.data["knowledges"].index(
                    st.session_state.data["currentknowledge"]
                )
            select_option = st.selectbox(
                "Knowledge base selection",
                st.session_state.data["knowledges"],
                key="id",
                format_func=optionname,
                index=index,
                )
        if select_option:
            st.session_state.data["currentknowledge"] = select_option
        loadqas = (
            []
            if st.session_state.data["currentknowledge"]["id"] == ""
            else st.session_state.data["qas"][
                st.session_state.data["currentknowledge"]["id"]
            ]
        )
        df = pd.DataFrame(
            loadqas,
            columns=["question", "answer"],
        )

        options_builder = GridOptionsBuilder.from_dataframe(df)
        options_builder.configure_default_column(
            wrapText=True,
            autoHeight=True,
            cellStyle={"white-space": "pre-wrap"},
        )
        options_builder.configure_column(
            "question",
            maxWidth=dfwdith / 3,
        )
        options_builder.configure_column(
            "answer",
            maxWidth=dfwdith / 3 * 2,
        )
        options_builder.configure_grid_options(
            theme="blue", enable_pagination=True, paginationAutoPageSize=True
        )
        grid_options = options_builder.build()
        AgGrid(
            df,
            grid_options,
        )
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        with st.popover("➕︎"):
            Add_Str = "Add New Knowledge"
            Overwrite_Str = "Overwrite Current Knowledge"
            option = Add_Str
            if "filename" not in st.session_state:
                st.session_state.filename = ""
            file = st.file_uploader(
                "upload a knowledge base", accept_multiple_files=False
            )
            if file:
                if st.session_state.filename != file.name:
                    st.session_state.filename = file.name
                    upload(file, option == Add_Str, Overwrite_Str == option)
                    st.rerun()

    with c2:
        if "delkid" not in st.session_state:
            st.session_state.delkid = ""
        if st.session_state.data["currentknowledge"]["id"] != "":
            with st.popover("🗑️"):
                st.write(
                    "do you want to remove the Knowledge: "
                    + st.session_state.data["currentknowledge"]["knowledgename"]
                )
                s = st.button("Yes")
                if s:
                    st.session_state.delkid = st.session_state.data["currentknowledge"][
                        "id"
                    ]
                    delk(st.session_state.delkid)
                    st.rerun()


def Chat():
    col1, col2 = st.columns([1, 3])
    with col1:
        index = 0
        if len(st.session_state.data["knowledges"]) > 0:
            index = st.session_state.data["knowledges"].index(
                st.session_state.data["currentknowledge"]
            )
        input_qa = st.selectbox(
            "Knowledge base selection",
            st.session_state.data["knowledges"],
            key="id",
            format_func=optionname,
            index=index,
        )
        st.session_state.data["currentknowledge"] = input_qa

    st.title("🐳Welcome to the QA page")

    prompt = st.chat_input("Please input the question")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    tag="\t-,-\t"
    with st.container():
        for message in st.session_state["messages"]:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):

                with st.chat_message("assistant"):
                    data = []
                    mess = message.content.strip().split("\n\n")
                    for i in mess:
                        data2 = {
                            "question": i.split(tag)[0],
                            "answer": i.split(tag)[1],
                        }
                        data.append(data2)
                    df = pd.DataFrame(data, columns=["question", "answer"])

                    st.table(df)
        if prompt:
            st.session_state["messages"].append(HumanMessage(content=prompt))
            with st.chat_message("user"):
                st.markdown(prompt)

            rag_result = Search(prompt)

            temp = ""
            if len(rag_result) == 0:
                temp = tag
            for i in rag_result:
                temp += i["question"] + tag + i["answer"] + "\n\n"

            st.session_state["messages"].append(AIMessage(content=temp))
            with st.chat_message("assistant"):
                df = pd.DataFrame(rag_result, columns=["question", "answer"])
                st.table(df)
                s = '''
                placeholder = st.empty()
                response = OpenAI(
                    base_url="https://ms-fc-55f208be-e444.api-inference.modelscope.cn/v1",
                    # base_url="https://ms-fc-130c6638-b97b.api-inference.modelscope.cn/v1",
                    api_key="a827ca8d-8be4-4d31-b856-76c5a9f5073f",
                ).chat.completions.create(
                    model="unsloth/DeepSeek-R1-Distill-Qwen-1.5B-GGUF",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )
                aswr = ""
                isaswr = False
                for chunk in response:
                    if isaswr:
                        aswr += chunk.choices[0].delta.content
                        placeholder.text(aswr)
                    if chunk.choices[0].delta.content == "</think>":
                        isaswr = True
                    print(chunk.choices[0].delta.content)
                '''

if __name__ == "__main__":
    st.set_page_config(
        page_title="WebXT Chatbot",
        page_icon="💬",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None,
    )

    st.session_state.data = InitData()
    initSession()
    pg = st.navigation(
        [
            st.Page(QAView, title="🐬Q&A View"),
            st.Page(Chat, title="🐳 Knowledge Base Q&A"),
        ]
    )

    pg.run()
