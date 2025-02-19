import os
import json
from src_code.find_similar import SearchClient
from src_code.db_logic import DBLogic
from src_code.emb_model import MyEmbModel


class API:
    def __init__(self):
        RootDIR = os.getcwd()
        self.db = DBLogic(os.path.join(RootDIR, "data", "db"))
        self.sc = SearchClient()
        self.em = MyEmbModel()

    # @app.post("/api/search")
    def search(self, knowledgeid: str, top_k: int, sentence: str):
        emb = self.em.to_emb(sentence)
        data = self.db.get_qas(knowledgeid)
        return self.sc.find_top_n_similar(data, emb[0].tolist(), top_k)

    # @app.get("/api/qas")
    def qas(self, knowledgeid: str):
        data = self.db.get_qas(knowledgeid)
        return [
            {"question": item["q"], "answer": item["a"], "id": item["id"]}
            for item in data
        ]

    # @app.get("/api/knowledges")
    def get_knowledges(
        self,
    ):
        return self.db.get_knowledges()

    # @app.get("/api/add_knowledge")
    def add_knowledge(self, knowledgename: str):
        return self.db.add_knowledge(knowledgename)

    # @app.get("/api/del_knowledge")
    def del_knowledge(self, knowledgeid: str):
        return self.db.del_knowledge(knowledgeid)

    # @app.post("/api/add_qas")
    def add_qas(self, knowledgeid: str, overwrite: bool, qas: str):
        qaes = [
            {"a": qa["a"], "q": qa["q"], "e": self.em.to_emb(qa["q"])[0].tolist()}
            for qa in json.loads(qas)
        ]
        return self.db.add_qas(knowledgeid, qaes, overwrite)

    # @app.post("/api/embedding")
    def p_embedding(self, sentence: str):
        emb = self.em.to_emb(sentence)
        return {"sentence": sentence, "embedding": emb.tolist()}