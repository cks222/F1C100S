import pandas as pd

from pypinyin import lazy_pinyin
import pickle
import os
import faiss
from emb_model import MyEmbModel
import jsonlines


def cover_name(name):
    return "_".join(lazy_pinyin(name))


class MyEmbDatabase():
    def __init__(self, emb_dir, qa_df, name):
        global client
        self.name = cover_name(name)
        self.emb_model = MyEmbModel(emb_dir)

        if not os.path.exists(os.path.join(".cache", f"{name}_faiss_index.pkl")):

            index = faiss.IndexFlatL2(self.emb_model.model.get_sentence_embedding_dimension())
            embs = self.emb_model.to_emb(qa_df["question"])
            index.add(embs)

            with open(os.path.join(".cache", f"{name}_faiss_index.pkl"), "wb") as f:
                pickle.dump(index, f)
            with open(os.path.join(".cache", f"{name}_faiss_index_df.pkl"), "wb") as f:
                pickle.dump(qa_df, f)
        else:
            with open(os.path.join(".cache", f"{name}_faiss_index.pkl"), "rb") as f:
                index = pickle.load(f)
            with open(os.path.join(".cache", f"{name}_faiss_index_df.pkl"), "rb") as f:
                qa_df = pickle.load(f)
        self.index = index
        self.qa_df = qa_df

    def search(self, content, topn=3):
        global client

        if isinstance(content, str):
            content = self.emb_model.to_emb(content)
        distances , idxs = self.index.search(content,topn) # mlivus
        results = self.qa_df.iloc[ idxs[0]]
        return results

def manually_vectors(name):

    result = []

    txt = f'data/database_dir/{name}/txt/0.txt'
    with open(txt, "r") as f:
        for obj in jsonlines.Reader(f):

            result.append({
                "question": obj["question"],
                "answer": obj["answer"]
            })

    result_df = pd.DataFrame(result)
    print(result_df["question"])
    emb_dir='moka-ai_m3e-base'

    MyEmbDatabase(emb_dir, result_df, name)

if __name__ == "__main__":

    name='WebXT_Quality'
    manually_vectors(name)








