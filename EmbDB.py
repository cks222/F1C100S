from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from typing import List
from database import load_database, MyEmbDatabase
from emb_model import MyEmbModel
from datetime import datetime
import hashlib


class MyMilvusData:
    def __init__(self, vector: List[float], question: str, answer: str):
        self.id = hashlib.sha256(question.encode("utf-8")).hexdigest()
        self.vector = vector
        self.question = question
        self.answer = answer
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


class MyMilvusClient:
    def __init__(self, host: str = "localhost", port: str = "19530"):
        self.host = host
        self.port = port
        connections.connect("default", host=self.host, port=self.port)

    def _create_collection(
        self, collection_name: str, dim: int, idlength: int, timesteplength: int
    ) -> Collection:
        fields = [
            FieldSchema(
                name="id", is_primary=True, dtype=DataType.VARCHAR, max_length=idlength
            ),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dim),
            FieldSchema(name="question", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="answer", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(
                name="timestamp", dtype=DataType.VARCHAR, max_length=timesteplength
            ),
        ]
        schema = CollectionSchema(fields, collection_name)
        collection = Collection(collection_name, schema)
        index_param = {"index_type": "FLAT", "metric_type": "L2", "params": {}}
        collection.create_index("vector", index_param)
        collection.load()
        return collection

    def insert_data(self, collection_name: str, data: List[MyMilvusData]) -> None:
        self._create_collection(collection_name, len(data[0].vector), len(data[0].id), len(data[0].timestamp))
        collection = Collection(collection_name)
        data = self.filter_data_existence(collection_name, data)
        if len(data) == 0:
            return
        ist_data = [
            [getattr(d, field) for d in data]
            for field in ["id", "vector", "question", "answer", "timestamp"]
        ]
        collection.insert(ist_data)
        collection.load()

    def search_similar(
        self, collection_name: str, vector: List[float], top_k: int = 3
    ) -> List:
        collection = Collection(collection_name)
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            [vector],
            "vector",
            search_params,
            output_fields=["vector", "question", "answer"],
            limit=top_k,
        )
        return results

    def _delete_collection(self, collection_name: str) -> None:
        try:
            collection = Collection(collection_name)
            collection.drop()
        except:
            print("can't drop")

    def get_all_data_paginated(
        self, collection_name: str, page_number: int = 1, page_size: int = 100,output_fields=["vector", "question", "answer"]
    ):
        collection = Collection(collection_name)
        offset = (page_number - 1) * page_size
        results = collection.query(expr='timestamp like"%:%"', offset=offset, limit=page_size,output_fields=output_fields)
        return results

    def filter_data_existence(self, collection_name: str, data: List[MyMilvusData]) -> List[int]:
        page_number=1
        newids = set([d.id for d in data])
        while True: 
            results = self.get_all_data_paginated(collection_name,page_number=page_number,  output_fields=["id"]) 
            if not results : 
                break 
            dbids=set([result["id"] for result in results])
            newids=newids-dbids
            if len(newids)==0:
                return []
            
            page_number=page_number+1
        new_arr = [item for item in data if item.id in newids]
        return new_arr

if __name__ == "__main__":
    database_list, database_namelist = load_database()
    emb_model = MyEmbModel("moka-ai_m3e-base")
    mdb = MyMilvusClient()

    data = []
    for name in database_namelist:
        db = MyEmbDatabase("moka-ai_m3e-base", None, name)
        mdb._delete_collection(name)
        for i in range(len(db.qa_df)):
            qa = db.qa_df.values[i]
            q = qa[0]
            a = qa[1]
            e = emb_model.to_emb(q)[0]
            data.append(MyMilvusData(e, q, a))
        mdb.insert_data(name, data)
