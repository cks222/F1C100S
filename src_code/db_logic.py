import uuid
import os
import threading
import json
import copy


class MyCollection:
    def __init__(self, dir, name: str):
        self.lock = threading.Lock()
        self.Path = os.path.join(dir, name + ".json")
        if not os.path.exists(dir):
            os.makedirs(dir)
        if not os.path.exists(self.Path):
            self._save([])

    def select_all(self):
        return self._read()
    
    def remove_all(self):
        self._save([])
        return []
    
    def drop(self):
        with self.lock:
            os.remove(self.Path)

    def delete_one(self, query):
        data = self._read()
        removeIds=[item["id"] for item in self._filter(data, query)]
        if len(removeIds)==0:
            return ""
        rid=removeIds[0]
        leftdata = [item for item in data if item["id"] != rid ]        
        self._save(leftdata)

    def delete_many(self, query):
        data = self._read()
        removeIds=[item["id"] for item in self._filter(data, query)]
        if len(removeIds)==0:
            return 
        leftdata = [item for item in data if item["id"] not in removeIds ]        
        self._save(leftdata)

    def insert_one(self, data):
        self.insert_many([data])

    def insert_many(self, data):
        ad = []
        for d in data:
            dbd = copy.deepcopy(d)
            dbd["id"] = str(uuid.uuid4())
            ad.append(dbd)
        alldata = self._read()
        alldata.extend(ad)
        self._save(alldata)

    def find_one(self, query):
        result = self.find(query)
        return result[0] if len(result) > 0 else None

    def find(self, query):
        data = self._read()
        return self._filter(data, query)

    def update_one(self, query, change):
        data = self.find_one(query)
        self._update_many([data], change)

    def update_many(self, query, change):
        data = self.find(query)
        self._update_many(data, change)

    def _update_many(self, data, change):
        if len(data) == 0:
            return
        for key, value in change["$set"].items():
            keys = key.split(".")
            for dd in data:
                d = dd
                for k in keys[:-1]:
                    d = d[k]
                d[keys[-1]] = value

        existids = [d["id"] for d in data]
        alldata = [d for d in self._read() if d["id"] not in existids]
        alldata.extend(data)
        self._save(alldata)

    def _and_filter(self, data, andarry):
        ids = set(item["id"] for item in data)
        for query in andarry:
            ids2 = set(item["id"] for item in self._filter(data, query))
            ids = ids & ids2
        return [item for item in data if item["id"] in ids]

    def _or_filter(self, data, orarry):
        combined_dict = {}
        for query in orarry:
            combined_dict.update(
                {item["id"]: item for item in self._filter(data, query)}
            )
        return list(combined_dict.values())

    def _filter(self, data, query):
        result = []
        for q in query.keys():
            if q == "$and":
                result = self._and_filter(data, query[q])
            elif q == "$or":
                result = self._or_filter(data, query[q])
            elif q == "$in":
                key, value = list(query.items())[0]
                keys = key.split(".")
                result = list(
                    filter(
                        lambda item: self._get_nested_value(item, keys) in value, data
                    )
                )
            else:
                key, value = list(query.items())[0]
                keys = key.split(".")
                if isinstance(value, dict):
                    result = list(
                        filter(
                            lambda item: self._get_nested_value(item, keys)
                            in value["$in"],
                            data,
                        )
                    )
                else:
                    result = list(
                        filter(
                            lambda item: self._get_nested_value(item, keys) == value,
                            data,
                        )
                    )
        return result

    def _get_nested_value(self, item, keys):
        for key in keys:
            item = item.get(key, None)
            if item is None:
                return None
        return item

    def _read(self):
        with self.lock:
            with open(self.Path, "r") as file:
                data = json.load(file)
        return data

    def _save(self, data):
        with self.lock:
            with open(self.Path, "w") as file:
                json.dump(data, file)


class DBLogic:
    def __init__(self, DbDir: str):
        self.host = DbDir
        self.Knowledgecollection = self.get_col("Knowledge")

    def get_col(self, collection_name: str):
        return MyCollection(self.host, collection_name)

    def getGuid(self):
        return str(uuid.uuid4())

    def add_knowledge(self, knowledgename: str):
        kid = self.getGuid()
        data = {
            "id": kid,
            "knowledgename": knowledgename,
        }
        self.Knowledgecollection.insert_one({"data": data})
        return data
    
    def del_knowledge(self, knowledgeid: str):
        self.Knowledgecollection.delete_one({"data.id": knowledgeid})
        self.get_col(knowledgeid).drop()

    def get_knowledges(self):
        data = self.Knowledgecollection.select_all()
        result = [d["data"] for d in data]
        return result

    def add_qas(self, knowledgeid: str, qas: list[dict],overwrite:bool):
        data = []
        for qa in qas:
            data.append(
                {
                    "data": {
                        "id": self.getGuid(),
                        "q": qa["q"],
                        "a": qa["a"],
                        "e": qa["e"],
                    }
                }
            )
        if overwrite:
            self.get_col(knowledgeid).remove_all()
        self.get_col(knowledgeid).insert_many(data)

    def get_qas(self, knowledgeid: str):
        data = self.get_col(knowledgeid).select_all()
        return [d["data"] for d in data]
