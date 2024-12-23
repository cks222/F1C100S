
import pickle

def look_content(topic_name):
    # Replace 'file_path.pkl' with your file path
    file_path = f".cache/{topic_name}_contents.pkl"

    # Open the file in binary read mode
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    # Print or inspect the loaded data
    print(data)

def look_faiss_db(topic_name):
    # Replace 'file_path.pkl' with your file path
    file_path = f".cache/{topic_name}_faiss_index_df.pkl"

    # Open the file in binary read mode
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    # Print or inspect the loaded data
    print(data)

def look_faiss_index_db(topic_name):
    # Replace 'file_path.pkl' with your file path
    file_path = f".cache/{topic_name}_faiss_index.pkl"

    # Open the file in binary read mode
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    # Print or inspect the loaded data
    print(data)

if __name__ == "__main__":

    topic_name = 'WebXT_Quality'
    # look_content(topic_name)

    look_faiss_db(topic_name)
    look_faiss_index_db(topic_name)
