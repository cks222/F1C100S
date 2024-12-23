import pandas as pd
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
import os
import pickle


class MyDocument():
    def __init__(self, dir, name):

        if not os.path.exists(os.path.join(".cache", f"{name}_contents.pkl")):
            loader = DirectoryLoader(dir)
            documents = loader.load()
            text_spliter = CharacterTextSplitter(chunk_size=1800, chunk_overlap=50)

            split_docs = text_spliter.split_documents(documents)
            contents = [i.page_content for i in split_docs]
            with open(os.path.join(".cache", f"{name}_contents.pkl"), "wb") as f:
                pickle.dump(contents, f)
        else:
            with open(os.path.join(".cache", f"{name}_contents.pkl"), "rb") as f:
                contents = pickle.load(f)


        if os.path.exists(os.path.join(".cache", f"{name}_faiss_index_df.pkl")):
            with open(os.path.join(".cache", f"{name}_faiss_index_df.pkl"), "rb") as f:
                df = pickle.load(f)
        else:
            df = pd.DataFrame({})
        self.qa_df = df
        self.contents = contents

    def get_contents(self):
        return self.contents

    def get_pkls(self):
        return self.qa_df

if __name__ == "__main__":
    topic = 'WebXT_Quality'
    my_documents = MyDocument(f"data/database_dir/{topic}/txt/", topic)
    print("knowledge demo:", my_documents.get_contents())
    print("knowledge num:", len(my_documents.get_contents()))
    print("knowledge num:", len(my_documents.get_pkls()))
    print("knowledge num:", my_documents.get_pkls())
