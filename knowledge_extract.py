import pandas as pd
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from tqdm import tqdm
from local_llm_model import get_ans


def generate_qa(name,contents):
    result = []
    qa_dir = f"data/database_dir/{name}/qa"

    for content in tqdm(contents):

        if len(content) < 2:
            continue
        prompt = f"""
You are a document reading expert, you can convert documents to QA form, if the documents are in JSON format, the question is in JSON question, 
the answer is JSON answer. 
Subject headings:{name}
Article content: {content}
Please note that the Q&A content you extract must be highly consistent with the subject headings, and there is no need to output other content, and each Q&A you extract returns a python dictionary format.
the format is as follows:
{{"question":"xxx","answer":"xxx"}}
In English, the extracted Q&A content is:"""

        answers = get_ans(prompt)
        answers = answers.split("\n")

        for answer in answers:
            if len(answer) < 10:
                continue
            try:
                answer = eval(answer)
            except:
                continue
            if "question" not in answer or "answer" not in answer:
                continue
            result.append({
                "question": answer["question"],
                "answer": answer["answer"]
            })
    result_df = pd.DataFrame(result)
    result_df.to_excel(qa_dir + "/qa_result.xlsx", index=False)
    result_df.to_csv(qa_dir + "/qa_result.csv",)
    return result_df


if __name__ == "__main__":
    name = "WebXT_Quality"
    dir = f"data/database_dir/{name}/txt"
    qa_dir = f"data/database_dir/{name}/qa"
    # Load the text
    loader = DirectoryLoader(dir)
    documents = loader.load()
    # Cut the text
    text_spliter = CharacterTextSplitter(chunk_size=1800, chunk_overlap=20)
    split_docs = text_spliter.split_documents(documents)
    contents = [i.page_content for i in split_docs]
    generate_qa(name, contents)

