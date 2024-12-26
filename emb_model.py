from sentence_transformers import SentenceTransformer


class MyEmbModel():
    def __init__(self, model_dir):

        self.model = SentenceTransformer('moka-ai/m3e-base')
        '''
        self.model = SentenceTransformer(model_dir,local_files_only=True)'''

    def to_emb(self, sentence):
        if isinstance(sentence, str):
            sentence = [sentence]
        return self.model.encode(sentence)


if __name__ == "__main__":
    my_documents = MyEmbModel("moka-ai_m3e-base")
    sent_vec = my_documents.to_emb("What is a large model")
    print("vec dim:", sent_vec[0])