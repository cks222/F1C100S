import os
import gradio as gr
import shutil
import jieba.analyse as aly
from collections import Counter
from database import MyDataBase
import pandas as pd
import random
from database import load_database
from local_llm_model import get_ans
from knowledge_extract import generate_qa


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
    context = pd.DataFrame(database_list[database_namelist.index(name)].document.contents, columns=["question"])
    return context


def generate_rag_result(knowledge_name, question):
    # Call your data generation function here
    database = database_list[database_namelist.index(knowledge_name)]
    search_result = database.search(question, 3)
    abstract = "\n".join(search_result["answer"])
    prompt = f'''
Please respond to the user's question succinctly and concisely based on what you already know, which is as follows:
 {abstract},
 The user's question is:{question},
 How do you know that the content can't answer the user's question, please reply directly: I don't know, no other content is needed.
'''
    result = get_ans(prompt)
    return result, search_result


def process_qa_data(input_qa):
    global database_list, database_namelist
    select_database = database_list[database_namelist.index(input_qa)]
    contexts = select_database.document.contents
    qa_df = generate_qa(input_qa, contexts)
    select_database.create_emb_database(qa_df)
    return qa_df


if __name__ == "__main__":
    database_list, database_namelist = load_database()
    print("data................")

    authorized_users = [("admin", "123456"), ("monica", "pass456")]

    with gr.Blocks(css=".dataframe-cell { white-space: normal; word-wrap: break-word; }") as glass:


        with gr.Tab("Knowledge base management"):
            knowledge_names = gr.Dropdown(choices=database_namelist, label="Knowledge base selection", value=database_namelist[0])
            context = gr.DataFrame(pd.DataFrame(database_list[0].document.contents, columns=["context"]), max_height=800)
            input3 = gr.UploadButton(label="Upload a knowledge base", file_count="directory")
            input3.upload(upload, input3, [knowledge_names, context])
            knowledge_names.change(database_change, knowledge_names, context)

        with gr.Tab("Generate Q&A datasets"):
            input_qa = gr.Dropdown(choices=database_namelist, label="Knowledge base selection", value=database_namelist[0])
            output_data = gr.DataFrame(database_list[0].document.qa_df, max_height=400)
            generate_data_button = gr.Button("Generate Q&A datasets")
            generate_data_button.click(process_qa_data, [input_qa], [output_data])


        with gr.Tab("Knowledge Base Q&A"):
            input_qa = gr.Dropdown(choices=database_namelist, label="Knowledge Base Q&A", value=database_namelist[0])
            text_input = gr.Textbox(label="Please output the question")
            text_rag = gr.DataFrame(pd.DataFrame(), max_height=500, label="RAG results")
            text_output = gr.Textbox(label="LLM generate answers")
            qa_button = gr.Button("generate answers")
            qa_button.click(generate_rag_result, [input_qa, text_input], [text_output, text_rag])

    glass.launch(server_name="0.0.0.0", share=False, server_port=9999, show_api=False, auth=authorized_users)
