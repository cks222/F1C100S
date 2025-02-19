from typing import List
import numpy as np


class SearchClient:
    def search_similar(self, vector: List[float], alldata, top_k: int = 3) -> List:
        if len(alldata) == 0:
            return []
        return self.find_top_n_similar(alldata, vector, top_k)

    def cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        return dot_product / (norm_vec1 * norm_vec2)

    def find_top_n_similar(self, data, search_vector, n=3):
        similarities = [] 
        for item in data:
            similarity = self.cosine_similarity(
                np.array(item["e"]), np.array(search_vector)
            )
            similarities.append(
                (similarity, {"question": item["q"], "answer": item["a"]})
            )
        similarities.sort(key=lambda x: x[0], reverse=True)

        top_n = similarities[:n]

        return [
            {"question": item[1]["question"], "answer": item[1]["answer"]}
            for item in top_n
        ]
