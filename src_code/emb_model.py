'''
from sentence_transformers import SentenceTransformer
import os
import sys


class MyEmbModel():
    def __init__(self):
        self.model = SentenceTransformer(self.get_path("./model/m3e-base"),local_files_only=True)

    def to_emb(self, sentence):
        if isinstance(sentence, str):
            sentence = [sentence]
        return self.model.encode(sentence)
    def get_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
'''
import requests
import json    
import numpy as np
class MyEmbModel():
    def __init__(self):
        pass
    def to_emb(self,sentence:str):
        data={"sentence":sentence}
        response = requests.post("http://39.106.90.31:1440/api/embedding",data)
        elist = json.loads(response.text)["embedding"]
        emd = np.array(elist)
        return emd



if __name__ == "__main__":
    my_documents = MyEmbModel("moka-ai_m3e-base")
    sent_vec = my_documents.to_emb("What is a large model")
    print("vec dim:", sent_vec[0])